from litestar.config.app import AppConfig
from litestar.di import Provide
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.plugins.prometheus import PrometheusController
from litestar.plugins.sqlalchemy import base
from litestar.stores.redis import RedisStore
from redis.asyncio import ConnectionPool, Redis, RedisError
from redis.commands.core import AsyncScript
from sqlalchemy import select

from app.config import conf
from app.data import operator_ids, operators_id_dict
from app.db.model import OperatorsVoteRecords, sqlalchemy_config

_redis_pool: ConnectionPool | None = None
_redis_instance: Redis | None = None
_redis_script: AsyncScript | None = None
lua_script = """
local ballot_code = ARGV[1]
local timestamp = ARGV[2]
local data = ARGV[3]
local win_id = tonumber(ARGV[4])
local lose_id = tonumber(ARGV[5])
local multiplier = tonumber(ARGV[6])

redis.call("HSET", "req:" .. ballot_code, "timestamp", timestamp, "data", data)

redis.call("ZADD", "req_index:by_time", timestamp, ballot_code)
redis.call("SADD", "req_index:by_operator:win:" .. win_id, ballot_code)
redis.call("SADD", "req_index:by_operator:lose:" .. lose_id, ballot_code)

redis.call("INCRBY", win_id..":win", multiplier)
redis.call("INCRBY", lose_id..":lose", multiplier)
redis.call("INCRBY", "op_matrix:"..win_id..":"..lose_id, multiplier)
redis.call("DECRBY", "op_matrix:"..lose_id..":"..win_id, multiplier)

return 1
"""


def setup_redis_pool() -> ConnectionPool:
    global _redis_pool  # noqa: PLW0603
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            conf.redis.redis_url,
            max_connections=200,
            socket_connect_timeout=5,
            socket_keepalive=True,
            decode_responses=True,
        )
    return _redis_pool


async def redis_provider() -> Redis:
    global _redis_instance  # noqa: PLW0603
    global _redis_script  # noqa: PLW0603
    if _redis_instance is None:
        pool = setup_redis_pool()
        _redis_instance = Redis(connection_pool=pool)

    try:
        if not await _redis_instance.ping():
            raise ConnectionError("Redis ping failed")
    except (ConnectionError, RedisError):
        _redis_instance = Redis(connection_pool=setup_redis_pool())

    if _redis_script is None:
        _redis_script = _redis_instance.register_script(lua_script)

    return _redis_instance


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    __slots__ = ("app_slug", "redis")
    redis: Redis
    app_slug: str

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        from advanced_alchemy.exceptions import RepositoryError

        from app.__about__ import __version__ as current_version
        from app.config import app as app_conf
        from app.domain import root_handler
        from app.lib.exceptions import ApplicationError, exception_to_http_response
        from app.server import plugins

        self.redis = conf.redis.get_client()
        self.app_slug = conf.app.slug
        app_config.debug = conf.app.debug
        # openapi
        app_config.openapi_config = OpenAPIConfig(
            title=conf.app.name,
            version=current_version,
            use_handler_docstrings=True,
            render_plugins=[ScalarRenderPlugin(version="latest")],
        )
        # security
        app_config.cors_config = app_conf.cors
        # static files
        app_config.static_files_config.append(app_conf.static_files)
        # templates
        app_config.template_config = app_conf.templates
        # plugins
        app_config.plugins.extend(
            [
                plugins.structlog,
                plugins.granian,
                plugins.saq,
                plugins.problem_details,
                plugins.sqlalchemy_plugin,
            ],
        )
        # compression
        # app_config.compression_config = app_conf.compression  # noqa: ERA001
        # middleware
        app_config.middleware.extend([app_conf.rate_limit.middleware, app_conf.prometheus_config.middleware])

        # routes
        app_config.route_handlers.extend(root_handler)
        app_config.route_handlers.append(PrometheusController)
        # exception handling
        app_config.exception_handlers = {
            ApplicationError: exception_to_http_response,
            RepositoryError: exception_to_http_response,
        }
        app_config.stores = {
            "ballot": RedisStore(self.redis, "ballot"),
        }

        # dependencies
        dependencies = {"redis": Provide(redis_provider, use_cache=True)}
        app_config.dependencies.update(dependencies)

        app_config.on_startup.append(on_startup)  # type: ignore[attr-defined]
        app_config.on_shutdown.append([on_shutdown, self.redis.aclose])  # type: ignore[attr-defined]
        return app_config


async def on_startup() -> None:
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(base.DefaultBase.metadata.create_all)

    async with sqlalchemy_config.get_session() as session:
        result = (await session.stream(select(OperatorsVoteRecords))).scalars()
        records = {r.operator_id: r async for r in result}
        for oid in operators_id_dict.values():
            if oid not in records:
                session.add(
                    OperatorsVoteRecords(
                        operator_id=oid,
                        score_win=0,
                        score_lose=0,
                    )
                )
        await session.commit()
        await session.flush()

    # add to redis
    redis = conf.redis.get_client()
    pipeline = redis.pipeline()
    for oid in operators_id_dict.values():
        pipeline.exists(f"{oid}:win")
        pipeline.exists(f"{oid}:lose")
    exists_results = await pipeline.execute()

    pipeline = redis.pipeline()
    for idx, oid in enumerate(operators_id_dict.values()):
        if not exists_results[idx * 2]:
            pipeline.set(f"{oid}:win", 0)
        if not exists_results[idx * 2 + 1]:
            pipeline.set(f"{oid}:lose", 0)
    await pipeline.execute()
    pipeline = redis.pipeline()
    all_op_matrix_keys = [f"op_matrix:{i}:{j}" for i in operators_id_dict.values() for j in operators_id_dict.values()]
    for key_op in all_op_matrix_keys:
        pipeline.setnx(key_op, 0)
    pipeline.setnx("op_matrix", str([[0] * len(operator_ids) for _ in operator_ids]))
    await pipeline.execute()


async def on_shutdown() -> None:
    if _redis_instance:
        await _redis_instance.close()
    if _redis_pool:
        await _redis_pool.disconnect()
