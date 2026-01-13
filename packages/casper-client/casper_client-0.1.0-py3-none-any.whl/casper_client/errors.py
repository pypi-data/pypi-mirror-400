from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CasperErrorKind(str, Enum):
    CLIENT = "client"
    SERVER = "server"
    NOT_FOUND = "not_found"
    OPERATION_NOT_ALLOWED = "operation_not_allowed"
    CONFLICT = "conflict"
    INVALID_RESPONSE = "invalid_response"
    UNKNOWN = "unknown"


@dataclass
class CasperError(Exception):
    kind: CasperErrorKind
    message: str
    status: int | None = None
    cause: Exception | None = None

    def __str__(self) -> str:
        status_part = f" (status={self.status})" if self.status is not None else ""
        cause_part = f" (cause={self.cause!r})" if self.cause is not None else ""
        return f"casper: {self.kind.value}{status_part}: {self.message}{cause_part}"


def classify_http_error(status: int, message: str) -> CasperError:
    if status == 404:
        kind = CasperErrorKind.NOT_FOUND
    elif status == 405:
        kind = CasperErrorKind.OPERATION_NOT_ALLOWED
    elif status == 409:
        kind = CasperErrorKind.CONFLICT
    elif 400 <= status < 500:
        kind = CasperErrorKind.CLIENT
    elif 500 <= status <= 599:
        kind = CasperErrorKind.SERVER
    else:
        kind = CasperErrorKind.UNKNOWN
    return CasperError(kind=kind, status=status, message=message)


