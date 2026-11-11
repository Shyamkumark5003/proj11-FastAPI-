import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.errors import error_response
from app.logging_config import request_id_var

logger = logging.getLogger("app.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                # full stack trace LOG la mattum (exc_info)
                logger.exception("unhandled error")
                # client ku safe message mattum
                response = error_response(
                    500, "internal_error", "Something went wrong. Please contact support with the request_id."
                )

            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request completed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration_ms": duration_ms,
                    }
                },
            )
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)
