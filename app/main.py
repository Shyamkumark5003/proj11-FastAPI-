import logging

from fastapi import FastAPI

from app.config import get_settings
from app.errors import register_error_handlers
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
from app.routes import router

logger = logging.getLogger("app")


def create_app() -> FastAPI:
    settings = get_settings()  # config missing na, inga ye startup stop
    setup_logging(settings.log_level)

    # docs dev la mattum on; matha env la off
    docs_url = "/docs" if settings.docs_enabled else None
    redoc_url = "/redoc" if settings.docs_enabled else None
    openapi_url = "/openapi.json" if settings.docs_enabled else None

    app = FastAPI(
        title="RAG Service",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    app.add_middleware(RequestIDMiddleware)
    register_error_handlers(app)
    app.include_router(router)

    logger.info("app created", extra={"extra_fields": {"env": settings.app_env}})
    return app


app = create_app()
