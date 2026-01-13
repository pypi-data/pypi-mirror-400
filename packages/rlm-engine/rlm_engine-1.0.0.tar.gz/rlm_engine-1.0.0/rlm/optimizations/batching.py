"""
Request Batching for High Throughput.

Collects multiple requests and sends them together,
reducing overhead and improving GPU utilization.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable, Any
from threading import Thread, Lock
from queue import Queue, Empty
from concurrent.futures import Future


@dataclass
class PendingRequest:
    """A request waiting to be batched."""
    messages: list[dict]
    future: Future
    created_at: float = field(default_factory=time.time)


class RequestBatcher:
    """
    Batches multiple LLM requests for efficient processing.
    
    Benefits:
    - Better GPU utilization with vLLM
    - Reduced network overhead
    - Higher throughput under load
    
    Usage:
        batcher = RequestBatcher(
            batch_fn=lambda batch: client.batch_completions(batch),
            max_batch_size=8,
            max_wait_ms=50,
        )
        
        # Submit request (returns Future)
        future = batcher.submit(messages)
        result = future.result()  # Blocks until complete
    """
    
    def __init__(
        self,
        batch_fn: Callable[[list[list[dict]]], list[str]],
        max_batch_size: int = 8,
        max_wait_ms: float = 50.0,
    ):
        """
        Args:
            batch_fn: Function that processes a batch of message lists
            max_batch_size: Maximum requests per batch
            max_wait_ms: Maximum wait time before sending partial batch
        """
        self.batch_fn = batch_fn
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        
        self._queue: Queue[PendingRequest] = Queue()
        self._running = False
        self._thread: Thread | None = None
        self._lock = Lock()
        
        # Stats
        self._batches_sent = 0
        self._requests_processed = 0
    
    def start(self):
        """Start the batcher background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = Thread(target=self._batch_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the batcher."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def submit(self, messages: list[dict]) -> Future:
        """
        Submit a request for batching.
        
        Args:
            messages: Chat messages
            
        Returns:
            Future that will contain the response
        """
        if not self._running:
            self.start()
        
        future: Future = Future()
        request = PendingRequest(messages=messages, future=future)
        self._queue.put(request)
        return future
    
    def _batch_loop(self):
        """Background loop that collects and processes batches."""
        while self._running:
            batch: list[PendingRequest] = []
            batch_start = time.time()
            
            # Collect requests
            while len(batch) < self.max_batch_size:
                elapsed_ms = (time.time() - batch_start) * 1000
                wait_ms = max(0, self.max_wait_ms - elapsed_ms)
                
                try:
                    request = self._queue.get(timeout=wait_ms / 1000)
                    batch.append(request)
                except Empty:
                    break
            
            if not batch:
                continue
            
            # Process batch
            try:
                messages_batch = [r.messages for r in batch]
                results = self.batch_fn(messages_batch)
                
                for request, result in zip(batch, results):
                    request.future.set_result(result)
                
                self._batches_sent += 1
                self._requests_processed += len(batch)
                
            except Exception as e:
                for request in batch:
                    request.future.set_exception(e)
    
    @property
    def stats(self) -> dict:
        """Get batcher statistics."""
        return {
            "batches_sent": self._batches_sent,
            "requests_processed": self._requests_processed,
            "avg_batch_size": (
                self._requests_processed / self._batches_sent
                if self._batches_sent > 0 else 0
            ),
            "queue_size": self._queue.qsize(),
        }


class AsyncRequestBatcher:
    """
    Async version of RequestBatcher for async code.
    
    Usage:
        async with AsyncRequestBatcher(batch_fn) as batcher:
            results = await asyncio.gather(
                batcher.submit(messages1),
                batcher.submit(messages2),
                batcher.submit(messages3),
            )
    """
    
    def __init__(
        self,
        batch_fn: Callable[[list[list[dict]]], Awaitable[list[str]]],
        max_batch_size: int = 8,
        max_wait_ms: float = 50.0,
    ):
        self.batch_fn = batch_fn
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        
        self._pending: list[tuple[list[dict], asyncio.Future]] = []
        self._lock = asyncio.Lock()
        self._flush_task: asyncio.Task | None = None
    
    async def submit(self, messages: list[dict]) -> str:
        """Submit request and wait for result."""
        future = asyncio.get_event_loop().create_future()
        
        async with self._lock:
            self._pending.append((messages, future))
            
            if len(self._pending) >= self.max_batch_size:
                await self._flush()
            elif len(self._pending) == 1:
                # Start timer for partial batch
                self._flush_task = asyncio.create_task(self._delayed_flush())
        
        return await future
    
    async def _delayed_flush(self):
        """Flush after timeout."""
        await asyncio.sleep(self.max_wait_ms / 1000)
        async with self._lock:
            if self._pending:
                await self._flush()
    
    async def _flush(self):
        """Process all pending requests."""
        if not self._pending:
            return
        
        batch = self._pending[:]
        self._pending.clear()
        
        if self._flush_task:
            self._flush_task.cancel()
            self._flush_task = None
        
        try:
            messages_batch = [m for m, _ in batch]
            results = await self.batch_fn(messages_batch)
            
            for (_, future), result in zip(batch, results):
                if not future.done():
                    future.set_result(result)
                    
        except Exception as e:
            for _, future in batch:
                if not future.done():
                    future.set_exception(e)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        async with self._lock:
            await self._flush()
