#!/usr/bin/env python3
"""
Test script for infinity_institute SyncClient.

Validates all sync client methods work correctly with real server.

Usage:
    # Run all tests
    python -m infinity_institute.tests.test_sync_client

    # Run specific test
    python -m infinity_institute.tests.test_sync_client --test image

    # Use custom server
    python -m infinity_institute.tests.test_sync_client --server http://localhost:8000

Requirements:
    - Server must be running at the specified URL
    - Tests use small parameters for quick validation
"""

import sys
import argparse

# Add parent to path for local development
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from infinity_institute import (
    SyncClient,
    run,
    submit,
    Queued,
    InProgress,
    Completed,
    Failed,
    ImageResult,
    VideoResult,
    AudioResult,
    SyncRequestHandle,
)


def test_health(client: SyncClient) -> bool:
    """Test health endpoint."""
    print("  Testing health()...", end=" ")
    try:
        result = client.health()
        assert result["status"] == "ok"
        print(f"✅ {result}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_ready(client: SyncClient) -> bool:
    """Test ready endpoint."""
    print("  Testing ready()...", end=" ")
    try:
        result = client.ready()
        assert "ready" in result or "gpu_available" in result
        print(f"✅ GPU: {result.get('gpu_name', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_models(client: SyncClient) -> bool:
    """Test models endpoint."""
    print("  Testing models()...", end=" ")
    try:
        result = client.models()
        assert "models" in result
        print(f"✅ Found {len(result['models'])} models")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_submit_and_wait(client: SyncClient) -> bool:
    """Test submit() -> status() -> wait() flow."""
    print("  Testing submit() + status() + wait()...", end=" ", flush=True)
    try:
        # Submit job
        handle = client.submit("boson-ai/higgs-audio-v2", {"text": "Hello test"})
        assert isinstance(handle, SyncRequestHandle)
        assert handle.request_id

        # Check status
        st = handle.status()
        assert isinstance(st, (Queued, InProgress, Completed))

        # Wait for result (use get() which blocks)
        result = handle.get()
        assert "audio" in result

        print(f"✅ request_id={handle.request_id[:8]}...")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_iter_events(client: SyncClient) -> bool:
    """Test iter_events() for status streaming."""
    print("  Testing iter_events()...", end=" ", flush=True)
    try:
        handle = client.submit("boson-ai/higgs-audio-v2", {"text": "Test events"})

        events = []
        for event in handle.iter_events(interval=1.0):
            events.append(type(event).__name__)
            if isinstance(event, (Completed, Failed)):
                break

        assert len(events) >= 1
        assert events[-1] == "Completed"
        print(f"✅ events: {' -> '.join(events)}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_subscribe(client: SyncClient) -> bool:
    """Test subscribe() with callbacks."""
    print("  Testing subscribe()...", end=" ", flush=True)
    try:
        updates = []

        def on_update(st):
            updates.append(type(st).__name__)

        result = client.subscribe(
            "boson-ai/higgs-audio-v2",
            {"text": "Subscribe test"},
            on_queue_update=on_update,
        )

        assert "audio" in result
        print(f"✅ updates: {len(updates)}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_run(client: SyncClient) -> bool:
    """Test run() blocking call."""
    print("  Testing run()...", end=" ", flush=True)
    try:
        result = client.run(
            "boson-ai/higgs-audio-v2",
            {"text": "Run test"},
            timeout=120.0,
        )
        assert "audio" in result
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_image_convenience(client: SyncClient) -> bool:
    """Test image() convenience method with typed result."""
    print("  Testing image()...", end=" ", flush=True)
    try:
        result = client.image(
            "A simple test image",
            model="black-forest-labs/flux-dev",
            width=512,
            height=512,
            num_inference_steps=4,
            seed=42,
        )
        assert isinstance(result, ImageResult)
        assert len(result.images) > 0
        assert result.images[0].download_url
        print(f"✅ {result.images[0].width}x{result.images[0].height}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_video_convenience(client: SyncClient) -> bool:
    """Test video() convenience method with typed result."""
    print("  Testing video()...", end=" ", flush=True)
    try:
        result = client.video(
            "A simple test video",
            model="wan-ai/wan2.2-t2v",
            width=480,
            height=320,
            num_frames=9,
            num_inference_steps=8,
            seed=42,
        )
        assert isinstance(result, VideoResult)
        assert result.video.download_url
        print(f"✅ duration={result.video.duration:.1f}s")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_audio_convenience(client: SyncClient) -> bool:
    """Test audio() convenience method with typed result."""
    print("  Testing audio()...", end=" ", flush=True)
    try:
        result = client.audio(
            "This is a test of the audio convenience method.",
            model="boson-ai/higgs-audio-v2",
        )
        assert isinstance(result, AudioResult)
        assert result.audio.download_url
        print(f"✅ duration={result.audio.duration:.1f}s")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_module_functions(server_url: str) -> bool:
    """Test module-level functions (run, submit, etc.)."""
    print("  Testing module-level run()...", end=" ", flush=True)
    try:
        # Module functions use a shared default client
        # We need to set the URL by creating a client first
        from infinity_institute import _get_client

        client = _get_client()
        client.base_url = server_url

        result = run("boson-ai/higgs-audio-v2", {"text": "Module test"})
        assert "audio" in result
        print("✅")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def test_module_submit(server_url: str) -> bool:
    """Test module-level submit()."""
    print("  Testing module-level submit()...", end=" ", flush=True)
    try:
        from infinity_institute import _get_client

        client = _get_client()
        client.base_url = server_url

        handle = submit("boson-ai/higgs-audio-v2", {"text": "Module submit test"})
        assert handle.request_id
        result = handle.get()
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
    "iter_events": test_iter_events,
    "subscribe": test_subscribe,
    "run": test_run,
    "image": test_image_convenience,
    "video": test_video_convenience,
    "audio": test_audio_convenience,
}

MODULE_TESTS = {
    "module_run": test_module_functions,
    "module_submit": test_module_submit,
}


def main():
    parser = argparse.ArgumentParser(description="Test infinity_institute SyncClient")
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

    print(f"\n{'=' * 60}")
    print("infinity_institute SyncClient Tests")
    print(f"Server: {args.server}")
    print(f"{'=' * 60}\n")

    client = SyncClient(args.server)

    passed = 0
    failed = 0

    # Quick tests (no generation)
    quick_tests = ["health", "ready", "models"]

    # Full tests
    if args.test == "all":
        tests_to_run = list(TESTS.keys())
        module_tests_to_run = list(MODULE_TESTS.keys())
    elif args.test == "quick":
        tests_to_run = quick_tests
        module_tests_to_run = []
    elif args.test in MODULE_TESTS:
        tests_to_run = []
        module_tests_to_run = [args.test]
    else:
        tests_to_run = [args.test]
        module_tests_to_run = []

    # Run client tests
    print("Client method tests:")
    for name in tests_to_run:
        if TESTS[name](client):
            passed += 1
        else:
            failed += 1

    # Run module tests
    if module_tests_to_run:
        print("\nModule-level function tests:")
        for name in module_tests_to_run:
            if MODULE_TESTS[name](args.server):
                passed += 1
            else:
                failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    client.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
