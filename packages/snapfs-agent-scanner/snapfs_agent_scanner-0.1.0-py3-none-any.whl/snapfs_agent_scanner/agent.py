#!/usr/bin/env python3
#
# Copyright (c) 2025 SnapFS, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
import sys
import traceback
from typing import Any, Dict, Optional

import aiohttp

from .config import settings

LOG_PREFIX = "[agent-scanner]"


def log(msg: str) -> None:
    print(f"{LOG_PREFIX} {msg}", file=sys.stderr, flush=True)


def build_agent_hello() -> Dict[str, Any]:
    """Build AGENT_HELLO payload: one FS capability for now."""
    return {
        "type": "AGENT_HELLO",
        "agent_id": settings.agent_id,
        "agent_type": "scanner",
        "version": "0.1.0",
        "capabilities": [
            {
                "id": "default-fs",
                "kind": "fs",
                "root": settings.scan_root,
            }
        ],
    }


async def run_scan_command(
    root: str,
    options: Dict[str, Any],
    command_id: str,
    ws: aiohttp.ClientWebSocketResponse,
) -> None:
    """
    Run `snapfs scan <root> ...` as a subprocess.

    For v1:
      - We do NOT send scan start/finish over WS to avoid duplicating
        scan events that the CLI already publishes via HTTP.
      - We ONLY send SCAN_ERROR if the subprocess fails.
    """
    cmd = ["snapfs", "scan", root]

    if options.get("verbose"):
        cmd.append("--verbose")

    if options.get("force"):
        cmd.append("--force")

    # Never use --no-cache here; the agent is for online mode.
    env = os.environ.copy()

    log(f"Running scan command_id={command_id} root={root} cmd={' '.join(cmd)}")

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout_bytes, stderr_bytes = await process.communicate()
        stdout_text = stdout_bytes.decode("utf-8", errors="replace")
        returncode = process.returncode

        if returncode == 0:
            log(
                f"Scan completed OK command_id={command_id} "
                f"(stdout tail: {stdout_text[-400:].rstrip()})"
            )

        stderr_text = stderr_bytes.decode("utf-8", errors="replace")
        log(
            f"Scan failed command_id={command_id} returncode={returncode} "
            f"stderr={stderr_text[-2000:]}"
        )

        await ws.send_json(
            {
                "type": "SCAN_ERROR",
                "command_id": command_id,
                "agent_id": settings.agent_id,
                "root": root,
                "status": "error",
                "returncode": returncode,
                "stderr": stderr_text[-2000:],
            }
        )

    except Exception as e:
        log(f"Exception while running scan: {e!r}")
        traceback.print_exc()
        try:
            await ws.send_json(
                {
                    "type": "SCAN_ERROR",
                    "command_id": command_id,
                    "agent_id": settings.agent_id,
                    "root": root,
                    "status": "error",
                    "error": str(e),
                }
            )
        except Exception:
            # If WS is already dead, nothing more to do
            pass


async def ws_loop() -> None:
    """Main WS loop: connect to gateway, send HELLO, listen for SCAN_TARGET."""
    url = settings.gateway_ws.rstrip("/") + settings.ws_path
    backoff = 1

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                log(f"Connecting to gateway WS at {url}")
                async with session.ws_connect(url) as ws:
                    log("Connected to gateway WS")
                    backoff = 1

                    await ws.send_json(build_agent_hello())

                    current_task: Optional[asyncio.Task] = None

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                payload = msg.json()
                            except Exception:
                                log("Received non-JSON text; ignoring")
                                continue

                            msg_type = payload.get("type")

                            if msg_type == "PING":
                                await ws.send_json({"type": "PONG"})
                                continue

                            if msg_type == "SCAN_TARGET":
                                if current_task is not None and not current_task.done():
                                    log(
                                        "Received SCAN_TARGET while a scan is in progress; ignoring"
                                    )
                                    await ws.send_json(
                                        {
                                            "type": "SCAN_ERROR",
                                            "command_id": payload.get("command_id"),
                                            "agent_id": settings.agent_id,
                                            "status": "busy",
                                            "error": "Scan already in progress",
                                        }
                                    )
                                    continue

                                target = payload.get("target") or {}
                                root = target.get("root") or settings.scan_root
                                options = payload.get("options") or {}
                                command_id = payload.get("command_id") or "unknown"

                                current_task = asyncio.create_task(
                                    run_scan_command(
                                        root=root,
                                        options=options,
                                        command_id=command_id,
                                        ws=ws,
                                    )
                                )
                                continue

                            log(f"Ignoring unknown WS message type: {msg_type}")
                            continue

                        if msg.type in (
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.CLOSING,
                            aiohttp.WSMsgType.CLOSED,
                        ):
                            log("WS closed by server")
                            break

                        # ignore binary/other for now

                log("WebSocket closed; will reconnect")

            except Exception as e:
                log(f"WS loop error: {e!r}; retrying in {backoff}s")
                traceback.print_exc()
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
