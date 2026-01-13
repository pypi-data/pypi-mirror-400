# Phystack Hub Client (Python)

Python client for PhyHub that provides:
- Events and Actions via twin messaging
- WebRTC DataChannel for P2P data
- WebRTC MediaStream for P2P video/audio (with webcam support)

## Installation

```bash
pip install phystack-hub-client
```

Or install from source:

```bash
pip install -e .
```

## Usage

### Basic Connection

```python
import asyncio
from phystack.hub_client import PhyHubClient

async def main():
    # Create client from environment variables
    async with PhyHubClient.from_env() as client:
        instance = await client.get_instance()
        print(f"Connected as twin: {instance.id}")

asyncio.run(main())
```

### Environment Variables

- `DEVICE_ID` or `PHYGRID_DEVICE_ID`: Device identifier
- `ACCESS_KEY` or `PHYGRID_DEVICE_KEY`: Access key
- `PHYHUB_URL` or `PHYHUB_REGION`: Server URL or region (eu, us, etc.)
- `TWIN_ID` or `INSTANCE_ID`: Optional specific twin ID

### Events

```python
# Listen for events
instance.on("my-event", lambda data, respond: print(f"Received: {data}"))

# Send events to a peer
instance.to(peer_twin_id).emit("my-event", {"message": "hello"})
```

### Actions (Request-Response)

```python
def on_result(result):
    print(f"Response: {result.status} - {result.message}")

# Send action with callback
instance.to(peer_twin_id).emit("my-action", {"command": "process"}, callback=on_result)

# Handle actions
def handle_action(data, respond):
    if respond:
        respond(TwinMessageResult(
            status=TwinMessageResultStatus.SUCCESS,
            message="Processed",
            data={"result": "done"}
        ))

instance.on("my-action", handle_action)
```

### WebRTC DataChannel

```python
# Create DataChannel connection
dc = await client.create_data_channel(peer_twin_id, is_initiator=True)

# Send data
dc.send({"message": "hello via WebRTC"})

# Receive data
dc.on_message(lambda data: print(f"Received: {data}"))

# Close when done
dc.close()
```

### WebRTC MediaStream (with Webcam)

```python
# Create MediaStream connection (streams from webcam)
stream = await client.create_media_stream(peer_twin_id, is_initiator=True)

# Check if streaming
print(f"Streaming: {stream.is_open()}")
print(f"Has video: {stream.video_track is not None}")

# Close when done
stream.close()
```

## Testing

### Python-Node Interoperability Test

Test communication between Python and Node.js hub-client implementations:

```bash
# Setup credentials
./scripts/python-node-test.sh setup

# Run test (Python initiator, Node.js responder)
./scripts/python-node-test.sh run

# Run reversed (Node.js initiator, Python responder)
./scripts/python-node-test.sh run-rev
```

### Browser Test Backend

Use the Python client as initiator for the browser-based responder:

```bash
export DEVICE_ID=your-device-id
export ACCESS_KEY=your-access-key
export PEER_TWIN_ID=browser-responder-twin-id
export PHYHUB_REGION=eu

python examples/browser_test_backend.py
```

## Dependencies

- `python-socketio[asyncio]` - Socket.IO client
- `aiortc` - WebRTC implementation
- `opencv-python` - Webcam capture
- `aiohttp` - HTTP client

## License

MIT
