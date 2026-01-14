# SnapFS Scanner Agent

The SnapFS Scanner Agent connects to the SnapFS Gateway over WebSocket and
runs `snapfs scan` commands on demand.

This lets the gateway (and web app) trigger scans on machines that have
direct access to storage (local filesystems, NFS mounts, etc.) without
teaching the `snapfs` CLI about WebSockets or long-running daemons.

The `snapfs` CLI remains responsible for talking HTTP to the gateway,
performing hash lookups, and publishing `file.upsert` events. The
scanner agent is purely a control-plane component that runs `snapfs scan`
as a subprocess.

## Responsibilities

- Connect to the SnapFS Gateway via WebSocket as a **scanner agent**.
- Advertise its capabilities (e.g. a local filesystem root).
- Receive `SCAN_TARGET` commands from the gateway.
- Run `snapfs scan <root> [options]` locally for each command.
- Report errors back to the gateway if scans fail.

the agent:

- Handles a single filesystem root (configured by `SNAPFS_SCAN_ROOT`).
- Runs one scan at a time.
- The `snapfs` CLI toolpublishes scan events

## Requirements

- SnapFS Gateway with an `/agents` WebSocket endpoint that:
  - accepts `AGENT_HELLO` messages, and
  - sends `SCAN_TARGET` commands to scanner agents.
- Python 3.8+ (if running the agent directly).
- The `snapfs` CLI installed and on `PATH` inside the container/host.

## Running

From Python (local dev):

```bash
pip install snapfs-agent-scanner snapfs
snapfs-agent-scanner
```

In Docker (image built from this repo):

```bash
docker run --rm \
  -e GATEWAY_WS=ws://gateway:8000 \
  -e SNAPFS_AGENT_ID=scanner-01 \
  -e SNAPFS_SCAN_ROOT=/mnt/data \
  -v /mnt/data:/mnt/data \
  ghcr.io/snapfsio/snapfs-agent-scanner:latest
```

## Configuration

The agent is configured via environment variables:

```bash
GATEWAY_WS          WebSocket base URL for the gateway (default: ws://gateway:8000)
GATEWAY_HTTP        HTTP base URL for the gateway (reserved for future use)
SNAPFS_AGENT_ID     Stable ID for this scanner agent (default: scanner-01)
SNAPFS_SCAN_ROOT    Default filesystem root inside the container (default: /data)
```
