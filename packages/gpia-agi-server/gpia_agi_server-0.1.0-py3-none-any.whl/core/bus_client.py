"""Client for interacting with the message bus.

All network requests are wrapped in exception handling. Any errors are
recorded to the knowledge base via :func:`kb.add_entry`. Both GET and POST
operations support an optional retry mechanism with exponential backoff,
configurable via the ``retries`` and ``backoff`` parameters on
``BusClient``. Optional ``jitter`` and ``circuit_breaker`` callbacks allow
customisation of retry delays and early termination of retries.
"""

import os
import asyncio
import logging
from uuid import uuid4
from typing import Any, Callable, Dict, Optional, TypeVar, Coroutine, Type

import httpx

from core.kb import add_entry
from core.settings import settings
from hnet.dynamic_chunker import DynamicChunker


T = TypeVar("T")

logger = logging.getLogger(__name__)


class BusClient:
    def __init__(
        self,
        base_url: str,
        topic: str,
        handler: Callable[[Dict[str, Any]], None],
        *,
        retries: int = 0,
        backoff: float = 0.0,
        token: Optional[str] = None,
        jitter: Optional[Callable[[float], float]] = None,
        circuit_breaker: Optional[Callable[[], bool]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.topic = topic
        self.handler = handler
        self.retries = retries
        self.backoff = backoff
        self.token = token or settings.BUS_TOKEN or os.environ.get("BUS_TOKEN")
        self.jitter = jitter
        self.circuit_breaker = circuit_breaker
        self.client_id = uuid4().hex
        self._stop = False
        self._client = httpx.AsyncClient(timeout=60)

    async def _with_retry(
        self,
        func: Callable[[], Coroutine[Any, Any, T]],
        *,
        label: str,
        retries: int,
        backoff: float,
        exc_type: Type[Exception],
    ) -> T | None:
        for attempt in range(retries + 1):
            try:
                return await func()
            except exc_type as exc:  # pragma: no cover - logging path
                logger.exception("%s failed", label)
                add_entry(kind="bus_client_error", data=f"{label} failed: {exc}")
                if self.circuit_breaker and self.circuit_breaker():
                    break
                if attempt < retries:
                    delay = backoff * (2**attempt)
                    if self.jitter:
                        delay = self.jitter(delay)
                    if delay:
                        await asyncio.sleep(delay)
        return None

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
        **kwargs: Any,
    ) -> httpx.Response | None:
        return await self._arequest(
            method,
            endpoint,
            retries=retries,
            backoff=backoff,
            **kwargs,
        )

    async def run(self) -> None:
        """Process a single message from the bus."""
        r = await self._request(
            "get",
            "get",
            params={
                "topic": self.topic,
                "group": self.client_id,
                "consumer": self.client_id,
            },
        )
        if r and r.status_code == 200:
            msg = r.json()
            data = msg.get("data", {})
            text = data.get("text")
            if text:
                chunker = DynamicChunker()
                chunks = chunker.chunk(text)
                total = len(chunks)
                for idx, chunk in enumerate(chunks, 1):
                    payload: Dict[str, Any] = {
                        "topic": msg.get("topic", self.topic),
                        "data": {
                            **{k: v for k, v in data.items() if k != "text"},
                            "text": chunk,
                            "chunk": idx,
                            "total": total,
                        },
                    }
                    if settings.USE_OPENVINO:
                        try:
                            from integrations.openvino_embedder import get_embeddings

                            payload["data"]["embedding"] = get_embeddings(chunk)
                        except Exception:  # pragma: no cover - inference failure
                            pass
                    self.handler(payload)
            else:
                self.handler(msg)
        else:
            await asyncio.sleep(1)

    async def run_forever(self) -> None:
        """Continuously process messages until :meth:`stop` is called."""
        while not self._stop:
            await self.run()

    async def stop(self) -> None:
        self._stop = True
        await self._client.aclose()

    async def _arequest(
        self,
        method: str,
        endpoint: str,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
        **kwargs: Any,
    ) -> httpx.Response | None:
        retries = self.retries if retries is None else retries
        backoff = self.backoff if backoff is None else backoff
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.pop("headers", {})
        if self.token:
            headers.setdefault("Authorization", f"Bearer {self.token}")

        async def call() -> httpx.Response:
            return await self._client.request(method, url, headers=headers, **kwargs)
        request_coro: Callable[[], Coroutine[Any, Any, httpx.Response]] = call

        result = await self._with_retry(
            request_coro,
            label=f"{method.upper()} {url}",
            retries=retries,
            backoff=backoff,
            exc_type=httpx.RequestError,
        )
        return result

    async def publish(
        self,
        topic: str,
        data: str,
        *,
        retries: Optional[int] = None,
        backoff: Optional[float] = None,
    ) -> None:
        """Chunk ``data`` and publish each piece asynchronously."""
        chunker = DynamicChunker()
        chunks = chunker.chunk(data)
        total = len(chunks)
        for idx, chunk in enumerate(chunks, 1):
            payload: Dict[str, Any] = {
                "topic": topic,
                "data": {"text": chunk, "chunk": idx, "total": total},
            }
            if settings.USE_OPENVINO:
                try:
                    from integrations.openvino_embedder import get_embeddings

                    payload["data"]["embedding"] = get_embeddings(chunk)
                except Exception:  # pragma: no cover - inference failure
                    pass
            await self._arequest(
                "post",
                "publish",
                retries=retries,
                backoff=backoff,
                json=payload,
            )
