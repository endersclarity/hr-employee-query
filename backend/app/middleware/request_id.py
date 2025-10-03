"""Request ID middleware for distributed tracing."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request.

    The request ID is:
    - Generated as a UUID v4
    - Stored in request.state.request_id
    - Added to response headers as X-Request-ID

    This enables distributed tracing and request tracking across services.
    """

    async def dispatch(self, request, call_next):
        """Process request and add request ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
