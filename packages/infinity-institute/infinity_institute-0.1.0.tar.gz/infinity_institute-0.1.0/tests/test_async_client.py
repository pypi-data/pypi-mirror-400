#!/usr/bin/env python3
"""
Test script for infinity_institute AsyncClient.

Validates all async client methods work correctly with real server.

Usage:
    # Run all tests
    python -m infinity_institute.tests.test_async_client

    # Run specific test
    python -m infinity_institute.tests.test_async_client --test image

    # Use custom server
    python -m infinity_institute.tests.test_async_client --server http://localhost:8000

Requirements:
    - Server must be running at the specified URL
    - Tests use small parameters for quick validation
"""

import sys
import asyncio
import argparse

# Add parent to path for local development
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from infinity_institute import (
    AsyncClient,
    run_async,
    submit_async,
    Queued,
    InProgress,
    Completed,
    AsyncRequestHandle,
)


async def test_health(client: AsyncClient) -> bool:
    """Test health endpoint."""
    print("  Testing health()...", end=" ")
    try:
        result = await client.health()
        assert result["status"] == "ok"
        print(f"✅ {result}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_ready(client: AsyncClient) -> bool:
    """Test ready endpoint."""
    print("  Testing ready()...", end=" ")
    try:
        result = await client.ready()
        assert "ready" in result or "gpu_available" in result
        print(f"✅ GPU: {result.get('gpu_name', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_models(client: AsyncClient) -> bool:
    """Test models endpoint."""
    print("  Testing models()...", end=" ")
    try:
        result = await client.models()
        assert "models" in result
        print(f"✅ Found {len(result['models'])} models")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_submit_and_wait(client: AsyncClient) -> bool:
    """Test submit() -> status() -> get() flow."""
    print("  Testing submit() + status() + get()...", end=" ", flush=True)
    try:
        # Submit job
        handle = await client.submit(
            "boson-ai/higgs-audio-v2", {"text": "Async hello test"}
        )
        assert isinstance(handle, AsyncRequestHandle)
        assert handle.request_id

        # Check status
        st = await handle.status()
        assert isinstance(st, (Queued, InProgress, Completed))

        # Wait for result
        result = await handle.get()
        assert "audio" in result

        print(f"✅ request_id={handle.request_id[:8]}...")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_subscribe(client: AsyncClient) -> bool:
    """Test subscribe() with callbacks."""
    print("  Testing subscribe()...", end=" ", flush=True)
    try:
        updates = []

        def on_update(st):
            updates.append(type(st).__name__)

        result = await client.subscribe(
            "boson-ai/higgs-audio-v2",
            {"text": "Async subscribe test"},
            on_queue_update=on_update,
        )

        assert "audio" in result
        print(f"✅ updates: {len(updates)}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_run(client: AsyncClient) -> bool:
    """Test run() async blocking call."""
    print("  Testing run()...", end=" ", flush=True)
    try:
        result = await client.run(
            "boson-ai/higgs-audio-v2",
            {"text": "Async run test"},
            timeout=120.0,
        )
        assert "audio" in result
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_concurrent_submits(client: AsyncClient) -> bool:
    """Test concurrent job submissions."""
    print("  Testing concurrent submits...", end=" ", flush=True)
    try:
        # Submit multiple jobs concurrently
        handles = await asyncio.gather(
            client.submit("boson-ai/higgs-audio-v2", {"text": "Concurrent 1"}),
            client.submit("boson-ai/higgs-audio-v2", {"text": "Concurrent 2"}),
        )

        assert len(handles) == 2
        assert all(h.request_id for h in handles)

        # Wait for all results
        results = await asyncio.gather(*[h.get() for h in handles])
        assert all("audio" in r for r in results)

        print(f"✅ completed {len(results)} concurrent jobs")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_module_run_async(server_url: str) -> bool:
    """Test module-level run_async()."""
    print("  Testing module-level run_async()...", end=" ", flush=True)
    try:
        from infinity_institute import _get_async_client

        client = _get_async_client()
        client.base_url = server_url

        result = await run_async(
            "boson-ai/higgs-audio-v2", {"text": "Module async test"}
        )
        assert "audio" in result
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


async def test_module_submit_async(server_url: str) -> bool:
    """Test module-level submit_async()."""
    print("  Testing module-level submit_async()...", end=" ", flush=True)
    try:
        from infinity_institute import _get_async_client

        client = _get_async_client()
        client.base_url = server_url

        handle = await submit_async(
            "boson-ai/higgs-audio-v2", {"text": "Module async submit"}
        )
        assert handle.request_id
        result = await handle.get()
        assert "audio" in result
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


# Test registry
TESTS = {
    "health": test_health,
    "ready": test_ready,
    "models": test_models,
    "submit": test_submit_and_wait,
    "subscribe": test_subscribe,
    "run": test_run,
    "concurrent": test_concurrent_submits,
}

MODULE_TESTS = {
    "module_run": test_module_run_async,
    "module_submit": test_module_submit_async,
}


async def run_tests(server_url: str, test_name: str):
    """Run the specified tests."""
    print(f"\n{'=' * 60}")
    print("infinity_institute AsyncClient Tests")
    print(f"Server: {server_url}")
    print(f"{'=' * 60}\n")

    async with AsyncClient(server_url) as client:
        passed = 0
        failed = 0

        # Quick tests (no generation)
        quick_tests = ["health", "ready", "models"]

        # Determine which tests to run
        if test_name == "all":
            tests_to_run = list(TESTS.keys())
            module_tests_to_run = list(MODULE_TESTS.keys())
        elif test_name == "quick":
            tests_to_run = quick_tests
            module_tests_to_run = []
        elif test_name in MODULE_TESTS:
            tests_to_run = []
            module_tests_to_run = [test_name]
        else:
            tests_to_run = [test_name]
            module_tests_to_run = []

        # Run client tests
        print("AsyncClient method tests:")
        for name in tests_to_run:
            if await TESTS[name](client):
                passed += 1
            else:
                failed += 1

        # Run module tests
        if module_tests_to_run:
            print("\nModule-level async function tests:")
            for name in module_tests_to_run:
                if await MODULE_TESTS[name](server_url):
                    passed += 1
                else:
                    failed += 1

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'=' * 60}\n")

        return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Test infinity_institute AsyncClient")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="Server URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--test",
        choices=list(TESTS.keys()) + list(MODULE_TESTS.keys()) + ["all", "quick"],
        default="quick",
        help="Which test to run (default: quick)",
    )
    args = parser.parse_args()

    success = asyncio.run(run_tests(args.server, args.test))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
