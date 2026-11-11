import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

# Ovvoru request ku oru ID. Default "-" (request illaadha pothu)
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": request_id_var.get(),
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            log.update(extra)
        if record.exc_info:
            # stack trace LOG la mattum, client ku pogaadhu
            log["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log, default=str)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # uvicorn logs um namma JSON handler kulla varanum
    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    # uvicorn access log la request ID irukkaadhu, so adha off pannrom
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False
