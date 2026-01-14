# -*- coding: utf-8 -*-

from pathlib import Path


def safe_write(path: Path, content: str, encoding: str = "utf-8"):
    """
    Safely write content to a file, creating parent directories if needed.
    """
    try:
        path.write_text(content, encoding=encoding)
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
