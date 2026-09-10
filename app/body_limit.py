from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.responses import JSONResponse
from starlette.types import Message, Receive, Scope, Send


class _BodyLimitExceeded(Exception):
    pass


class RequestBodyLimitMiddleware:
    """Reject oversized request bodies before multipart parsing starts."""

    def __init__(
        self,
        app: Callable[[Scope, Receive, Send], Awaitable[None]],
        *,
        path: str | tuple[str, ...],
        maximum: int,
    ) -> None:
        self.app = app
        self.paths = {path} if isinstance(path, str) else set(path)
        self.maximum = maximum

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        values = [
            value
            for name, value in scope.get("headers", [])
            if name.lower() == b"content-length"
        ]
        if not values:
            return None
        if len(values) != 1:
            raise ValueError("ambiguous content length")
        try:
            declared = int(values[0].decode("ascii"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("invalid content length") from exc
        if declared < 0:
            raise ValueError("invalid content length")
        return declared

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") not in self.paths
        ):
            await self.app(scope, receive, send)
            return

        try:
            declared = self._content_length(scope)
        except ValueError:
            await JSONResponse(
                {"detail": "Invalid content length"},
                status_code=400,
            )(scope, receive, send)
            return
        if declared is not None and declared > self.maximum:
            await JSONResponse(
                {"detail": "Upload request exceeds the local limit"},
                status_code=413,
            )(scope, receive, send)
            return

        total = 0

        async def limited_receive() -> Message:
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.maximum:
                    raise _BodyLimitExceeded
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyLimitExceeded:
            await JSONResponse(
                {"detail": "Upload request exceeds the local limit"},
                status_code=413,
            )(scope, receive, send)
