from app.cache import record_cache, save_batch
from app.config import conf
from app.data import operators_id_dict
from app.domain import root_handler
from app.model import OperatorsVoteRecords, sqlalchemy_config

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin, base
from litestar.static_files.config import StaticFilesConfig
from litestar.stores.redis import RedisStore
from litestar.template.config import TemplateConfig
from sqlalchemy import select

root_store = RedisStore.with_client(url=conf.redis.redis_url, db=conf.redis.redis_db)
rate_limit_config = RateLimitConfig(
    rate_limit=(
        conf.rate_limit.rate_limit_period,
        conf.rate_limit.rate_limit,
    )
)


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


app = Litestar(
    root_handler,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    cors_config=CORSConfig(allow_origins=["*"]),
    static_files_config=[StaticFilesConfig(path="/static", directories=["static"])],
    template_config=TemplateConfig(directory="templates", engine=JinjaTemplateEngine),
    middleware=[rate_limit_config.middleware],
    stores={
        "ballot": root_store.with_namespace("ballot"),
        "ip_mul_limiter": root_store.with_namespace("ip_mul_limiter"),
    },
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
)
