from fastapi import FastAPI

from app.api.v1.documents import router as documents_router
from app.api.v1.jobs import router as jobs_router
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware

configure_logging()

app = FastAPI(
    title="Document Processing Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(AppError, app_error_handler)
app.include_router(documents_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
