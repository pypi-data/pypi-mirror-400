"""Modes package - Each mode is self-contained with its logic and prompts."""

from . import action, automate, diff, displays, locate, locate_ocr, locate_xml, ocr

__all__ = [
    "action",
    "automate",
    "diff",
    "displays",
    "locate",
    "locate_ocr",
    "locate_xml",
    "ocr",
]
