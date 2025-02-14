from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from pprint import pformat
import re
import sys
from typing import TYPE_CHECKING, Any

from app.config import conf
from app.data_store import get_res_path
from app.status import HTTP_STATUS_TEXT_MAP

import loguru

if TYPE_CHECKING:
    # avoid sphinx autodoc resolve annotation failed
    # because loguru module do not have `Logger` class actually
    from loguru import Logger

LEVELSTRMAP = {
    "DEBUG": "DBG",
    "TRACE": "TRC",
    "INFO": "INF",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")

logger: "Logger" = loguru.logger


# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class ColorizedHTTPStatus:
    @classmethod
    def colorize(cls, status_code: int) -> str:
        status_text = HTTP_STATUS_TEXT_MAP.get(status_code, "")
        if 200 <= status_code < 300:
            return f" \033[0;32m{status_code} {status_text}\033[0m"
        if 300 <= status_code < 400:
            return f" \033[0;33m{status_code} {status_text}\033[0m"
        if 400 <= status_code < 500:
            return f" \033[0;31m{status_code} {status_text}\033[0m"
        if 500 <= status_code < 600:
            return f" \033[0;35m{status_code} {status_text}\033[0m"
        return str(status_code)


def format_record(record: Any) -> str:
    time = "[<g>{time:YYYY-MM-DD HH:mm:ss.ss}</g>]"
    record["level"].name = LEVELSTRMAP.get(record["level"].name, record["level"].name)
    level = "[<lvl>{level}</lvl>]"
    def_name = "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    message = "<level>{message}</level>"
    format_string = time + level + " - " + def_name + " | " + message
    if INTEGER_PATTERN.match(code := record["message"].split(" ")[-1]):
        record["message"] = record["message"].replace(f" {code}", ColorizedHTTPStatus.colorize(int(code)))
    if isinstance(record["extra"].get("payload"), dict | list | tuple):
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"
    format_string += "{exception}\n"

    return format_string


time_now = datetime.now()
Path("./log").mkdir(exist_ok=True)
last_log = max(Path("./log").glob("Server_*"), default=None, key=os.path.getmtime)

if last_log and (
    time_now - datetime.fromtimestamp(Path.stat(last_log).st_mtime)
) < timedelta(hours=1):
    log_file = f"log/{last_log.name}"
else:
    log_file = f'log/Server_{time_now.strftime("%Y-%m-%d_%H-%M-%S")}.log'

LEVEL: str = conf.log.log_level

logger.remove()
logger_id = logger.add(sys.stdout, level=LEVEL, diagnose=False, format=format_record)

logger.add(
    sink=get_res_path() / log_file,
    format=format_record,
    level=LEVEL,
    diagnose=False,
)
