"""
FastAPI middleware: request logging, timing, error handling.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

logger = logging.getLogger("fastapi.lms")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}"
            + (f"?{request.url.query}" if request.url.query else "")
        )

        try:
            response = await call_next(request)
            duration = (time.time() - start) * 1000
            logger.info(
                f"[{request_id}] {response.status_code} — {duration:.1f}ms"
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.1f}ms"
            return response
        except Exception as exc:
            duration = (time.time() - start) * 1000
            logger.exception(f"[{request_id}] Unhandled error after {duration:.1f}ms")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error", "request_id": request_id},
            )


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = " → ".join(str(e) for e in error["loc"])
            errors.append({"field": field, "message": error["msg"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "errors": errors},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": f"Route {request.url.path} not found"},
        )
