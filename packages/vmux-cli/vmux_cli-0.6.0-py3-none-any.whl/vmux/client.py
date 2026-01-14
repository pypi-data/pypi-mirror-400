"""HTTP client for vmux worker API."""

import base64
import json
import os
import secrets
import time
from typing import Callable, Iterator

import httpx

from .config import VmuxConfig, load_config

DEBUG = os.environ.get("VMUX_DEBUG", "").lower() in ("1", "true", "yes")

# Bundle size thresholds (in raw bytes, before base64 encoding)
# Under 24MB: use inline writeFile (simple, single request)
# Over 24MB: upload to R2 (faster and more consistent for large bundles)
INLINE_THRESHOLD = 24 * 1024 * 1024  # 24MB
MAX_BUNDLE_SIZE = 100 * 1024 * 1024  # 100MB (Worker request body limit)


class TupClient:
    """Client for the vmux worker API."""

    def __init__(self, config: VmuxConfig | None = None):
        self.config = config or load_config()
        self._client = httpx.Client(
            base_url=self.config.api_url,
            timeout=httpx.Timeout(300.0, connect=30.0),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TupClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        return headers

    def upload_bundle(self, bundle_data: bytes) -> str:
        """Upload raw bundle bytes to R2, return bundle_id."""
        bundle_id = secrets.token_hex(16)
        if DEBUG:
            print(f"[DEBUG] Uploading bundle {bundle_id} ({len(bundle_data)} bytes) to R2")

        t0 = time.time()
        response = self._client.put(
            f"/bundles/{bundle_id}",
            content=bundle_data,
            headers={**self._headers(), "Content-Type": "application/zip"},
        )
        response.raise_for_status()

        if DEBUG:
            print(f"[DEBUG] Bundle uploaded in {time.time() - t0:.2f}s")

        return bundle_id

    def run(
        self,
        command: str,
        bundle_data: bytes,
        env_vars: dict[str, str] | None = None,
        editables: list[str] | None = None,
        ports: list[int] | None = None,
        runtime: str | None = None,
        on_upload_start: Callable[[int, bool], None] | None = None,  # (size, is_r2) -> None
    ) -> Iterator[dict]:
        """Run a command and stream logs.

        Args:
            command: Command to run
            bundle_data: Raw zip bundle bytes (tiered upload handled automatically)
            env_vars: Environment variables
            editables: List of editable package names (for PYTHONPATH)
            ports: Ports to expose for preview URLs (default: [8000])
            runtime: Force runtime ("python", "bun", "node") - auto-detected if None

        Yields events:
            {"job_id": "..."} - First event with job ID
            {"log": "..."} - Log line
            {"status": "completed"|"failed", "exit_code": int} - Final status
            {"error": "..."} - Error message
        """
        merged_env = {**self.config.env, **(env_vars or {})}

        # Check bundle size limit
        bundle_size = len(bundle_data)
        if bundle_size > MAX_BUNDLE_SIZE:
            size_mb = bundle_size / (1024 * 1024)
            raise ValueError(
                f"Bundle too large: {size_mb:.1f}MB (max 100MB). "
                f"Try adding large files to .vmuxignore or use a smaller dataset."
            )

        # Tiered upload: small bundles inline, large bundles via R2
        use_r2 = bundle_size > INLINE_THRESHOLD

        # Notify caller that upload is starting
        if on_upload_start:
            on_upload_start(bundle_size, use_r2)

        if not use_r2:
            # Small bundle: base64 encode and send inline
            bundle_b64 = base64.b64encode(bundle_data).decode("ascii")
            payload: dict = {
                "command": command,
                "bundle": bundle_b64,
                "env_vars": merged_env,
                "editables": editables or [],
                "ports": ports or [],
            }
            if runtime:
                payload["runtime"] = runtime
            if DEBUG:
                print(f"[DEBUG] Using inline upload ({bundle_size} bytes raw, {len(bundle_b64)} chars base64)")
        else:
            # Large bundle: upload to R2 first, send bundle_id
            if DEBUG:
                print(f"[DEBUG] Bundle too large for inline ({bundle_size} bytes), using R2 upload")
            bundle_id = self.upload_bundle(bundle_data)
            payload = {
                "command": command,
                "bundle_id": bundle_id,
                "env_vars": merged_env,
                "editables": editables or [],
                "ports": ports or [],
            }
            if runtime:
                payload["runtime"] = runtime

        if DEBUG:
            print(f"[DEBUG] Payload size: {len(json.dumps(payload))} bytes")

        t0 = time.time()
        with self._client.stream(
            "POST",
            "/run",
            json=payload,
            headers={**self._headers(), "Accept": "text/event-stream"},
            timeout=None,
        ) as response:
            if DEBUG:
                print(f"[DEBUG] Response received in {time.time() - t0:.2f}s, status={response.status_code}")
            response.raise_for_status()

            buffer = ""
            first_event = True
            for chunk in response.iter_text():
                if first_event and DEBUG:
                    print(f"[DEBUG] First chunk received in {time.time() - t0:.2f}s")
                    first_event = False
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            pass

    def list_jobs(self, limit: int = 50) -> list[dict]:
        """List recent jobs."""
        response = self._client.get("/jobs", params={"limit": limit}, headers=self._headers())
        response.raise_for_status()
        return response.json().get("jobs", [])

    def get_job(self, job_id: str) -> dict:
        """Get job status."""
        response = self._client.get(f"/jobs/{job_id}", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        response = self._client.delete(f"/jobs/{job_id}", headers=self._headers())
        response.raise_for_status()
        return response.json().get("stopped", False)

    def purge_job(self, job_id: str) -> bool:
        """Permanently delete a job from history."""
        response = self._client.delete(f"/jobs/{job_id}?purge=true", headers=self._headers())
        response.raise_for_status()
        return response.json().get("purged", False)

    def get_logs(self, job_id: str) -> str:
        """Get job logs."""
        response = self._client.get(f"/jobs/{job_id}/logs", headers=self._headers())
        response.raise_for_status()
        return response.text

    def get_usage(self) -> dict:
        """Get current month's usage stats."""
        response = self._client.get("/usage", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_status(self) -> dict:
        """Get global capacity status."""
        response = self._client.get("/status", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def debug_job(self, job_id: str) -> dict:
        """Get debug info for a job (tmux status, processes, logs)."""
        response = self._client.get(f"/jobs/{job_id}/debug", headers=self._headers())
        response.raise_for_status()
        return response.json()
