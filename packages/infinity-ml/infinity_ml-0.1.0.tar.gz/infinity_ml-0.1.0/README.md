# infinity_ml

Python client for Infinity Media Server - GPU-accelerated image, video, and audio generation.

Designed to mirror the [fal_client](https://docs.fal.ai/api-reference) API for familiarity.

## Installation

```bash
pip install infinity_ml
```

## Quick Start

### Module-level Functions (fal_client style)

```python
from infinity_ml import run, submit, subscribe, status

# Simple blocking call
result = run("black-forest-labs/flux-dev", {"prompt": "A cat astronaut in space"})
print(result["images"][0]["download_url"])

# Submit and poll manually
handle = submit("black-forest-labs/flux-dev", {"prompt": "A cat"})
print(f"Submitted: {handle.request_id}")

# Wait with progress updates
for event in handle.iter_events():
    print(f"Status: {event}")
    
result = handle.get()

# Subscribe with callbacks
def on_update(status):
    print(f"Progress: {status}")

result = subscribe(
    "black-forest-labs/flux-dev",
    {"prompt": "A beautiful sunset"},
    on_queue_update=on_update,
)
```

### Client Class Usage

```python
from infinity_ml import SyncClient, AsyncClient

# Sync client
client = SyncClient()

# Run and wait
result = client.run("black-forest-labs/flux-dev", {"prompt": "A cat"})

# Convenience methods with typed results
image_result = client.image("A futuristic city")
print(image_result.images[0].download_url)

video_result = client.video("Ocean waves at sunset", num_frames=16)
print(video_result.video.download_url)

audio_result = client.audio("Hello from Infinity!")
print(audio_result.audio.download_url)

# Download file
client.download(audio_result.audio.download_url, "output.wav")
```

### Async Usage

```python
import asyncio
from infinity_ml import AsyncClient, run_async, submit_async

async def main():
    # Module-level async functions
    result = await run_async("black-forest-labs/flux-dev", {"prompt": "A cat"})
    
    # Or use AsyncClient
    async with AsyncClient() as client:
        handle = await client.submit("black-forest-labs/flux-dev", {"prompt": "A cat"})
        result = await handle.get()

asyncio.run(main())
```

## API Reference

### Module-level Functions

| Function | Description |
|----------|-------------|
| `run(app, args)` | Submit and wait for result (blocking) |
| `submit(app, args)` | Submit job, returns `SyncRequestHandle` |
| `subscribe(app, args, ...)` | Submit with status callbacks |
| `status(app, request_id)` | Get job status |
| `result(app, request_id)` | Get job result |
| `cancel(app, request_id)` | Cancel job (if supported) |

Async versions: `run_async`, `submit_async`, `subscribe_async`, `status_async`, `result_async`, `cancel_async`

### SyncClient / AsyncClient

```python
client = SyncClient(
    base_url="http://192.222.55.191:8000",  # Default demo server
    default_timeout=300.0,                   # Max wait time (seconds)
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `run(app, args)` | Submit and wait for result |
| `submit(app, args)` | Submit job, returns handle |
| `subscribe(app, args, ...)` | Submit with callbacks |
| `status(app, request_id)` | Get job status |
| `result(app, request_id)` | Get job result |
| `get_handle(app, request_id)` | Get handle for existing job |
| `health()` | Server health check |
| `ready()` | Server readiness & GPU status |
| `models()` | List available models |

#### Convenience Methods (typed results)

| Method | Description |
|--------|-------------|
| `image(prompt, ...)` | Generate image, returns `ImageResult` |
| `video(prompt, ...)` | Generate video, returns `VideoResult` |
| `audio(text, ...)` | Generate audio, returns `AudioResult` |
| `download(url, path)` | Download generated file |

### Request Handles

Returned by `submit()`, provides methods to track job progress:

```python
handle = submit("black-forest-labs/flux-dev", {"prompt": "A cat"})

handle.request_id           # Job ID string
handle.status()             # Returns Status (Queued, InProgress, Completed, Failed)
handle.get()                # Wait and return result (blocking)
handle.iter_events()        # Iterate status updates until complete
handle.cancel()             # Cancel job (if supported)
```

### Status Types

```python
from infinity_ml import Queued, InProgress, Completed, Failed

status = handle.status()

if isinstance(status, Queued):
    print(f"Queue position: {status.position}")
elif isinstance(status, InProgress):
    print("Processing...")
elif isinstance(status, Completed):
    print("Done!")
elif isinstance(status, Failed):
    print(f"Error: {status.error}")
```

## Available Models

| Model ID | Type | Example |
|----------|------|---------|
| `black-forest-labs/flux-dev` | Image | `{"prompt": "A cat"}` |
| `wan-ai/wan2.2-t2v` | Video (2.2) | `{"prompt": "Waves", "guidance_scale": 4.0, "guidance_scale_2": 3.0}` |
| `wan-ai/wan2.1-1.3b` | Video (2.1) | `{"prompt": "Waves", "num_frames": 33}` |
| `wan-ai/wan2.1-14b` | Video (2.1) | `{"prompt": "Waves", "num_frames": 33}` |
| `boson-ai/higgs-audio-v2` | Audio | `{"text": "Hello!"}` |

See [client_model_docs/](../../../client_model_docs/) for detailed parameter documentation.

## Caveats (Demo Version)

⚠️ **This is a demo/development version:**

- **Hardcoded server IP:** The default URL (`http://192.222.55.191:8000`) points to a Lambda Labs development instance. This will be replaced with a proper domain in production.
- **No authentication:** The demo server has no API key requirement.
- **Ephemeral storage:** Generated files are stored temporarily and may be cleaned up.

For production use, specify your own server URL:

```python
from infinity_ml import SyncClient

client = SyncClient("https://your-production-server.com")
```

Or set the `INFINITY_SERVER_URL` environment variable:

```bash
export INFINITY_SERVER_URL=https://your-production-server.com
```

## License

MIT
