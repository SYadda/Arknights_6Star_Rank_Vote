from pathlib import Path
from typing import Literal

import rtoml
from advanced_alchemy.utils.text import slugify
from msgspec import Struct, convert, field
from redis.asyncio import Redis

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.toml"

with Path.open(CONFIG_PATH, encoding="UTF-8") as f:
    CONFIG = rtoml.load(f)

DurationUnit = Literal["second", "minute", "hour", "day"]

class AppSettings(Struct):
    name: str = field(default="arknights-6star-rank-vote")
    url: str = field(default="http://localhost:8000")
    debug: bool = field(default=False)
    allowed_cors_origins: list[str] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slugify(self.name)


class DatabaseSettings(Struct):
    database_url: str = field(default="sqlite+aiosqlite:///./db/data.sqlite")
    echo: bool = field(default=False)
    echo_pool: bool = field(default=False)
    pool_size: int = field(default=5)
    pool_timeout: int = field(default=30)
    pool_recycle: int = field(default=900)


class ServerSettings(Struct):
    host: str = field(default="127.0.0.1")
    port: int = field(default=8000)
    reload: bool = field(default=False)


class LogSettings(Struct):
    log_level: str = field(default="INFO")
    saq_level: str = field(default="INFO")
    sqlalchemy_level: str = field(default="INFO")
    granian_error_level: str = field(default="INFO")
    granian_access_level: str = field(default="INFO")


class RedisSettings(Struct):
    redis_url: str = field(default="redis://localhost:6379/0")
    socket_connect_timeout: int = field(default=5)
    health_check_interval: int = field(default=5)
    socket_keepalive: bool = field(default=True)

    @property
    def client(self) -> Redis:
        return self.get_client()

    def get_client(self) -> Redis:
        return Redis.from_url(
            url=self.redis_url,
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=self.socket_connect_timeout,
            socket_keepalive=self.socket_keepalive,
            health_check_interval=self.health_check_interval,
        )

class RateLimitSettings(Struct):
    rate_limit: int = field(default=50000)
    rate_limit_period: DurationUnit = field(default="day")


class SAQSettings(Struct):
    processes: int = field(default=1)
    concurrency: int = field(default=10)
    web_enabled: bool = field(default=True)
    use_server_lifespan: bool = field(default=True)


class Settings(Struct):
    app: AppSettings = field(default_factory=AppSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LogSettings = field(default_factory=LogSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    saq: SAQSettings = field(default_factory=SAQSettings)


conf = convert(CONFIG, Settings)
