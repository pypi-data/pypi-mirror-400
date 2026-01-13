"""Router - Main orchestrator for all modes (replaces VisionAgent)."""

from __future__ import annotations

from typing import Any

from vision_agent.modes.llmclient import LlmClient
from vision_agent import modes


def route(
    llm: LlmClient,
    mode: str,
    prompt: str,
    image_paths: list[str] | None = None,
    device_id: str | None = None,
    display_id: int | None = None,
    output_dir: str = "outputs",
    max_steps: int = 10,
    lang: str = "cn",
) -> dict[str, Any]:
    """Route request to appropriate mode handler.

    This function replaces the VisionAgent class and directly routes to mode modules.
    Each mode is self-contained with its own logic and prompts.
    """
    image_paths = image_paths or []

    # Common kwargs for all modes
    kwargs = {
        "llm": llm,
        "prompt": prompt,
        "image_paths": image_paths,
        "device_id": device_id,
        "display_id": display_id,
        "output_dir": output_dir,
        "max_steps": max_steps,
        "lang": lang,
    }

    # Route to appropriate mode
    if mode == "displays":
        return modes.displays.run(**kwargs)

    if mode == "diff":
        return modes.diff.run(image_paths=image_paths, output_dir=output_dir, **kwargs)

    if mode == "locate-xml":
        return modes.locate_xml.run(**kwargs)

    if mode == "locate":
        return modes.locate.run(**kwargs)

    if mode == "ocr":
        return modes.ocr.run(**kwargs)

    if mode == "locate-ocr":
        return modes.locate_ocr.run(**kwargs)

    if mode == "action":
        return modes.action.run(**kwargs)

    if mode == "automate":
        return modes.automate.run(**kwargs)

    raise ValueError(f"Unknown mode: {mode}")


__all__ = ["route"]
