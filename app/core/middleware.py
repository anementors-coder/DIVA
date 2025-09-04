# app/core/middleware.py
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logging import set_request_id, reset_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    - Generates or propagates X-Request-ID per request
    - Attaches to request.state for handlers
    - Adds X-Request-ID and X-Response-Time to successful responses
    - Binds request_id to logging context for the duration of the request
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.perf_counter()

        # Bind to logging context
        token = set_request_id(request_id)

        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            # Always unbind the request_id after request finishes
            reset_request_id(token)
            if response is not None:
                duration_ms = int((time.perf_counter() - request.state.start_time) * 1000)
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = f"{duration_ms}ms"