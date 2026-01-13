"""Backward-compatible CLI entrypoint.

Prefer `python -m vision_agent ...` or installing the package and using the
console script entrypoint.
"""

from __future__ import annotations

from vision_agent.cli import main


if __name__ == "__main__":
    main()
