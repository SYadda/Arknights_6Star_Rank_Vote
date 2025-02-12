from app.app import app
from app.config import conf

import uvicorn

run_app = app

if __name__ == "__main__":
    uvicorn.run(
        app=run_app,
        reload=conf.server.reload,
        host=conf.server.host,
        port=conf.server.port,
        log_config={
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                },
            },
            "handlers": {
                "default": {"class": "app.logger.LoguruHandler"},
                "access": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        },
    )
