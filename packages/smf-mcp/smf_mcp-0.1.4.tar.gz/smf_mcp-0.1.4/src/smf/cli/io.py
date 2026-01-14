from pathlib import Path


def write_utf8(file_path: Path, content: str) -> None:
    """Write content to file with UTF-8 encoding."""
    file_path.write_text(content, encoding="utf-8")
