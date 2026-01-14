"""
infinity_institute - Python SDK for media generation.

Mirrors fal_client's API design with SyncClient, AsyncClient, and module-level functions.
"""

import os
import time
import asyncio
import httpx
from typing import Any, Dict, Iterator, Optional, Union, Callable
from pathlib import Path

from .models import (
    Status,
    Completed,
    Failed,
    ImageResult,
    VideoResult,
    AudioResult,
    AnyJSON,
    parse_status,
    parse_result,
)


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class InfinityClientError(Exception):
    """Base exception for Infinity client errors."""

    pass


class JobFailedError(InfinityClientError):
    """Raised when a job fails."""

    def __init__(self, request_id: str, error: str):
        self.request_id = request_id
        self.error = error
        super().__init__(f"Job {request_id} failed: {error}")


class TimeoutError(InfinityClientError):
    """Raised when polling times out."""

    pass


# ─────────────────────────────────────────────────────────────────────────────
# Request Handle (fal_client style)
# ─────────────────────────────────────────────────────────────────────────────


class SyncRequestHandle:
    """
    Handle to a submitted request.

    Returned by submit(), allows checking status and getting results.
    """

    def __init__(
        self,
        client: httpx.Client,
        base_url: str,
        application: str,
        request_id: str,
    ):
        self._client = client
        self._base_url = base_url
        self._application = application
        self.request_id = request_id

    def status(self, *, with_logs: bool = False) -> Status:
        """
        Returns the status of the request.

        Returns: Queued, InProgress, Completed, or Failed
        """
        response = self._client.get(
            f"{self._base_url}/{self._application}/requests/{self.request_id}/status"
        )
        response.raise_for_status()
        return parse_status(response.json())

    def get(self) -> AnyJSON:
        """
        Wait until the request is completed and return the result.

        Returns: Raw JSON response dict
        """
        while True:
            status = self.status()
            if isinstance(status, Completed):
                response = self._client.get(
                    f"{self._base_url}/{self._application}/requests/{self.request_id}"
                )
                response.raise_for_status()
                return response.json()
            elif isinstance(status, Failed):
                raise JobFailedError(self.request_id, status.error)
            time.sleep(1.0)

    def iter_events(
        self,
        *,
        with_logs: bool = False,
        interval: float = 0.5,
    ) -> Iterator[Status]:
        """
        Continuously poll for status and yield at each interval until completed.
        """
        while True:
            status = self.status(with_logs=with_logs)
            yield status
            if isinstance(status, (Completed, Failed)):
                break
            time.sleep(interval)

    def cancel(self) -> None:
        """Cancel the request (if supported by server)."""
        # Note: Our server doesn't support cancel yet, but keeping API compatible
        pass


class AsyncRequestHandle:
    """
    Async handle to a submitted request.

    Returned by submit_async(), allows async checking status and getting results.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        application: str,
        request_id: str,
    ):
        self._client = client
        self._base_url = base_url
        self._application = application
        self.request_id = request_id

    async def status(self, *, with_logs: bool = False) -> Status:
        """Returns the status of the request."""
        response = await self._client.get(
            f"{self._base_url}/{self._application}/requests/{self.request_id}/status"
        )
        response.raise_for_status()
        return parse_status(response.json())

    async def get(self) -> AnyJSON:
        """Wait until the request is completed and return the result."""
        while True:
            status = await self.status()
            if isinstance(status, Completed):
                response = await self._client.get(
                    f"{self._base_url}/{self._application}/requests/{self.request_id}"
                )
                response.raise_for_status()
                return response.json()
            elif isinstance(status, Failed):
                raise JobFailedError(self.request_id, status.error)
            await asyncio.sleep(1.0)

    async def cancel(self) -> None:
        """Cancel the request (if supported by server)."""
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Sync Client
# ─────────────────────────────────────────────────────────────────────────────


class SyncClient:
    """
    Synchronous client for Infinity Media Server.

    Mirrors fal_client.SyncClient API.

    Usage:
        client = SyncClient("http://192.222.55.191:8000")

        # Run and wait for result
        result = client.run("black-forest-labs/flux-dev", {"prompt": "A cat"})

        # Or submit and poll manually
        handle = client.submit("black-forest-labs/flux-dev", {"prompt": "A cat"})
        for status in handle.iter_events():
            print(status)
        result = handle.get()

        # Use environment variable for server URL
        # export INFINITY_SERVER_URL=http://your-server:8000
        client = SyncClient()  # Uses INFINITY_SERVER_URL or default
    """

    # Default server URL (can be overridden via INFINITY_SERVER_URL env var)
    DEFAULT_URL = os.environ.get("INFINITY_SERVER_URL", "http://192.222.55.191:8000")

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_timeout: float = 300.0,
    ):
        """
        Initialize the client.

        Args:
            base_url: Server URL. If not provided, uses INFINITY_SERVER_URL env var
                      or falls back to the default demo server.
            default_timeout: Default timeout for run() in seconds
        """
        if base_url is None:
            base_url = self.DEFAULT_URL
        self.base_url = base_url.rstrip("/")
        self.default_timeout = default_timeout
        self._client = httpx.Client(timeout=30.0)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    # ─────────────────────────────────────────────────────────────────────────
    # Core Methods (fal_client style)
    # ─────────────────────────────────────────────────────────────────────────

    def run(
        self,
        application: str,
        arguments: AnyJSON,
        *,
        timeout: Optional[float] = None,
    ) -> AnyJSON:
        """
        Run an application with the given arguments (blocking).

        This method will submit the job and wait for the result.

        Args:
            application: Model name (e.g., "black-forest-labs/flux-dev")
            arguments: Model parameters as dict (e.g., {"prompt": "A cat"})
            timeout: Max seconds to wait (default: self.default_timeout)

        Returns: Raw JSON response dict
        """
        timeout = timeout or self.default_timeout
        handle = self.submit(application, arguments)

        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Job {handle.request_id} timed out after {timeout}s"
                )

            status = handle.status()
            if isinstance(status, Completed):
                return handle.get()
            elif isinstance(status, Failed):
                raise JobFailedError(handle.request_id, status.error)

            time.sleep(1.0)

    def submit(
        self,
        application: str,
        arguments: AnyJSON,
    ) -> SyncRequestHandle:
        """
        Submit a job (non-blocking).

        Args:
            application: Model name (e.g., "black-forest-labs/flux-dev")
            arguments: Model parameters as dict

        Returns: SyncRequestHandle for polling status and getting result
        """
        response = self._client.post(
            f"{self.base_url}/{application}",
            json=arguments,
        )
        response.raise_for_status()
        data = response.json()

        return SyncRequestHandle(
            client=self._client,
            base_url=self.base_url,
            application=application,
            request_id=data["request_id"],
        )

    def subscribe(
        self,
        application: str,
        arguments: AnyJSON,
        *,
        on_enqueue: Optional[Callable[[str], None]] = None,
        on_queue_update: Optional[Callable[[Status], None]] = None,
    ) -> AnyJSON:
        """
        Submit and subscribe to status updates until complete.

        Args:
            application: Model name
            arguments: Model parameters
            on_enqueue: Callback when job is enqueued (receives request_id)
            on_queue_update: Callback on each status update

        Returns: Raw JSON response dict
        """
        handle = self.submit(application, arguments)

        if on_enqueue:
            on_enqueue(handle.request_id)

        for status in handle.iter_events():
            if on_queue_update:
                on_queue_update(status)

        return handle.get()

    def status(
        self,
        application: str,
        request_id: str,
        *,
        with_logs: bool = False,
    ) -> Status:
        """Get status of a request by ID."""
        response = self._client.get(
            f"{self.base_url}/{application}/requests/{request_id}/status"
        )
        response.raise_for_status()
        return parse_status(response.json())

    def result(
        self,
        application: str,
        request_id: str,
    ) -> AnyJSON:
        """Get result of a completed request."""
        response = self._client.get(
            f"{self.base_url}/{application}/requests/{request_id}"
        )
        response.raise_for_status()
        return response.json()

    def cancel(
        self,
        application: str,
        request_id: str,
    ) -> None:
        """Cancel a request (if supported by server)."""
        pass

    def get_handle(
        self,
        application: str,
        request_id: str,
    ) -> SyncRequestHandle:
        """Get a handle to an existing request by ID."""
        return SyncRequestHandle(
            client=self._client,
            base_url=self.base_url,
            application=application,
            request_id=request_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Health & Info
    # ─────────────────────────────────────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
        """Check server health."""
        response = self._client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def ready(self) -> Dict[str, Any]:
        """Check server readiness and GPU status."""
        response = self._client.get(f"{self.base_url}/ready")
        response.raise_for_status()
        return response.json()

    def models(self) -> Dict[str, Any]:
        """List available models and their status."""
        response = self._client.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience Methods (typed results)
    # ─────────────────────────────────────────────────────────────────────────

    def image(
        self,
        prompt: str,
        model: str = "black-forest-labs/flux-dev",
        **kwargs,
    ) -> ImageResult:
        """
        Generate an image (blocking, returns typed result).

        Args:
            prompt: Text prompt
            model: Image model (default: black-forest-labs/flux-dev)
            **kwargs: Additional parameters (width, height, seed, etc.)
        """
        handle = self.submit(model, {"prompt": prompt, **kwargs})
        raw = handle.get()
        result = parse_result(raw, handle.request_id)
        assert isinstance(result, ImageResult)
        return result

    def video(
        self,
        prompt: str,
        model: str = "wan-ai/wan2.2-t2v",
        **kwargs,
    ) -> VideoResult:
        """
        Generate a video (blocking, returns typed result).

        Args:
            prompt: Text prompt
            model: Video model (default: wan-ai/wan2.2-t2v)
            **kwargs: Additional parameters (num_frames, fps, etc.)
        """
        handle = self.submit(model, {"prompt": prompt, **kwargs})
        raw = handle.get()
        result = parse_result(raw, handle.request_id)
        assert isinstance(result, VideoResult)
        return result

    def audio(
        self,
        text: str,
        model: str = "boson-ai/higgs-audio-v2",
        **kwargs,
    ) -> AudioResult:
        """
        Generate audio/speech (blocking, returns typed result).

        Args:
            text: Text to synthesize
            model: Audio model (default: boson-ai/higgs-audio-v2)
            **kwargs: Additional parameters (voice, temperature, etc.)
        """
        handle = self.submit(model, {"text": text, **kwargs})
        raw = handle.get()
        result = parse_result(raw, handle.request_id)
        assert isinstance(result, AudioResult)
        return result

    def download(
        self,
        url: str,
        output_path: Union[str, Path],
    ) -> Path:
        """
        Download a generated file.

        Args:
            url: Download URL from result
            output_path: Where to save the file

        Returns: Path to downloaded file
        """
        output_path = Path(output_path)

        # Handle both relative and absolute URLs
        if url.startswith("/"):
            url = f"{self.base_url}{url}"

        response = self._client.get(url)
        response.raise_for_status()

        output_path.write_bytes(response.content)
        return output_path


# ─────────────────────────────────────────────────────────────────────────────
# Async Client
# ─────────────────────────────────────────────────────────────────────────────


class AsyncClient:
    """
    Asynchronous client for Infinity Media Server.

    Mirrors fal_client.AsyncClient API.

    Usage:
        async with AsyncClient() as client:
            result = await client.run("black-forest-labs/flux-dev", {"prompt": "A cat"})

        # Use environment variable for server URL
        # export INFINITY_SERVER_URL=http://your-server:8000
        client = AsyncClient()  # Uses INFINITY_SERVER_URL or default
    """

    # Default server URL (can be overridden via INFINITY_SERVER_URL env var)
    DEFAULT_URL = os.environ.get("INFINITY_SERVER_URL", "http://192.222.55.191:8000")

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_timeout: float = 300.0,
    ):
        """
        Initialize the async client.

        Args:
            base_url: Server URL. If not provided, uses INFINITY_SERVER_URL env var
                      or falls back to the default demo server.
            default_timeout: Default timeout for run() in seconds
        """
        if base_url is None:
            base_url = self.DEFAULT_URL
        self.base_url = base_url.rstrip("/")
        self.default_timeout = default_timeout
        self._client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def run(
        self,
        application: str,
        arguments: AnyJSON,
        *,
        timeout: Optional[float] = None,
    ) -> AnyJSON:
        """Run an application and wait for result (async)."""
        timeout = timeout or self.default_timeout
        handle = await self.submit(application, arguments)

        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Job {handle.request_id} timed out after {timeout}s"
                )

            status = await handle.status()
            if isinstance(status, Completed):
                return await handle.get()
            elif isinstance(status, Failed):
                raise JobFailedError(handle.request_id, status.error)

            await asyncio.sleep(1.0)

    async def submit(
        self,
        application: str,
        arguments: AnyJSON,
    ) -> AsyncRequestHandle:
        """Submit a job (non-blocking, returns async handle)."""
        response = await self._client.post(
            f"{self.base_url}/{application}",
            json=arguments,
        )
        response.raise_for_status()
        data = response.json()

        return AsyncRequestHandle(
            client=self._client,
            base_url=self.base_url,
            application=application,
            request_id=data["request_id"],
        )

    async def subscribe(
        self,
        application: str,
        arguments: AnyJSON,
        *,
        on_enqueue: Optional[Callable[[str], None]] = None,
        on_queue_update: Optional[Callable[[Status], None]] = None,
    ) -> AnyJSON:
        """Submit and subscribe to status updates until complete."""
        handle = await self.submit(application, arguments)

        if on_enqueue:
            on_enqueue(handle.request_id)

        while True:
            status = await handle.status()
            if on_queue_update:
                on_queue_update(status)
            if isinstance(status, (Completed, Failed)):
                break
            await asyncio.sleep(0.5)

        return await handle.get()

    async def status(
        self,
        application: str,
        request_id: str,
        *,
        with_logs: bool = False,
    ) -> Status:
        """Get status of a request by ID."""
        response = await self._client.get(
            f"{self.base_url}/{application}/requests/{request_id}/status"
        )
        response.raise_for_status()
        return parse_status(response.json())

    async def result(
        self,
        application: str,
        request_id: str,
    ) -> AnyJSON:
        """Get result of a completed request."""
        response = await self._client.get(
            f"{self.base_url}/{application}/requests/{request_id}"
        )
        response.raise_for_status()
        return response.json()

    async def cancel(
        self,
        application: str,
        request_id: str,
    ) -> None:
        """Cancel a request (if supported by server)."""
        pass

    def get_handle(
        self,
        application: str,
        request_id: str,
    ) -> AsyncRequestHandle:
        """Get a handle to an existing request by ID."""
        return AsyncRequestHandle(
            client=self._client,
            base_url=self.base_url,
            application=application,
            request_id=request_id,
        )

    async def health(self) -> Dict[str, Any]:
        """Check server health."""
        response = await self._client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def ready(self) -> Dict[str, Any]:
        """Check server readiness and GPU status."""
        response = await self._client.get(f"{self.base_url}/ready")
        response.raise_for_status()
        return response.json()

    async def models(self) -> Dict[str, Any]:
        """List available models."""
        response = await self._client.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()


# ─────────────────────────────────────────────────────────────────────────────
# Legacy Alias (backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────

# InfinityClient is an alias for SyncClient
InfinityClient = SyncClient
