#!/usr/bin/env python3
"""
Python Backend for Browser Test App

This script acts as the initiator for testing with the browser-based responder.
It runs tests for Events, Actions, DataChannel, and MediaStream.

Environment variables:
    DEVICE_ID: Device ID for PhyHub authentication
    ACCESS_KEY: Access key for PhyHub authentication
    PEER_TWIN_ID: Twin ID of the browser responder
    PHYHUB_REGION: PhyHub region (eu, us, etc.)

Usage:
    python examples/browser_test_backend.py
"""

import asyncio
import os
import sys
import time
from typing import Any, Optional

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from phystack.hub_client import PhyHubClient, TwinMessageResult, TwinMessageResultStatus


# ANSI colors
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    NC = "\033[0m"


def log_info(msg: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")


def log_success(msg: str) -> None:
    print(f"{Colors.GREEN}[PASS]{Colors.NC} {msg}")


def log_error(msg: str) -> None:
    print(f"{Colors.RED}[FAIL]{Colors.NC} {msg}")


def log_warn(msg: str) -> None:
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}")


def log_test(name: str, status: str) -> None:
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.NC} {name}")


class BrowserTestRunner:
    """Runs tests against the browser responder."""

    def __init__(self, client: PhyHubClient, peer_twin_id: str) -> None:
        self.client = client
        self.peer_twin_id = peer_twin_id
        self.results: dict[str, str] = {}

    async def run_all_tests(self) -> None:
        """Run all tests."""
        print("")
        print(f"{Colors.CYAN}=" * 50)
        print("Python Backend - Browser Test Initiator")
        print("=" * 50 + f"{Colors.NC}")
        print(f"  Peer Twin ID: {self.peer_twin_id}")
        print("")

        instance = await self.client.get_instance()
        if not instance:
            log_error("Failed to get instance")
            return

        await self.client.subscribe_twin(self.peer_twin_id)
        log_info(f"Subscribed to browser responder: {self.peer_twin_id}")

        # Give browser time to set up listeners
        log_info("Waiting for browser responder to be ready...")
        await asyncio.sleep(3)

        # Run tests
        await self.test_events(instance)
        await asyncio.sleep(1)

        await self.test_actions(instance)
        await asyncio.sleep(1)

        await self.test_datachannel()
        await asyncio.sleep(1)

        await self.test_mediastream()

        # Print summary
        self.print_summary()

    async def test_events(self, instance: Any) -> None:
        """Test events."""
        log_info("Testing Events...")
        test_name = "Events"

        echo_received = asyncio.Event()
        echo_count = 0
        expected_count = 3

        def on_echo(data: Any, respond: Optional[Any] = None) -> None:
            nonlocal echo_count
            echo_count += 1
            log_info(f"  Received echo {data.get('count', '?')}")
            if echo_count >= expected_count:
                echo_received.set()

        instance.on("test-event-echo", on_echo)

        # Send events
        for i in range(1, expected_count + 1):
            instance.to(self.peer_twin_id).emit("test-event", {
                "count": i,
                "timestamp": int(time.time() * 1000),
            })
            log_info(f"  Sent event {i}")
            await asyncio.sleep(0.2)

        try:
            await asyncio.wait_for(echo_received.wait(), timeout=10.0)
            self.results[test_name] = "PASS"
            log_test(test_name, "PASS")
        except asyncio.TimeoutError:
            self.results[test_name] = f"PARTIAL ({echo_count}/{expected_count})"
            log_test(test_name, "PARTIAL")

    async def test_actions(self, instance: Any) -> None:
        """Test actions (request-response)."""
        log_info("Testing Actions...")
        test_name = "Actions"

        response_received = asyncio.Event()
        response_count = 0
        expected_count = 3

        def on_response(result: TwinMessageResult) -> None:
            nonlocal response_count
            response_count += 1
            log_info(f"  Received action response: {result.status.value} - {result.message}")
            if response_count >= expected_count:
                response_received.set()

        # Send actions
        for i in range(1, expected_count + 1):
            instance.to(self.peer_twin_id).emit(
                "test-action",
                {"count": i},
                callback=on_response,
            )
            log_info(f"  Sent action {i}")
            await asyncio.sleep(0.3)

        try:
            await asyncio.wait_for(response_received.wait(), timeout=10.0)
            self.results[test_name] = "PASS"
            log_test(test_name, "PASS")
        except asyncio.TimeoutError:
            self.results[test_name] = f"PARTIAL ({response_count}/{expected_count})"
            log_test(test_name, "PARTIAL")

    async def test_datachannel(self) -> None:
        """Test DataChannel."""
        log_info("Testing DataChannel...")
        test_name = "DataChannel"

        echo_received = asyncio.Event()
        echo_count = 0
        expected_count = 3

        try:
            dc = await self.client.create_data_channel(self.peer_twin_id, is_initiator=True)
            log_info(f"  DataChannel connected: {dc.is_open()}")

            def on_message(data: Any) -> None:
                nonlocal echo_count
                echo_count += 1
                log_info(f"  Received echo: {data}")
                if echo_count >= expected_count:
                    echo_received.set()

            dc.on_message(on_message)

            # Send messages
            for i in range(1, expected_count + 1):
                dc.send({"type": "test", "messageNum": i})
                log_info(f"  Sent message {i}")
                await asyncio.sleep(0.2)

            try:
                await asyncio.wait_for(echo_received.wait(), timeout=10.0)
                self.results[test_name] = "PASS"
                log_test(test_name, "PASS")
            except asyncio.TimeoutError:
                self.results[test_name] = f"PARTIAL ({echo_count}/{expected_count})"
                log_test(test_name, "PARTIAL")

            dc.close()

        except Exception as e:
            log_error(f"  DataChannel error: {e}")
            self.results[test_name] = "FAIL"
            log_test(test_name, "FAIL")

    async def test_mediastream(self) -> None:
        """Test MediaStream with webcam."""
        log_info("Testing MediaStream (webcam)...")
        test_name = "MediaStream"

        try:
            stream = await self.client.create_media_stream(self.peer_twin_id, is_initiator=True)
            log_info(f"  MediaStream connected: {stream.is_open()}")

            # Check if we have a video track
            has_video = stream.video_track is not None
            log_info(f"  Has local video track: {has_video}")

            if stream.is_open():
                log_info("  Streaming video to browser for 5 seconds...")
                await asyncio.sleep(5)
                self.results[test_name] = "PASS"
                log_test(test_name, "PASS")
            else:
                self.results[test_name] = "FAIL"
                log_test(test_name, "FAIL")

            stream.close()

        except Exception as e:
            log_error(f"  MediaStream error: {e}")
            self.results[test_name] = "FAIL"
            log_test(test_name, "FAIL")

    def print_summary(self) -> None:
        """Print test summary."""
        print("")
        print(f"{Colors.CYAN}=" * 50)
        print("Test Summary")
        print("=" * 50 + f"{Colors.NC}")

        passed = 0
        failed = 0

        for name, status in self.results.items():
            if "PASS" in status:
                passed += 1
                color = Colors.GREEN
            elif "FAIL" in status:
                failed += 1
                color = Colors.RED
            else:
                color = Colors.YELLOW
            print(f"  {color}{status:12}{Colors.NC} {name}")

        print("-" * 50)
        total = passed + failed
        print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
        print("=" * 50)


async def run_interactive() -> None:
    """Run in interactive mode with menu."""
    peer_twin_id = os.environ.get("PEER_TWIN_ID")

    if not peer_twin_id:
        log_error("PEER_TWIN_ID environment variable is required")
        print("")
        print("Usage:")
        print("  export DEVICE_ID=your-device-id")
        print("  export ACCESS_KEY=your-access-key")
        print("  export PEER_TWIN_ID=browser-responder-twin-id")
        print("  export PHYHUB_REGION=eu")
        print("  python examples/browser_test_backend.py")
        sys.exit(1)

    print("")
    print(f"{Colors.MAGENTA}=" * 50)
    print("Python Hub Client - Browser Test Backend")
    print("=" * 50 + f"{Colors.NC}")
    print("")
    print("This script acts as the initiator for testing with")
    print("the browser-based WebRTC test app (responder).")
    print("")
    print("Make sure the browser app is:")
    print("  1. Connected to PhyHub")
    print("  2. On the Responder page")
    print("  3. Subscribed to this device's twin")
    print("")

    try:
        async with PhyHubClient.from_env() as client:
            log_success(f"Connected to PhyHub")

            instance = await client.get_instance()
            if instance:
                log_info(f"Twin ID: {instance.id}")

            runner = BrowserTestRunner(client, peer_twin_id)
            await runner.run_all_tests()

    except KeyboardInterrupt:
        print("")
        log_info("Interrupted by user")
    except Exception as e:
        log_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def run_continuous() -> None:
    """Run continuously, keeping connection alive."""
    peer_twin_id = os.environ.get("PEER_TWIN_ID")

    if not peer_twin_id:
        log_error("PEER_TWIN_ID environment variable is required")
        sys.exit(1)

    print("")
    print(f"{Colors.MAGENTA}=" * 50)
    print("Python Hub Client - Continuous Mode")
    print("=" * 50 + f"{Colors.NC}")
    print("")

    try:
        async with PhyHubClient.from_env() as client:
            log_success("Connected to PhyHub")

            instance = await client.get_instance()
            if instance:
                log_info(f"Twin ID: {instance.id}")

            await client.subscribe_twin(peer_twin_id)
            log_info(f"Subscribed to: {peer_twin_id}")

            print("")
            print("Commands:")
            print("  e - Send event")
            print("  a - Send action")
            print("  d - Open DataChannel")
            print("  m - Start MediaStream")
            print("  t - Run all tests")
            print("  q - Quit")
            print("")

            while True:
                try:
                    cmd = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: input(f"{Colors.CYAN}>{Colors.NC} ").strip().lower()
                    )

                    if cmd == "q":
                        break
                    elif cmd == "e":
                        if instance:
                            instance.to(peer_twin_id).emit("test-event", {
                                "count": 1,
                                "timestamp": int(time.time() * 1000),
                            })
                            log_info("Sent event")
                    elif cmd == "a":
                        if instance:
                            def cb(r: TwinMessageResult) -> None:
                                log_info(f"Response: {r.status.value} - {r.message}")
                            instance.to(peer_twin_id).emit("test-action", {"count": 1}, callback=cb)
                            log_info("Sent action")
                    elif cmd == "d":
                        dc = await client.create_data_channel(peer_twin_id, is_initiator=True)
                        log_info(f"DataChannel open: {dc.is_open()}")
                        dc.send({"type": "test", "messageNum": 1})
                        log_info("Sent DataChannel message")
                    elif cmd == "m":
                        stream = await client.create_media_stream(peer_twin_id, is_initiator=True)
                        log_info(f"MediaStream open: {stream.is_open()}")
                        log_info("Streaming for 10 seconds...")
                        await asyncio.sleep(10)
                        stream.close()
                        log_info("MediaStream closed")
                    elif cmd == "t":
                        runner = BrowserTestRunner(client, peer_twin_id)
                        await runner.run_all_tests()

                except Exception as e:
                    log_error(f"Error: {e}")

    except KeyboardInterrupt:
        print("")
        log_info("Interrupted by user")


def main() -> None:
    """Main entry point."""
    mode = os.environ.get("MODE", "test")

    if mode == "continuous":
        asyncio.run(run_continuous())
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
