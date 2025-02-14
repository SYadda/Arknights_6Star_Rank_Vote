from pathlib import Path
from typing import Literal

from msgspec import Struct, convert, field
import rtoml

CONFIG_PATH = Path(__file__).parent.parent / "config.toml"

with Path.open(CONFIG_PATH, encoding="UTF-8") as f:
    CONFIG = rtoml.load(f)

DurationUnit = Literal["second", "minute", "hour", "day"]

class AppSettings(Struct):
    url: str = field(default="http://localhost:8000")
    debug: bool = field(default=False)


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


class RedisSettings(Struct):
    redis_url: str = field(default="redis://localhost:6379")
    redis_db: int = field(default=0)

class RateLimitSettings(Struct):
    rate_limit: int = field(default=50000)
    rate_limit_period: DurationUnit = field(default="day")


class Settings(Struct):
    app: AppSettings = field(default_factory=AppSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LogSettings = field(default_factory=LogSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)


conf = convert(CONFIG, Settings)
