from litestar.config.app import AppConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.plugins.sqlalchemy import base
from litestar.stores.redis import RedisStore
from redis.asyncio import Redis
from sqlalchemy import select

from app.data import operators_id_dict
from app.db.model import OperatorsVoteRecords, sqlalchemy_config
from app.lib.cache import record_cache, save_batch


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    __slots__ = ("app_slug", "redis")
    redis: Redis
    app_slug: str

    def on_app_init(self, app_config: AppConfig) -> AppConfig:

        from advanced_alchemy.exceptions import RepositoryError

        from app.__about__ import __version__ as current_version
        from app.config import app as app_conf
        from app.config import conf
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
        app_config.compression_config = app_conf.compression
        # middleware
        app_config.middleware.append(app_conf.rate_limit.middleware)

        # routes
        app_config.route_handlers.extend(root_handler)
        # exception handling
        app_config.exception_handlers = {
            ApplicationError: exception_to_http_response,
            RepositoryError: exception_to_http_response,
        }
        app_config.stores = {
            "ballot": self.redis_store_factory("ballot"),
            "ip_mul_limiter": self.redis_store_factory("ip_mul_limiter"),
        }
        app_config.on_startup.append(on_startup)
        app_config.on_shutdown.append([on_shutdown, self.redis.aclose])  # type: ignore[attr-defined]
        return app_config

    def redis_store_factory(self, name: str) -> RedisStore:
        return RedisStore(self.redis, namespace=f"{self.app_slug}:{name}")

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


async def on_shutdown() -> None:
    async with sqlalchemy_config.get_session() as session:
        batch = await record_cache.swap_batches()
        await save_batch(session, batch)
