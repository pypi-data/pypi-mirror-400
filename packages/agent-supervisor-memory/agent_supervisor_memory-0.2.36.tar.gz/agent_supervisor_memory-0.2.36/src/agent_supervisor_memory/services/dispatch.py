"""
Background task execution via 'codex exec' with polling support.

CodexDispatch:
  - Launches 'codex exec' in background threads (non-blocking)
  - Captures stdout.jsonl, stderr.log, and last_message.txt
  - Supports job buckets for multi-project setups
  - Thread-safe; metadata stored in JSON for durability
  - Polling API: status(job_id) returns meta + tails with optional compaction

Usage:
  1. config = CodexDispatchConfig(jobs_dir=Path(...))
  2. dispatch = CodexDispatch(config)
  3. res = dispatch.start(prompt="...", model="...", cwd="...")  # returns job_id
  4. status = dispatch.status(job_id=res['job_id'])  # poll until status in (completed, failed)
  5. Access artifacts via status['meta']['artifacts'] (paths to job_dir, stdout, stderr, etc.)

Storage layout:
  - jobs_dir/
    - {job_id}/meta.json          # job metadata + status + command
    - {job_id}/stdout.jsonl       # codex output (JSONL)
    - {job_id}/stderr.log         # stderr from codex process
    - {job_id}/last_message.txt   # final message from codex (if --output-last-message used)
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..utils.fs import atomic_write_json


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text_tail(path: Path, max_bytes: int) -> str | None:
    if max_bytes <= 0:
        return None
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            start = max(0, size - max_bytes)
            f.seek(start)
            data = f.read()
    except FileNotFoundError:
        return None
    return data.decode("utf-8", errors="replace")


def _read_text_from_offset(path: Path, start_offset: int, max_bytes: int) -> tuple[str | None, int]:
    if max_bytes <= 0:
        return None, int(start_offset or 0)
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            start = max(0, min(int(start_offset or 0), size))
            if start >= size:
                return None, size
            f.seek(start)
            data = f.read(max_bytes)
            return data.decode("utf-8", errors="replace"), start + len(data)
    except FileNotFoundError:
        return None, int(start_offset or 0)


def _read_jsonl_events_from_offset(
    path: Path,
    start_offset: int,
    *,
    max_bytes: int,
    max_items: int,
) -> tuple[list[dict[str, Any]], int, bool]:
    """
    Read JSONL events from a file starting at a byte offset.

    Returns (events, next_cursor, has_more). Cursor advances only on complete lines (newline-terminated).
    """
    events: list[dict[str, Any]] = []
    start = int(start_offset or 0)
    if max_bytes <= 0 or max_items <= 0:
        return events, start, False
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            start = max(0, min(start, size))
            if start >= size:
                return events, size, False
            f.seek(start)
            buf = f.read(max_bytes)
            if not buf:
                return events, start, False

            i = 0
            consumed = 0
            while i < len(buf) and len(events) < max_items:
                j = buf.find(b"\n", i)
                if j == -1:
                    break
                line = buf[i:j].strip()
                i = j + 1
                consumed = i
                if not line:
                    continue
                try:
                    obj = json.loads(line.decode("utf-8", errors="replace"))
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    events.append(obj)

            next_cursor = start + consumed
            has_more = next_cursor < size
            return events, next_cursor, has_more
    except FileNotFoundError:
        return events, start, False


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CodexDispatchConfig:
    jobs_dir: Path


class CodexDispatch:
    """
    Background task execution via 'codex exec' with polling support.

    Thread-safe. Launches each task in a daemon thread and stores metadata/output in JSON files.
    Suitable for MCP use where tool calls must return quickly.
    """

    def __init__(self, config: CodexDispatchConfig):
        self._config = config
        self._lock = threading.Lock()
        self._threads: dict[str, threading.Thread] = {}

    @property
    def jobs_dir(self) -> Path:
        return self._config.jobs_dir

    def _job_dir(self, job_id: str) -> Path:
        return self._config.jobs_dir / job_id

    def _meta_path(self, job_id: str) -> Path:
        return self._job_dir(job_id) / "meta.json"

    def _write_meta(self, job_id: str, data: dict[str, Any]) -> None:
        atomic_write_json(self._meta_path(job_id), data)

    def _patch_meta(self, job_id: str, patch: dict[str, Any]) -> None:
        existing = self.load_meta(job_id) or {"id": job_id}
        merged = {**existing, **patch}
        self._write_meta(job_id, merged)

    def load_meta(self, job_id: str) -> dict[str, Any] | None:
        try:
            return json.loads(self._meta_path(job_id).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return {"id": job_id, "status": "unknown", "corrupt": True}

    def start(
        self,
        *,
        prompt: str,
        model: str | None,
        cwd: str | None,
        sandbox: str | None,
        approval_policy: str | None,
        extra_config: list[str] | None,
        env: dict[str, str] | None,
        job_id: str | None = None,
        job_id_prefix: str | None = None,
    ) -> dict[str, Any]:
        """
        Launch a background 'codex exec' task.

        Args:
            prompt: Task prompt/instruction to pipe into codex exec
            model: Codex model (e.g., gpt-5.1-codex-max); passed to -m flag
            cwd: Working directory for task execution; passed to -C flag
            sandbox: Sandbox level (e.g., workspace-write, danger-full-access); passed to -s flag
            approval_policy: Approval mode (e.g., never, ask); passed to -a flag
            extra_config: List of extra config strings; each passed as -c <config>
            env: Environment variables to inject into task process
            job_id_prefix: Optional bucket prefix for job_id (typically project name);
                          job_id will be formatted as "{prefix}--{uuid}" if provided

        Returns:
            dict with job_id, status="running", and artifacts paths (job_dir, stdout_jsonl, stderr_log, last_message)
        """
        resolved_job_id = str(job_id).strip() if job_id else ""
        if not resolved_job_id:
            base_id = uuid.uuid4().hex
            resolved_job_id = f"{job_id_prefix}--{base_id}" if job_id_prefix else base_id

        # Idempotency/attach: if job already exists, do not start a second process.
        existing_meta = self.load_meta(resolved_job_id)
        if existing_meta is None:
            probe_dir = self._job_dir(resolved_job_id)
            if probe_dir.exists():
                existing_meta = {"id": resolved_job_id, "status": "unknown", "corrupt": True}
        if isinstance(existing_meta, dict) and existing_meta.get("status"):
            artifacts = existing_meta.get("artifacts") if isinstance(existing_meta.get("artifacts"), dict) else None
            if not artifacts:
                job_dir = self._job_dir(resolved_job_id)
                artifacts = {
                    "job_dir": str(job_dir),
                    "stdout_jsonl": str(job_dir / "stdout.jsonl"),
                    "stderr_log": str(job_dir / "stderr.log"),
                    "last_message": str(job_dir / "last_message.txt"),
                }
            return {
                "job_id": resolved_job_id,
                "status": existing_meta.get("status") or "unknown",
                "artifacts": artifacts,
                "existing": True,
            }

        job_id = resolved_job_id
        job_dir = self._job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        stdout_path = job_dir / "stdout.jsonl"
        stderr_path = job_dir / "stderr.log"
        last_msg_path = job_dir / "last_message.txt"

        cmd: list[str] = ["codex"]
        if approval_policy:
            cmd += ["-a", approval_policy]
        cmd += ["exec", "--json", "--color", "never", "--output-last-message", str(last_msg_path), "-"]
        if model:
            cmd += ["-m", model]
        if sandbox:
            cmd += ["-s", sandbox]
        if cwd:
            cmd += ["-C", cwd]
        for c in (extra_config or []):
            if c and isinstance(c, str):
                cmd += ["-c", c]

        meta: dict[str, Any] = {
            "id": job_id,
            "created_at": _utc_now_iso(),
            "status": "running",
            "prompt_sha256": _sha256(prompt),
            "cwd": cwd,
            "model": model,
            "sandbox": sandbox,
            "approval_policy": approval_policy,
            "command": cmd,
            "artifacts": {
                "job_dir": str(job_dir),
                "stdout_jsonl": str(stdout_path),
                "stderr_log": str(stderr_path),
                "last_message": str(last_msg_path),
            },
            "pid": None,
            "cancel_requested": False,
        }
        self._write_meta(job_id, meta)

        def run() -> None:
            try:
                proc_env = os.environ.copy()
                if env:
                    proc_env.update({str(k): str(v) for k, v in env.items()})
                with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
                    p = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=out,
                        stderr=err,
                        env=proc_env,
                    )
                    self._patch_meta(job_id, {"pid": p.pid})
                    assert p.stdin is not None
                    p.stdin.write((prompt or "").encode("utf-8"))
                    p.stdin.close()
                    exit_code = p.wait()

                done_meta = self.load_meta(job_id) or {"id": job_id}
                cancel_requested = bool(done_meta.get("cancel_requested"))
                if cancel_requested and exit_code != 0:
                    status = "canceled"
                else:
                    status = "completed" if exit_code == 0 else "failed"
                done_meta.update(
                    {
                        "status": status,
                        "exit_code": exit_code,
                        "finished_at": _utc_now_iso(),
                    }
                )
                self._write_meta(job_id, done_meta)
            except Exception as e:  # pragma: no cover - defensive
                fail_meta = self.load_meta(job_id) or {"id": job_id}
                fail_meta.update({"status": "failed", "error": repr(e), "finished_at": _utc_now_iso()})
                self._write_meta(job_id, fail_meta)

        t = threading.Thread(target=run, name=f"codex-dispatch-{job_id}", daemon=True)
        with self._lock:
            self._threads[job_id] = t
        t.start()

        return {"job_id": job_id, "status": "running", "artifacts": meta["artifacts"]}

    def cancel(self, *, job_id: str) -> dict[str, Any]:
        meta = self.load_meta(job_id)
        if not meta:
            return {"state": "not_found", "job_id": job_id, "message": "Job not found"}

        status = str(meta.get("status") or "")
        if status and status != "running":
            return {"state": status, "job_id": job_id, "message": "Job is not running"}

        pid = meta.get("pid")
        if not pid:
            self._patch_meta(job_id, {"cancel_requested": True})
            return {"state": "running", "job_id": job_id, "code": "E_NO_PID", "message": "cancel requested (pid unavailable)"}

        try:
            os.kill(int(pid), signal.SIGTERM)
        except ProcessLookupError:
            self._patch_meta(job_id, {"cancel_requested": True})
            return {"state": "running", "job_id": job_id, "code": "E_PROCESS_NOT_FOUND", "message": "process not found"}
        except Exception as e:  # pragma: no cover - defensive
            return {"state": "error", "job_id": job_id, "code": "E_CANCEL_FAILED", "message": compact_text(repr(e), max_len=160)}

        self._patch_meta(job_id, {"cancel_requested": True})
        return {"state": "running", "job_id": job_id, "message": "cancel requested"}

    def events(
        self,
        *,
        job_id: str,
        cursor: int = 0,
        max_bytes: int = 8000,
        max_items: int = 50,
    ) -> dict[str, Any]:
        meta = self.load_meta(job_id)
        if not meta:
            return {"found": False, "job_id": job_id}
        artifacts = meta.get("artifacts") or {}
        stdout_path = Path(str(artifacts.get("stdout_jsonl") or ""))
        events, next_cursor, has_more = _read_jsonl_events_from_offset(
            stdout_path,
            int(cursor or 0),
            max_bytes=int(max_bytes or 0),
            max_items=int(max_items or 0),
        )
        keys = ["id", "status", "created_at", "finished_at", "exit_code", "cwd", "model", "sandbox", "approval_policy"]
        meta_out = {k: meta.get(k) for k in keys if k in meta}
        return {
            "found": True,
            "meta": meta_out,
            "events": events,
            "cursor": next_cursor,
            "has_more": has_more,
        }

    def status(
        self,
        *,
        job_id: str,
        stdout_cursor: int | None = None,
        stderr_cursor: int | None = None,
        stdout_tail_bytes: int = 20000,
        stderr_tail_bytes: int = 20000,
        include_last_message: bool = True,
        last_message_max_bytes: int = 200000,
        compact: bool = True,
        include_artifacts: bool = False,
        include_command: bool = False,
    ) -> dict[str, Any]:
        """
        Poll the status of a background task.

        Args:
            job_id: Task identifier returned from start()
            stdout_tail_bytes: Max bytes of stdout.jsonl to include (0 = skip); default 20KB
            stderr_tail_bytes: Max bytes of stderr.log to include (0 = skip); default 20KB
            include_last_message: If True, read last_message.txt (can be large); use False while polling for efficiency
            last_message_max_bytes: Max bytes of last_message.txt to include; default 200KB
            compact: If True, return minimal meta (id/status/timestamps only); False returns full meta with command etc.
            include_artifacts: If compact=True, include artifact paths in meta
            include_command: If compact=True, include codex command in meta

        Returns:
            dict with found (bool), meta (dict with status/timestamps/model/cwd), last_message (str or None),
            stdout_tail (str or None), stderr_tail (str or None)
        """
        meta = self.load_meta(job_id)
        if not meta:
            return {"found": False, "job_id": job_id}

        artifacts = meta.get("artifacts") or {}
        last_msg_path = Path(str(artifacts.get("last_message") or ""))
        stdout_path = Path(str(artifacts.get("stdout_jsonl") or ""))
        stderr_path = Path(str(artifacts.get("stderr_log") or ""))

        last_message = None
        if include_last_message and last_msg_path.name:
            last_message = _read_text_tail(last_msg_path, last_message_max_bytes)

        stdout_delta = None
        stderr_delta = None
        next_stdout_cursor = None
        next_stderr_cursor = None
        stdout_tail = None
        stderr_tail = None

        if stdout_cursor is not None and stdout_path.name:
            stdout_delta, next_stdout_cursor = _read_text_from_offset(stdout_path, stdout_cursor, stdout_tail_bytes)
        else:
            stdout_tail = _read_text_tail(stdout_path, stdout_tail_bytes) if stdout_path.name else None

        if stderr_cursor is not None and stderr_path.name:
            stderr_delta, next_stderr_cursor = _read_text_from_offset(stderr_path, stderr_cursor, stderr_tail_bytes)
        else:
            stderr_tail = _read_text_tail(stderr_path, stderr_tail_bytes) if stderr_path.name else None

        if compact:
            keys = ["id", "status", "created_at", "finished_at", "exit_code", "cwd", "model", "sandbox", "approval_policy"]
            meta_out = {k: meta.get(k) for k in keys if k in meta}
            if include_command and "command" in meta:
                meta_out["command"] = meta.get("command")
            if include_artifacts and "artifacts" in meta:
                meta_out["artifacts"] = meta.get("artifacts")
        else:
            meta_out = meta

        payload: dict[str, Any] = {
            "found": True,
            "meta": meta_out,
            "last_message": last_message,
        }
        if stdout_cursor is not None:
            payload["stdout_delta"] = stdout_delta
            payload["stdout_cursor"] = next_stdout_cursor if next_stdout_cursor is not None else int(stdout_cursor or 0)
        else:
            payload["stdout_tail"] = stdout_tail
        if stderr_cursor is not None:
            payload["stderr_delta"] = stderr_delta
            payload["stderr_cursor"] = next_stderr_cursor if next_stderr_cursor is not None else int(stderr_cursor or 0)
        else:
            payload["stderr_tail"] = stderr_tail
        return payload
