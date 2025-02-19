import logging
import sys
from functools import lru_cache

import structlog
from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging.config import (
    LoggingConfig,
    StructLoggingConfig,
    default_logger_factory,
    default_structlog_processors,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.plugins.problem_details import ProblemDetailsConfig
from litestar.plugins.prometheus import PrometheusConfig

from litestar.plugins.structlog import StructlogConfig
from litestar.static_files.config import StaticFilesConfig
from litestar.template import TemplateConfig
from litestar_saq import CronJob, QueueConfig, SAQConfig

from app import task

from .config import conf

compression = CompressionConfig(backend="gzip")
rate_limit = RateLimitConfig(
    rate_limit=(
        conf.rate_limit.rate_limit_period,
        conf.rate_limit.rate_limit,
    )
)
problem_details = ProblemDetailsConfig(enable_for_all_http_exceptions=True)
cors = CORSConfig(allow_origins=conf.app.allowed_cors_origins)
saq = SAQConfig(
    web_enabled=conf.saq.web_enabled,
    use_server_lifespan=conf.saq.use_server_lifespan,
    queue_configs=[
        QueueConfig(
            dsn=f"{conf.redis.redis_url}",
            name="database_save_task",
            # 1 minute
            scheduled_tasks=[CronJob(function=task.database_save_task, cron="* * * * *", timeout=600, ttl=2000)],
        ),
        QueueConfig(
            dsn=f"{conf.redis.redis_url}",
            name="redis_op_matrix_update_task",
            # 1 minute, 或者要不把redis_op_matrix_update_task()合到上面那个队列去?
            scheduled_tasks=[
                CronJob(function=task.redis_op_matrix_update_task, cron="* * * * *", timeout=600, ttl=2000)
            ],
        ),

    ],
)
templates = TemplateConfig(directory="templates", engine=JinjaTemplateEngine)
static_files = StaticFilesConfig(path="/static", directories=["static"])
prometheus_config = PrometheusConfig(
    app_name="arknights-6star-rank-vote",
    prefix="vote",
    exclude=["/metrics"],
)



@lru_cache
def _is_tty() -> bool:
    return bool(sys.stderr.isatty() or sys.stdout.isatty())


_render_as_json = not _is_tty()
_structlog_default_processors = default_structlog_processors(as_json=_render_as_json)
_structlog_default_processors.insert(1, structlog.processors.EventRenamer("message"))
_structlog_standard_lib_processors = default_structlog_standard_lib_processors(as_json=_render_as_json)
_structlog_standard_lib_processors.insert(1, structlog.processors.EventRenamer("message"))

log = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions="always",
        processors=_structlog_default_processors,
        logger_factory=default_logger_factory(as_json=_render_as_json),
        standard_lib_logging_config=LoggingConfig(
            root={"level": logging.getLevelName(conf.log.log_level), "handlers": ["queue_listener"]},
            formatters={
                "standard": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": _structlog_standard_lib_processors,
                },
            },
            loggers={
                "granian.access": {
                    "propagate": False,
                    "level": conf.log.granian_access_level,
                    "handlers": ["queue_listener"],
                },
                "granian.error": {
                    "propagate": False,
                    "level": conf.log.granian_error_level,
                    "handlers": ["queue_listener"],
                },
                "saq": {
                    "propagate": False,
                    "level": conf.log.saq_level,
                    "handlers": ["queue_listener"],
                },
                "sqlalchemy.engine": {
                    "propagate": False,
                    "level": conf.log.sqlalchemy_level,
                    "handlers": ["queue_listener"],
                },
                "sqlalchemy.pool": {
                    "propagate": False,
                    "level": conf.log.sqlalchemy_level,
                    "handlers": ["queue_listener"],
                },
            },
        ),
    ),
    middleware_logging_config=LoggingMiddlewareConfig(
        request_log_fields=["method", "path", "path_params", "query"],
        response_log_fields=["status_code"],
    ),
)
