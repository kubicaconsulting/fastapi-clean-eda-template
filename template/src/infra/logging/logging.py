"""Structured logging configuration."""

import sys
import json
import traceback

from loguru import logger

from config.main import get_settings


settings = get_settings()

# Set up base logging level
log_level = "DEBUG" if settings.debug else "INFO"


def serialize(record):
    fields = {
        "time": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "level": record["level"].name,
        "message": record["message"],
        "context": {
            **record["extra"],
        },
    }

    if record["exception"]:
        exc = record["exception"]
        fields["exception"] = {
            "type": exc.type.__name__,
            "value": str(exc.value),
            "traceback": traceback.format_exception(exc.type, exc.value, exc.traceback),
        }

    return json.dumps(fields)


def patching(record):
    record["serialized"] = serialize(record)


logger.remove(0)
logger = logger.patch(patching)
logger.add(
    sys.stderr,
    level=log_level,
    enqueue=True,  # non-blocking and safe across threads/processes
    format="{serialized}\n",
)
