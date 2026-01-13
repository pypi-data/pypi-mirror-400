import asyncio
import inspect
from typing import AsyncGenerator, AsyncIterator, Awaitable, Callable, Optional, Union

Chunk = Union[bytes, str]
TransformReturn = Union[Chunk, AsyncGenerator[Chunk, None]]
TransformFn = Callable[[Chunk], Union[TransformReturn, Awaitable[TransformReturn]]]


class MessageTransformer:
    """
    Single-worker async chunk transformer with decoupled emissions.
    No max queue size, no concurrency.
    """

    def __init__(self, transform: TransformFn):
        self._transform = transform
        self._in_q: asyncio.Queue[Optional[Chunk]] = asyncio.Queue()  # unbounded
        self._out_q: asyncio.Queue[Optional[Chunk]] = asyncio.Queue()  # unbounded
        self._worker: Optional[asyncio.Task] = None
        self._closed_in = False
        self._closed_out = False

    async def __aenter__(self):
        self._ensure_worker()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def _ensure_worker(self):
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                item = await self._in_q.get()
                if item is None:
                    self._in_q.task_done()
                    break
                try:
                    ret = self._transform(item)
                    if asyncio.iscoroutine(ret):
                        ret = await ret  # type: ignore[assignment]

                    if inspect.isasyncgen(ret):  # async generator -> stream many
                        async for out in ret:  # type: ignore[misc]
                            await self._out_q.put(out)
                    else:  # single chunk
                        await self._out_q.put(ret)  # type: ignore[arg-type]
                except Exception as e:
                    # Surface transform errors downstream as a chunk of the same "kind"
                    err = (
                        f"[transform-error]: {e}"
                        if isinstance(item, str)
                        else f"[transform-error]: {e}".encode()
                    )
                    await self._out_q.put(err)  # type: ignore[arg-type]
                finally:
                    self._in_q.task_done()
        finally:
            if not self._closed_out:
                await self._out_q.put(None)
                self._closed_out = True

    async def feed(self, chunk: Chunk):
        if self._closed_in:
            raise RuntimeError("Cannot feed after end()")
        self._ensure_worker()
        await self._in_q.put(chunk)

    async def end(self):
        if self._closed_in:
            return
        self._closed_in = True
        self._ensure_worker()
        await self._in_q.put(None)

    async def aclose(self):
        await self.end()
        if self._worker:
            await self._worker

    def __aiter__(self) -> AsyncIterator[Chunk]:
        self._ensure_worker()
        return self._iterate_outputs()

    async def _iterate_outputs(self) -> AsyncIterator[Chunk]:
        while True:
            item = await self._out_q.get()
            if item is None:
                self._out_q.task_done()
                break
            try:
                yield item
            finally:
                self._out_q.task_done()
