# app/utils/logging.py
import logging
from enum import StrEnum
from typing import Union, Optional
from contextvars import ContextVar

# Default formats (include request_id)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | req_id=%(request_id)s | %(message)s"
LOG_FORMAT_DEBUG = "%(asctime)s | %(levelname)s | %(name)s | req_id=%(request_id)s | %(pathname)s:%(funcName)s:%(lineno)d | %(message)s"


class LogLevels(StrEnum):
    info = "INFO"
    warn = "WARN"   # alias to WARNING
    error = "ERROR"
    debug = "DEBUG"


# Context variable to carry request_id through async tasks
REQUEST_ID_CTX_VAR: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Injects request_id into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.request_id = REQUEST_ID_CTX_VAR.get()
        except LookupError:
            record.request_id = "-"
        return True


def set_request_id(request_id: Optional[str]):
    """Bind a request_id for the current context. Returns a token for reset()."""
    if not request_id:
        request_id = "-"
    return REQUEST_ID_CTX_VAR.set(request_id)


def reset_request_id(token) -> None:
    """Reset the previously bound request_id context."""
    try:
        REQUEST_ID_CTX_VAR.reset(token)
    except Exception:
        # Safe no-op if token is invalid (e.g., background logs)
        pass


def configure_logging(log_level: Union[str, LogLevels, None] = LogLevels.error) -> None:
    """Configure root + uvicorn loggers once, with request_id-aware formatting."""
    # Resolve log level
    level_str = (log_level.value if isinstance(log_level, LogLevels) else str(log_level or "ERROR")).upper()
    if level_str == "WARN":
        level_str = "WARNING"
    level = getattr(logging, level_str, logging.ERROR)

    root = logging.getLogger()
    root.setLevel(level)

    # Only add handlers once
    if not root.handlers:
        handler = logging.StreamHandler()
        fmt = LOG_FORMAT_DEBUG if level == logging.DEBUG else LOG_FORMAT
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(level)
        handler.addFilter(RequestIdFilter())
        root.addHandler(handler)
    else:
        # Ensure level and filter are applied even if handlers already exist
        for h in root.handlers:
            h.setLevel(level)
            h.addFilter(RequestIdFilter())

    # Align common framework loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        lg = logging.getLogger(name)
        lg.setLevel(level)
        # Let uvicorn loggers propagate to root; keep their handlers if any
        if not lg.handlers:
            lg.propagate = True
        for h in lg.handlers:
            h.setLevel(level)
            h.addFilter(RequestIdFilter())