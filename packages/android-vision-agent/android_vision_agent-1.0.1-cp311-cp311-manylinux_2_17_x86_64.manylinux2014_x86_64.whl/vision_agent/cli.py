"""CLI entrypoint for the vision agent app."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Iterator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vision agent application")
    parser.add_argument("prompt", nargs="?", help="User request or task")
    parser.add_argument(
        "--image",
        "-i",
        action="append",
        default=[],
        help="Path to an input image (repeatable)",
    )
    parser.add_argument("--device-id", "-d", help="ADB device ID")
    parser.add_argument(
        "--display-id",
        type=int,
        help="Android WindowManager display ID (useful for multi-display car systems)",
    )
    parser.add_argument(
        "--mode",
        choices=[
            "locate",
            "ocr",
            "locate-ocr",
            "locate-xml",
            "action",
            "diff",
            "automate",
            "displays",
        ],
        required=True,
        help="Execution mode",
    )
    parser.add_argument("--output-dir", help="Directory for outputs")
    parser.add_argument("--max-steps", type=int, help="Max steps for automate mode")
    parser.add_argument("--lang", choices=["cn", "en"], help="System prompt language")
    return parser.parse_args()


class _TeeTextIO:
    def __init__(self, *streams: IO[str]):
        self._streams = streams
        self.encoding = getattr(streams[0], "encoding", "utf-8")

    def write(self, data: str) -> int:
        for stream in self._streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()

    def isatty(self) -> bool:
        return any(getattr(stream, "isatty", lambda: False)() for stream in self._streams)


@contextmanager
def _tee_stdout_stderr(log_file: IO[str]) -> Iterator[None]:
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    try:
        sys.stdout = _TeeTextIO(original_stdout, log_file)  # type: ignore[assignment]
        sys.stderr = _TeeTextIO(original_stderr, log_file)  # type: ignore[assignment]
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def _install_termination_handlers(message: str) -> None:
    def _handler(signum: int, _frame) -> None:  # pragma: no cover
        print(f"{message} (signal={signum})", file=sys.stderr, flush=True)
        raise KeyboardInterrupt()

    for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGBREAK", None)):
        if sig is None:
            continue
        try:
            signal.signal(sig, _handler)
        except (OSError, RuntimeError, ValueError):
            continue


def main() -> None:
    args = parse_args()
    if args.mode != "displays" and not args.prompt:
        raise SystemExit("Missing prompt/task")

    from vision_agent.config import load_dotenv, load_settings
    from vision_agent.router import route
    from vision_agent.modes.llmclient import LlmClient

    load_dotenv()
    model_settings, app_settings = load_settings()

    if args.output_dir:
        app_settings.output_dir = args.output_dir
    if args.max_steps:
        app_settings.max_steps = args.max_steps
    if args.lang:
        app_settings.lang = args.lang

    output_dir = Path(app_settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"{time.strftime('%Y%m%d_%H%M%S')}_run.txt"

    llm = LlmClient(model_settings)

    image_paths = [str(Path(p)) for p in args.image]
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"cwd={Path.cwd()}\n")
        log_file.write(f"argv={sys.argv}\n")
        log_file.flush()

        with _tee_stdout_stderr(log_file):
            _install_termination_handlers("Execution interrupted")
            try:
                result = route(
                    llm=llm,
                    mode=args.mode,
                    prompt=args.prompt or "",
                    image_paths=image_paths,
                    device_id=args.device_id,
                    display_id=args.display_id,
                    output_dir=app_settings.output_dir,
                    max_steps=app_settings.max_steps,
                    lang=app_settings.lang,
                )
                if isinstance(result, dict):
                    result.setdefault("log_file_path", str(log_path))
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except KeyboardInterrupt:
                error = {"error": "interrupted", "log_file_path": str(log_path)}
                print(json.dumps(error, ensure_ascii=False, indent=2))
                raise SystemExit(130)
            except Exception as exc:
                import traceback

                traceback.print_exc()
                error = {
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "log_file_path": str(log_path),
                }
                print(json.dumps(error, ensure_ascii=False, indent=2))
                raise SystemExit(1)


if __name__ == "__main__":
    main()
