"""
infinity_institute: Python client for GPU-accelerated media generation.

Mirrors fal_client's API design:

    from infinity_institute import run, submit, status, result

    # Simple usage (blocking)
    result = run("black-forest-labs/flux-dev", {"prompt": "A cat astronaut"})

    # Or use the client classes
    from infinity_institute import SyncClient, AsyncClient

    client = SyncClient()
    handle = client.submit("black-forest-labs/flux-dev", {"prompt": "A cat"})
    for event in handle.iter_events():
        print(event)
    result = handle.get()
"""

from .client import (
    SyncClient,
    AsyncClient,
    InfinityClient,  # Legacy alias for SyncClient
    SyncRequestHandle,
    AsyncRequestHandle,
    InfinityClientError,
    JobFailedError,
    TimeoutError,
)

from .models import (
    Status,
    Queued,
    InProgress,
    Completed,
    Failed,
    ImageResult,
    VideoResult,
    AudioResult,
    GenerationResult,
    AnyJSON,
)

import os

__version__ = "0.1.0"

# Default server URL (can be overridden via INFINITY_SERVER_URL env var)
DEFAULT_URL = os.environ.get("INFINITY_SERVER_URL", "http://192.222.55.191:8000")

# ─────────────────────────────────────────────────────────────────────────────
# Module-level convenience functions (mirrors fal_client)
# ─────────────────────────────────────────────────────────────────────────────

# Shared default client (lazily initialized)
_default_client: "SyncClient | None" = None
_default_async_client: "AsyncClient | None" = None


def _get_client() -> SyncClient:
    """Get or create the default sync client."""
    global _default_client
    if _default_client is None:
        _default_client = SyncClient()
    return _default_client


def _get_async_client() -> AsyncClient:
    """Get or create the default async client."""
    global _default_async_client
    if _default_async_client is None:
        _default_async_client = AsyncClient()
    return _default_async_client


def run(
    application: str,
    arguments: dict,
    *,
    timeout: float | None = None,
) -> dict:
    """
    Run an application with the given arguments (blocking).

    Args:
        application: Model name (e.g., "black-forest-labs/flux-dev")
        arguments: Model parameters as dict (e.g., {"prompt": "A cat"})
        timeout: Max seconds to wait

    Returns: Raw JSON response dict

    Example:
        result = run("black-forest-labs/flux-dev", {"prompt": "A cat"})
        print(result["images"][0]["download_url"])
    """
    return _get_client().run(application, arguments, timeout=timeout)


def submit(
    application: str,
    arguments: dict,
) -> SyncRequestHandle:
    """
    Submit a job (non-blocking).

    Args:
        application: Model name (e.g., "black-forest-labs/flux-dev")
        arguments: Model parameters as dict

    Returns: SyncRequestHandle for polling status and getting result

    Example:
        handle = submit("black-forest-labs/flux-dev", {"prompt": "A cat"})
        print(handle.request_id)
        result = handle.get()  # Blocks until complete
    """
    return _get_client().submit(application, arguments)


def subscribe(
    application: str,
    arguments: dict,
    *,
    on_enqueue=None,
    on_queue_update=None,
) -> dict:
    """
    Submit and subscribe to status updates until complete.

    Args:
        application: Model name
        arguments: Model parameters
        on_enqueue: Callback when job is enqueued (receives request_id)
        on_queue_update: Callback on each status update

    Returns: Raw JSON response dict
    """
    return _get_client().subscribe(
        application,
        arguments,
        on_enqueue=on_enqueue,
        on_queue_update=on_queue_update,
    )


def status(
    application: str,
    request_id: str,
    *,
    with_logs: bool = False,
) -> Status:
    """
    Get status of a request by ID.

    Returns: Queued, InProgress, Completed, or Failed
    """
    return _get_client().status(application, request_id, with_logs=with_logs)


def result(
    application: str,
    request_id: str,
) -> dict:
    """
    Get result of a completed request.

    Returns: Raw JSON response dict
    """
    return _get_client().result(application, request_id)


def cancel(
    application: str,
    request_id: str,
) -> None:
    """Cancel a request (if supported by server)."""
    return _get_client().cancel(application, request_id)


# ─────────────────────────────────────────────────────────────────────────────
# Async module-level functions
# ─────────────────────────────────────────────────────────────────────────────


async def run_async(
    application: str,
    arguments: dict,
    *,
    timeout: float | None = None,
) -> dict:
    """Async version of run()."""
    return await _get_async_client().run(application, arguments, timeout=timeout)


async def submit_async(
    application: str,
    arguments: dict,
) -> AsyncRequestHandle:
    """Async version of submit()."""
    return await _get_async_client().submit(application, arguments)


async def subscribe_async(
    application: str,
    arguments: dict,
    *,
    on_enqueue=None,
    on_queue_update=None,
) -> dict:
    """Async version of subscribe()."""
    return await _get_async_client().subscribe(
        application,
        arguments,
        on_enqueue=on_enqueue,
        on_queue_update=on_queue_update,
    )


async def status_async(
    application: str,
    request_id: str,
    *,
    with_logs: bool = False,
) -> Status:
    """Async version of status()."""
    return await _get_async_client().status(
        application, request_id, with_logs=with_logs
    )


async def result_async(
    application: str,
    request_id: str,
) -> dict:
    """Async version of result()."""
    return await _get_async_client().result(application, request_id)


async def cancel_async(
    application: str,
    request_id: str,
) -> None:
    """Async version of cancel()."""
    return await _get_async_client().cancel(application, request_id)


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Client classes
    "SyncClient",
    "AsyncClient",
    "InfinityClient",  # Legacy alias
    # Request handles
    "SyncRequestHandle",
    "AsyncRequestHandle",
    # Status types
    "Status",
    "Queued",
    "InProgress",
    "Completed",
    "Failed",
    # Result types
    "ImageResult",
    "VideoResult",
    "AudioResult",
    "GenerationResult",
    "AnyJSON",
    # Exceptions
    "InfinityClientError",
    "JobFailedError",
    "TimeoutError",
    # Module-level functions (sync)
    "run",
    "submit",
    "subscribe",
    "status",
    "result",
    "cancel",
    # Module-level functions (async)
    "run_async",
    "submit_async",
    "subscribe_async",
    "status_async",
    "result_async",
    "cancel_async",
]
