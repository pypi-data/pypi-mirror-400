#!/usr/bin/env python3
"""
Communication Test Harness (Python)

Tests Events, Actions, DataChannel, and MediaStream communication
between Python and Node.js hub-client implementations.

Matches npm communication-comprehensive-test.ts timing and structure.

Environment variables:
    DEVICE_ID: Device ID for PhyHub authentication
    ACCESS_KEY: Access key for PhyHub authentication
    PEER_TWIN_ID: Twin ID of the peer to communicate with
    PHYHUB_REGION: PhyHub region (eu, us, etc.)
    ROLE: 'initiator' or 'responder'

Usage:
    ROLE=initiator python tests/test_communication.py
    ROLE=responder python tests/test_communication.py
"""

import asyncio
import os
import sys
import time
from typing import Any, Optional

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from phystack.hub_client import PhyHubClient, TwinMessageResult, TwinMessageResultStatus


# Constants matching npm test
MESSAGES_PER_TEST = 3


# ANSI colors for output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def log(msg: str) -> None:
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def log_info(msg: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")


def log_success(msg: str) -> None:
    print(f"{Colors.GREEN}[PASS]{Colors.NC} {msg}")


def log_error(msg: str) -> None:
    print(f"{Colors.RED}[FAIL]{Colors.NC} {msg}")


def log_warn(msg: str) -> None:
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}")


class TestResults:
    """Track test results."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.tests: list[tuple[str, bool, str, int]] = []

    def record(self, name: str, passed: bool, details: str, start_time: float) -> None:
        duration = int((time.time() - start_time) * 1000)
        self.tests.append((name, passed, details, duration))
        if passed:
            self.passed += 1
            status = f"{Colors.GREEN}PASS{Colors.NC}"
        else:
            self.failed += 1
            status = f"{Colors.RED}FAIL{Colors.NC}"
        log(f"[{status}] {name}: {details} ({duration}ms)")

    def summary(self) -> None:
        print("")
        print("=" * 65)
        print("TEST SUMMARY")
        print("=" * 65)
        print(f"{'Test':<40}{'Status':<10}Time")
        print("-" * 65)
        for name, passed, details, duration in self.tests:
            status = f"{Colors.GREEN}PASS{Colors.NC}" if passed else f"{Colors.RED}FAIL{Colors.NC}"
            print(f"{name:<40}{status:<15}{duration}ms")
        print("-" * 65)
        total_time = sum(d for _, _, _, d in self.tests)
        print(f"Total: {self.passed} passed, {self.failed} failed ({total_time}ms)")
        print("=" * 65)


# =============================================================================
# Test 1: Events (Fire-and-Forget via Hub)
# =============================================================================
async def test_events(
    client: PhyHubClient,
    instance: Any,
    peer_twin_id: str,
    is_initiator: bool,
    results: TestResults,
) -> None:
    test_name = "Events (Hub-based)"
    start_time = time.time()
    log(f"\n=== Test 1: {test_name} ===")

    try:
        received_count = 0

        await client.subscribe_twin(peer_twin_id)
        log(f"Subscribed to peer twin: {peer_twin_id}")

        def on_event(data: Any, respond: Optional[Any] = None) -> None:
            nonlocal received_count
            received_count += 1
            log(f"[EVENT RECEIVED] {data}")

        instance.on("test-event", on_event)

        if is_initiator:
            # Wait for responder to be ready
            log("Waiting for responder to set up listeners...")
            await asyncio.sleep(3)

            # Send test events to peer
            log("Sending test events...")
            for i in range(MESSAGES_PER_TEST):
                event_data = {"type": "test", "count": i + 1, "timestamp": time.time()}
                log(f"[SENDING EVENT] {event_data}")
                instance.to(peer_twin_id).emit("test-event", event_data)
                await asyncio.sleep(0.5)

            # Wait for responses/echoes
            await asyncio.sleep(5)

            passed = received_count >= MESSAGES_PER_TEST
            results.record(test_name, passed, f"Sent {MESSAGES_PER_TEST}, received echoes: {received_count}", start_time)
        else:
            # Responder: Listen for events and echo them back
            log("Waiting for events from initiator...")

            def on_event_echo(data: Any, respond: Optional[Any] = None) -> None:
                echo_data = {**data, "echo": True, "echoedAt": int(time.time() * 1000)}
                log(f"[ECHOING EVENT] {echo_data}")
                instance.to(peer_twin_id).emit("test-event", echo_data)

            instance.on("test-event", on_event_echo)

            # Wait for test to complete
            await asyncio.sleep(10)

            passed = received_count >= MESSAGES_PER_TEST
            results.record(test_name, passed, f"Received {received_count} events from initiator", start_time)

    except Exception as e:
        results.record(test_name, False, str(e), start_time)


# =============================================================================
# Test 2: Actions (Request-Response via Hub)
# =============================================================================
async def test_actions(
    client: PhyHubClient,
    instance: Any,
    peer_twin_id: str,
    is_initiator: bool,
    results: TestResults,
) -> None:
    test_name = "Actions (Hub-based)"
    start_time = time.time()
    log(f"\n=== Test 2: {test_name} ===")

    try:
        successful_actions = 0
        failed_actions = 0

        if is_initiator:
            # Wait for responder to set up action handlers
            log("Waiting for responder to set up action handlers...")
            await asyncio.sleep(3)

            log("Testing instance.to(peerTwinId).emit() with callback (action pattern)...")
            for i in range(MESSAGES_PER_TEST):
                action_payload = {"command": "process", "value": i * 10, "timestamp": time.time()}
                log(f"[SENDING ACTION {i + 1}] test-action: {action_payload}")

                action_done = asyncio.Event()
                action_result: Optional[TwinMessageResult] = None

                def on_result(result: TwinMessageResult) -> None:
                    nonlocal action_result
                    action_result = result
                    action_done.set()
                    log(f"[ACTION RESPONSE] {result.status.value} - {result.message}")

                instance.to(peer_twin_id).emit("test-action", action_payload, callback=on_result)

                try:
                    await asyncio.wait_for(action_done.wait(), timeout=10.0)
                    if action_result and action_result.status == TwinMessageResultStatus.SUCCESS:
                        successful_actions += 1
                    else:
                        failed_actions += 1
                except asyncio.TimeoutError:
                    log(f"[ACTION ERROR] Timeout")
                    failed_actions += 1

                await asyncio.sleep(0.5)

            passed = successful_actions >= MESSAGES_PER_TEST
            results.record(test_name, passed, f"Success: {successful_actions}, Failed: {failed_actions}", start_time)
        else:
            # Responder: Handle requests
            log("Setting up request handlers via instance.on()...")

            def on_action(data: Any, respond: Optional[Any] = None) -> None:
                log(f"[REQUEST RECEIVED] {data}")
                if respond:
                    respond(TwinMessageResult(
                        status=TwinMessageResultStatus.SUCCESS,
                        message="Request processed successfully",
                    ))

            instance.on("test-action", on_action)

            # Wait for test to complete
            await asyncio.sleep(15)

            results.record(test_name, True, "Request handler registered and responded", start_time)

    except Exception as e:
        results.record(test_name, False, str(e), start_time)


# =============================================================================
# Test 3: DataChannel Default (Unnamed)
# =============================================================================
async def test_datachannel_default(
    client: PhyHubClient,
    peer_twin_id: str,
    is_initiator: bool,
    results: TestResults,
) -> None:
    test_name = "DataChannel Default (P2P)"
    start_time = time.time()
    log(f"\n=== Test 3: {test_name} ===")

    try:
        received_count = 0

        if is_initiator:
            channel = await client.create_data_channel(peer_twin_id, is_initiator=True)
            log(f"Created default channel. Name: {channel.channel_name}")

            if channel.channel_name != "default":
                raise Exception(f"Expected channel name 'default', got '{channel.channel_name}'")

            def on_message(data: Any) -> None:
                nonlocal received_count
                received_count += 1
                log(f"[DC RECEIVED] {data}")

            channel.on_message(on_message)

            await asyncio.sleep(2)

            for i in range(MESSAGES_PER_TEST):
                msg = {"test": "default", "num": i, "timestamp": time.time()}
                log(f"[DC SENDING] {msg}")
                channel.send(msg)
                await asyncio.sleep(0.3)

            await asyncio.sleep(3)

            passed = received_count >= MESSAGES_PER_TEST
            results.record(test_name, passed, f"Sent {MESSAGES_PER_TEST}, received echoes: {received_count}", start_time)

            channel.close()
        else:
            # Responder: wait for channel
            channel_received = asyncio.Event()
            channel_holder: list = []

            dc = await client.create_data_channel(peer_twin_id, is_initiator=False, blocking=False)

            def on_message(data: Any) -> None:
                nonlocal received_count
                received_count += 1
                log(f"[DC RECEIVED] {data}")
                dc.send({"echo": data})

            dc.on_message(on_message)

            # Wait for connection
            timeout = 30.0
            start = time.time()
            while time.time() - start < timeout:
                if dc.is_open():
                    log(f"Received default channel. Name: {dc.channel_name}")
                    break
                await asyncio.sleep(0.5)
            else:
                raise Exception("Timeout waiting for channel")

            # Wait for test to complete
            await asyncio.sleep(8)

            passed = received_count >= MESSAGES_PER_TEST
            results.record(test_name, passed, f"Received {received_count} messages", start_time)

    except Exception as e:
        results.record(test_name, False, str(e), start_time)


# =============================================================================
# Test 4: DataChannel Named Channels
# =============================================================================
async def test_datachannel_named(
    client: PhyHubClient,
    peer_twin_id: str,
    is_initiator: bool,
    results: TestResults,
) -> None:
    test_name = "DataChannel Named (P2P)"
    start_time = time.time()
    log(f"\n=== Test 4: {test_name} ===")

    channel_names = ["control", "data"]
    received_by_channel: dict[str, int] = {name: 0 for name in channel_names}

    try:
        if is_initiator:
            channels = []

            for name in channel_names:
                ch = await client.create_data_channel(peer_twin_id, is_initiator=True, channel_name=name)
                log(f"Created channel '{name}'. Reported name: {ch.channel_name}")

                if ch.channel_name != name:
                    raise Exception(f"Expected channel name '{name}', got '{ch.channel_name}'")

                def make_handler(channel_name: str):
                    def handler(data: Any) -> None:
                        received_by_channel[channel_name] += 1
                    return handler

                ch.on_message(make_handler(name))
                channels.append(ch)

            await asyncio.sleep(3)

            for i, ch in enumerate(channels):
                for j in range(MESSAGES_PER_TEST):
                    ch.send({"channel": channel_names[i], "num": j})
                    await asyncio.sleep(0.1)

            await asyncio.sleep(3)

            all_passed = all(received_by_channel.get(name, 0) >= MESSAGES_PER_TEST for name in channel_names)
            details = ", ".join(f"{n}:{received_by_channel.get(n, 0)}" for n in channel_names)
            results.record(test_name, all_passed, details, start_time)

            for ch in channels:
                ch.close()
        else:
            # Responder: wait for named channels
            async def wait_for_channel(name: str) -> None:
                dc = await client.create_data_channel(peer_twin_id, is_initiator=False, channel_name=name, blocking=False)
                log(f"Waiting for channel '{name}'...")

                def on_message(data: Any) -> None:
                    received_by_channel[name] += 1
                    log(f"[DC {name} RECEIVED] {data}")
                    dc.send({"echo": data})

                dc.on_message(on_message)

                # Wait for connection
                timeout = 30.0
                start = time.time()
                while time.time() - start < timeout:
                    if dc.is_open():
                        log(f"Received channel '{name}'. Reported: {dc.channel_name}")
                        break
                    await asyncio.sleep(0.5)

                await asyncio.sleep(10)

            await asyncio.gather(*[wait_for_channel(name) for name in channel_names])

            all_passed = all(received_by_channel.get(name, 0) >= MESSAGES_PER_TEST for name in channel_names)
            details = ", ".join(f"{n}:{received_by_channel.get(n, 0)}" for n in channel_names)
            results.record(test_name, all_passed, details, start_time)

    except Exception as e:
        results.record(test_name, False, str(e), start_time)


# =============================================================================
# Test 5: MediaStream Connection
# =============================================================================
async def test_mediastream(
    client: PhyHubClient,
    peer_twin_id: str,
    is_initiator: bool,
    results: TestResults,
) -> None:
    test_name = "MediaStream (P2P)"
    start_time = time.time()
    log(f"\n=== Test 5: {test_name} ===")

    try:
        if is_initiator:
            stream = await client.create_media_stream(peer_twin_id, is_initiator=True)
            log(f"MediaStream created. Target: {stream.target_twin_id}, Channel: {stream.stream_name}")

            if stream.stream_name != "default":
                raise Exception(f"Expected channel name 'default', got '{stream.stream_name}'")

            def on_track(track: Any) -> None:
                log(f"Received track: {track.kind}")

            stream.on_track(on_track)

            await asyncio.sleep(5)

            results.record(test_name, True, f"Connected to {stream.target_twin_id}", start_time)
            stream.close()
        else:
            # Responder: wait for stream
            stream = await client.create_media_stream(peer_twin_id, is_initiator=False, blocking=False)
            log(f"Waiting for MediaStream...")

            def on_track(track: Any) -> None:
                log(f"Track received: {track.kind}")

            stream.on_track(on_track)

            # Wait for connection
            timeout = 30.0
            start = time.time()
            while time.time() - start < timeout:
                if stream.is_open():
                    log(f"MediaStream received. Channel: {stream.stream_name}")
                    break
                await asyncio.sleep(0.5)

            await asyncio.sleep(5)

            results.record(test_name, True, f"Connected from {stream.target_twin_id}", start_time)

    except Exception as e:
        results.record(test_name, False, str(e), start_time)


# =============================================================================
# Main
# =============================================================================
async def main() -> None:
    """Main entry point."""
    print("=" * 65)
    print("  Communication Comprehensive Test Suite")
    print("  Hub-based: Events, Actions | P2P: DataChannels, MediaStreams")
    print("=" * 65)

    role = os.environ.get("ROLE", "initiator").lower()
    peer_twin_id = os.environ.get("PEER_TWIN_ID")

    if not peer_twin_id:
        print("ERROR: Set PEER_TWIN_ID")
        sys.exit(1)

    if role not in ("initiator", "responder"):
        print("ERROR: Set ROLE to initiator or responder")
        sys.exit(1)

    is_initiator = role == "initiator"
    log(f"Role: {role}")
    log(f"Peer Twin ID: {peer_twin_id}")

    results = TestResults()

    try:
        log("\nConnecting to PhyHub...")
        async with PhyHubClient.from_env() as client:
            log("Connected!")

            instance = await client.get_instance()
            if not instance:
                print("ERROR: Failed to get instance")
                sys.exit(1)

            log(f"Instance ID: {instance.id}\n")

            # Run tests sequentially like npm
            # Note: npm responder uses fixed sleep times that we must wait for:
            # - Events responder: 10s sleep
            # - Actions responder: 15s sleep
            # - DataChannel responder: 8s after receiving data
            # - DataChannel Named responder: 10s per channel after receiving data

            await test_events(client, instance, peer_twin_id, is_initiator, results)
            # Events test takes ~10s for both sides, just need inter-test gap
            await asyncio.sleep(2)

            await test_actions(client, instance, peer_twin_id, is_initiator, results)
            # If initiator: Actions took ~6s, but responder waits 15s total. Wait ~9s more.
            if is_initiator:
                await asyncio.sleep(9)
            else:
                await asyncio.sleep(2)

            await test_datachannel_default(client, peer_twin_id, is_initiator, results)
            # If initiator: DataChannel took ~6s, responder waits 8s after data. Wait ~4s more.
            if is_initiator:
                await asyncio.sleep(4)
            else:
                await asyncio.sleep(2)

            await test_datachannel_named(client, peer_twin_id, is_initiator, results)
            # If initiator: Named took ~7s, responder waits 10s per channel + 2s gap.
            # Need more time for npm to finish cleanup and register MediaStream handler.
            if is_initiator:
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(2)

            await test_mediastream(client, peer_twin_id, is_initiator, results)

    except Exception as e:
        log(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()

    results.summary()

    # Give time for final cleanup
    await asyncio.sleep(1)

    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
