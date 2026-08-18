from __future__ import annotations

import logging
import re

_DATABASE_CREDENTIALS = re.compile(
    r"(?P<prefix>\b[a-z][a-z0-9+.-]*://[^:\s/]+:)[^@\s]+@", re.IGNORECASE
)
_KEY_VALUE_SECRET = re.compile(
    r"(?P<key>\b(?:api[_-]?key|authorization|password|secret|token)\s*=\s*)[^\s,;]+",
    re.IGNORECASE,
)
_BEARER_TOKEN = re.compile(r"\bBearer\s+[^\s,;]+", re.IGNORECASE)


def redact_sensitive_text(value: str) -> str:
    redacted = _DATABASE_CREDENTIALS.sub(r"\g<prefix>***@", value)
    redacted = _KEY_VALUE_SECRET.sub(r"\g<key>***", redacted)
    return _BEARER_TOKEN.sub("Bearer ***", redacted)


class SecretRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_text(record.getMessage())
        record.args = ()
        return True


def configure_logging(log_level: str) -> None:
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers:
        if not any(isinstance(log_filter, SecretRedactionFilter) for log_filter in handler.filters):
            handler.addFilter(SecretRedactionFilter())
