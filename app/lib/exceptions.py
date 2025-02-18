import sys
from typing import Any

from advanced_alchemy.exceptions import IntegrityError
from litestar.connection import Request
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
    PermissionDeniedException,
)
from litestar.exceptions.responses import ExceptionResponseContent, create_debug_response, create_exception_response
from litestar.repository.exceptions import ConflictError, NotFoundError, RepositoryError
from litestar.response import Response
from litestar.status_codes import HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.types import Scope
from structlog.contextvars import bind_contextvars

__all__ = (
    "ApplicationError",
    "after_exception_hook_handler",
)


class ApplicationError(Exception):
    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        str_args = [str(arg) for arg in args if arg]
        if not detail:
            if str_args:
                detail, *str_args = str_args
            elif hasattr(self, "detail"):
                detail = self.detail
        self.detail = detail
        super().__init__(*str_args)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return " ".join((*self.args, self.detail)).strip()


class ApplicationClientError(ApplicationError):
    pass


class _HTTPConflictException(HTTPException):
    status_code = HTTP_409_CONFLICT


async def after_exception_hook_handler(exc: Exception, _scope: Scope) -> None:
    if isinstance(exc, ApplicationError):
        return
    if isinstance(exc, HTTPException) and exc.status_code < HTTP_500_INTERNAL_SERVER_ERROR:
        return
    bind_contextvars(exc_info=sys.exc_info())


def exception_to_http_response(
    request: Request[Any, Any, Any],
    exc: ApplicationError | RepositoryError,
) -> Response[ExceptionResponseContent]:
    http_exc: type[HTTPException]
    if isinstance(exc, NotFoundError):
        http_exc = NotFoundException
    elif isinstance(exc, ConflictError | RepositoryError | IntegrityError):
        http_exc = _HTTPConflictException
    else:
        http_exc = InternalServerException
    if request.app.debug and http_exc not in (PermissionDeniedException, NotFoundError):
        return create_debug_response(request, exc)
    return create_exception_response(request, http_exc(detail=str(exc.__cause__)))
