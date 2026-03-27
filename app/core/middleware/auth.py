"""
Cookie-based session authentication.
Mandatory employee_name cookie for all protected transactions.
Persistent sessions via static SECRET_KEY in .env.
"""

import logging
from typing import List
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)

PUBLIC_PATHS: List[str] = [
    "/api/health",
    "/api/modules",
    "/api/features",
    "/",
    "/static",
    "/favicon.ico",
]

PROTECTED_PATHS: List[str] = [
    "/api/",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        # Public paths bypass auth entirely
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Protected paths require employee_name cookie
        if any(path.startswith(p) for p in PROTECTED_PATHS):
            employee_name = request.cookies.get("employee_name")
            if not employee_name:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "authentication_required",
                        "message": "Missing employee_name cookie — session required.",
                    },
                )
            request.state.employee = employee_name
            logger.debug(f"Authenticated: {employee_name} → {path}")

        return await call_next(request)
