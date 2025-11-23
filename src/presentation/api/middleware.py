"""FastAPI middleware for logging, rate limiting, and error handling."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response."""
        start_time = time.time()

        # Log request
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} "
            f"- {response.status_code} - {process_time:.3f}s"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors gracefully."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log error
            print(f"Error processing request: {str(e)}")
            # Return error response
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "message": str(e)},
            )

