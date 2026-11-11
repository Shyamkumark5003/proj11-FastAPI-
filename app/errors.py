import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_config import request_id_var

logger = logging.getLogger("app.errors")


class AppError(Exception):
    """Namma own errors. Example: raise AppError(503, "db_unavailable", "Database not reachable")"""

    def __init__(self, status_code: int = 400, code: str = "bad_request", message: str = "Bad request"):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def error_response(status_code: int, code: str, message: str, details=None) -> JSONResponse:
    body = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id_var.get(),
        }
    }
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


async def app_error_handler(request: Request, exc: AppError):
    logger.warning("app error", extra={"extra_fields": {"code": exc.code}})
    return error_response(exc.status_code, exc.code, exc.message)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    codes = {404: "not_found", 405: "method_not_allowed"}
    code = codes.get(exc.status_code, "http_error")
    return error_response(exc.status_code, code, str(exc.detail))


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # field name + message mattum. User anuppina "input" value ah thirumba anuppaadhu.
    details = [
        {"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return error_response(422, "validation_error", "Request is invalid", details)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
