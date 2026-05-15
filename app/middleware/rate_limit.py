"""
Per-IP sliding-window rate limiter + request body size cap.

In-memory only — fine for a single-process deployment. If we scale to
multiple gunicorn workers, swap the backing dict for Redis (each worker
keeps its own counter today, so the effective limit is N * max_requests).
"""

import time
import threading
from collections import defaultdict, deque
from typing import Deque, Dict

_MAX_BODY_BYTES = 8 * 1024  # 8 KB — chat queries are tiny; larger = abuse


class RateLimitMiddleware:
    def __init__(self, app, path_prefix: str, max_requests: int, window_seconds: int):
        self.app = app
        self.path_prefix = path_prefix
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        if not path.startswith(self.path_prefix):
            return await self.app(scope, receive, send)

        # Body size cap
        headers = dict(scope.get("headers", []))
        cl = headers.get(b"content-length")
        if cl and cl.isdigit() and int(cl) > _MAX_BODY_BYTES:
            from starlette.responses import JSONResponse
            response = JSONResponse(
                {"results": [{"type": "chat", "message": "Request too large."}]},
                status_code=413,
            )
            return await response(scope, receive, send)

        # Get client IP
        client_ip = "unknown"
        fwd = headers.get(b"x-forwarded-for")
        if fwd:
            client_ip = fwd.decode("latin1").split(",")[0].strip()
        elif scope.get("client"):
            client_ip = scope["client"][0]

        now = time.time()
        cutoff = now - self.window

        with self._lock:
            q = self._hits[client_ip]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.max_requests:
                retry = int(self.window - (now - q[0])) + 1
                is_rate_limited = True
            else:
                is_rate_limited = False
                q.append(now)

        if is_rate_limited:
            from starlette.responses import JSONResponse
            response = JSONResponse(
                {"results": [{"type": "chat", "message": f"Bhai thoda dheere, {retry}s ruk jao."}]},
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
            return await response(scope, receive, send)

        return await self.app(scope, receive, send)
