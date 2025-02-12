from datetime import datetime

from app.config import conf

from litestar.plugins.sqlalchemy import (
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    base,
)
from sqlalchemy.orm import Mapped, mapped_column


class Archive(base.DefaultBase):
    __tablename__ = "archive"

    key: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column()
    vote_times: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)
    shared_link: Mapped[str] = mapped_column(default=None)
    ip: Mapped[str] = mapped_column()


class OperatorsVoteRecords(base.DefaultBase):
    __tablename__ = "operators_vote_records"

    operator_id: Mapped[int] = mapped_column(primary_key=True)
    score_win: Mapped[float] = mapped_column(default=1)
    score_lose: Mapped[float] = mapped_column(default=1)


session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///./db/data.sqlite",
    session_config=session_config,
    create_all=True,
    engine_config=EngineConfig(
        echo=conf.db.echo,
        echo_pool=conf.db.echo_pool,
        pool_size=conf.db.pool_size,
        pool_timeout=conf.db.pool_timeout,
        pool_recycle=conf.db.pool_recycle,
    ),
)
