import mimetypes
from pathlib import Path
from typing import BinaryIO


def get_file_content(
    file: str | bytes | BinaryIO,
    name: str | None = None,
) -> tuple[str, bytes, str]:
    """Prepare file content for multipart upload.

    Returns:
        Tuple of (filename, content_bytes, content_type)
    """
    filename = name or "unknown"
    content: bytes
    content_type = "application/octet-stream"

    if isinstance(file, str):
        file_path = Path(file)
        if file_path.is_file():
            filename = name or file_path.name
            content = file_path.read_bytes()
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                content_type = mime_type
        else:
            content = file.encode("utf-8")
            content_type = "text/plain"
    elif isinstance(file, bytes):
        content = file
    elif hasattr(file, "read"):
        content = file.read()
        if hasattr(file, "name") and not name:
            filename = Path(file.name).name
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                content_type = mime_type
    else:
        raise TypeError(f"Unsupported file type: {type(file)}")

    return filename, content, content_type
