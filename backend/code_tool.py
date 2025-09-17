from __future__ import annotations

import os
import sys
import json
import tempfile
import subprocess
from typing import Dict, Any


def run_python(code: str, timeout_seconds: float = 10.0, memory_limit_mb: int = 256) -> Dict[str, Any]:
    """Execute untrusted Python code in a subprocess and return stdout and stderr.

    Notes:
    - Runs with isolated flags (-I) to minimize environment exposure.
    - Captures stdout/stderr, returns exit_code, and truncates large outputs.
    - Applies a soft memory limit on POSIX systems using 'resource' if available.
    """
    # Safety: do not allow ridiculously long code blobs
    if len(code) > 200_000:
        return {
            "stdout": "",
            "stderr": "Code too large (>200k chars).",
            "exit_code": -1,
            "truncated": False,
        }

    # Prepare a temporary working directory and file
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = os.path.join(tmp_dir, "snippet.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        python_exe = sys.executable or "python3"

        # Pre-exec function to set resource limits (POSIX only)
        def _limit_resources():
            try:
                import resource

                # Address space / virtual memory limit
                mem_bytes = int(memory_limit_mb) * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                # Disable core dumps
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                # CPU time limit (double the timeout to allow some overhead)
                cpu_seconds = max(1, int(timeout_seconds) * 2)
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            except Exception:
                # If not supported, proceed without hard limits
                pass

        try:
            proc = subprocess.run(
                [python_exe, "-I", script_path],
                input=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tmp_dir,
                timeout=timeout_seconds,
                check=False,
                text=True,
                preexec_fn=_limit_resources if os.name == "posix" else None,
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            exit_code = proc.returncode
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout or ""
            stderr = (e.stderr or "") + "\nExecution timed out."
            exit_code = -2
        except Exception as e:  # noqa: BLE001
            stdout = ""
            stderr = f"Executor error: {type(e).__name__}: {e}"
            exit_code = -3

        # Truncate very long outputs to keep the LLM context bounded
        max_chars = 30_000
        truncated = False
        if len(stdout) > max_chars:
            stdout = stdout[:max_chars] + "\n...[truncated]"
            truncated = True
        if len(stderr) > max_chars:
            stderr = stderr[:max_chars] + "\n...[truncated]"
            truncated = True

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "truncated": truncated,
        }


def build_run_python_tool_definition() -> Dict[str, Any]:
    """JSON schema for registering the local code interpreter as a tool."""
    return {
        "name": "run_python",
        "type": "function",
        "description": (
            "Execute a Python snippet in an isolated subprocess (numpy and scipy preinstalled) and return stdout, stderr, and exit_code."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source code to execute.",
                },
                "timeout_seconds": {
                    "type": "number",
                    "description": "Max execution time in seconds (default 10).",
                    "minimum": 1,
                    "maximum": 120,
                },
                "memory_limit_mb": {
                    "type": "integer",
                    "description": "Soft memory cap in MB for the process (default 256).",
                    "minimum": 64,
                    "maximum": 2048,
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    }


