"""Internal process adapter. Never expose arbitrary argv as an MCP tool.

Process exit codes are deliberately separate from design-check results:
LibrePCB uses exit 1 for both rule findings and errors loading a project.
The domain layer must interpret the complete diagnostics before claiming a
clean design. Rule-diagnostic interpretation belongs to the Day 3 domain layer.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import math
import os
import subprocess
import threading
import time
from uuid import uuid4


@dataclass(frozen=True)
class ProcessResult:
    argv: tuple[str, ...]
    outcome: str
    exit_code: int | None
    elapsed_seconds: float
    stdout_path: str
    stderr_path: str
    stdout_excerpt: str
    stderr_excerpt: str
    stdout_truncated: bool
    stderr_truncated: bool
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _excerpt(path: Path, limit: int = 4000) -> tuple[str, bool]:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    return raw[:limit].decode("utf-8", errors="replace"), len(raw) > limit


class ProcessRunner:
    """Developer-facing adapter with finite timeout and disk-backed diagnostics.

    The caller supplies trusted executable/arguments. ProjectService enforces
    model-facing paths and operations; this adapter is not a product tool.
    """

    def __init__(self, executable: Path, logs_dir: Path, timeout: float = 60,
                 max_log_bytes: int = 2_000_000):
        if not math.isfinite(timeout) or timeout <= 0 or timeout > 300:
            raise ValueError("timeout must be finite and in (0, 300] seconds")
        self.executable = executable.resolve()
        self.logs_dir = logs_dir.resolve()
        self.timeout = timeout
        if type(max_log_bytes) is not int or not 1024 <= max_log_bytes <= 8_000_000:
            raise ValueError("max_log_bytes must be in 1024..8000000")
        self.max_log_bytes = max_log_bytes

    def run(self, args: list[str], *, cwd: Path) -> ProcessResult:
        argv = (str(self.executable), *args)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        operation_id = uuid4().hex
        stdout_path = self.logs_dir / f"{operation_id}.stdout.txt"
        stderr_path = self.logs_dir / f"{operation_id}.stderr.txt"
        started = time.monotonic()
        exit_code = None
        error = None
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            if not self.executable.is_file():
                outcome = "cli_missing"
                error = "The configured executable does not exist."
            else:
                # This Windows portable build hangs with QT_QPA_PLATFORM=offscreen.
                # Use the native default; CREATE_NO_WINDOW suppresses console windows.
                environment = os.environ.copy()
                if os.name == "nt":
                    environment.pop("QT_QPA_PLATFORM", None)
                # Locale behavior is verified only in the recorded host environment.
                environment["LC_ALL"] = "C"
                environment.pop("LIBREPCB_SUPPRESS_DEPRECATION_WARNINGS", None)
                try:
                    process = subprocess.Popen(
                        argv,
                        cwd=cwd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=False,
                        env=environment,
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                        ),
                    )
                except OSError as exc:
                    outcome = "process_failed"
                    error = str(exc)
                else:
                    overflow = threading.Event()
                    reader_errors = []

                    def drain(pipe, destination):
                        remaining = self.max_log_bytes
                        try:
                            with pipe:
                                while chunk := pipe.read1(16_384):
                                    destination.write(chunk[:remaining])
                                    remaining -= min(len(chunk), remaining)
                                    if remaining == 0:
                                        # Reaching the cap also terminates the process;
                                        # never report possibly truncated logs as clean.
                                        overflow.set()
                        except (OSError, ValueError) as exc:
                            reader_errors.append(type(exc).__name__)

                    readers = [threading.Thread(target=drain, args=(pipe, target), daemon=True)
                               for pipe, target in ((process.stdout, stdout), (process.stderr, stderr))]
                    for reader in readers:
                        reader.start()
                    try:
                        while True:
                            if overflow.is_set():
                                process.kill()
                                process.wait()
                                outcome = "output_limit"
                                error = "CLI diagnostics reached the byte limit; logs may be incomplete."
                                break
                            remaining_time = self.timeout - (time.monotonic() - started)
                            if remaining_time <= 0:
                                process.kill()
                                process.wait()
                                outcome = "timeout"
                                error = "The command exceeded its time limit and was terminated."
                                break
                            try:
                                exit_code = process.wait(timeout=min(.05, remaining_time))
                                outcome = "completed"
                                break
                            except subprocess.TimeoutExpired:
                                continue
                    except BaseException:
                        process.kill()
                        process.wait()
                        raise
                    finally:
                        for reader in readers:
                            reader.join(timeout=5)
                    if outcome == "completed" and overflow.is_set():
                        outcome = "output_limit"
                        error = "CLI diagnostics reached the byte limit; logs may be incomplete."
                    if reader_errors or any(reader.is_alive() for reader in readers):
                        outcome = "process_failed"
                        error = "CLI diagnostics could not be fully captured."
        out, out_truncated = _excerpt(stdout_path)
        err, err_truncated = _excerpt(stderr_path)
        return ProcessResult(
            argv=argv,
            outcome=outcome,
            exit_code=exit_code,
            elapsed_seconds=round(time.monotonic() - started, 3),
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            stdout_excerpt=out,
            stderr_excerpt=err,
            stdout_truncated=out_truncated,
            stderr_truncated=err_truncated,
            error=error,
        )
