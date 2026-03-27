"""
Full audit logging for every API transaction.
Every approve/reject action is traceable.
Output goes to dedicated 'audit' logger for separate log file routing.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

audit_logger = logging.getLogger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.perf_counter()
        employee = getattr(request.state, "employee", "anonymous")

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        audit_logger.info(
            "AUDIT | employee=%s | method=%s | path=%s | status=%d | duration=%.1fms",
            employee,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        return response
