"""Sandboxed filesystem tools with path validation and quotas."""

import os
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any


# Allowed base directories for sandboxing
# In production, these should be configured per agent
DEFAULT_ALLOWED_DIRS = [
    os.path.expanduser("~/anse_workspace"),  # User's ANSE workspace
    os.path.expanduser("~/anse_data"),       # User's ANSE data directory
]


def _validate_path(file_path: str, allowed_dirs: Optional[List[str]] = None) -> tuple[bool, str]:
    """
    Validate that a path is within allowed directories.

    Args:
        file_path: Path to validate
        allowed_dirs: List of allowed base directories

    Returns:
        (is_valid, reason)
    """
    if not allowed_dirs:
        allowed_dirs = DEFAULT_ALLOWED_DIRS

    # Resolve to absolute path
    try:
        abs_path = os.path.abspath(os.path.expanduser(file_path))
    except Exception as e:
        return False, f"path_invalid: {str(e)}"

    # Check if path is within allowed directories
    for allowed_dir in allowed_dirs:
        allowed_abs = os.path.abspath(os.path.expanduser(allowed_dir))
        try:
            # Use os.path.commonpath to check containment
            common = os.path.commonpath([abs_path, allowed_abs])
            if common == allowed_abs:
                return True, ""
        except ValueError:
            # Different drives on Windows
            continue

    return False, f"path_outside_allowed_dirs"


async def read_file(
    file_path: str,
    encoding: str = "utf-8",
    max_size_mb: int = 10,
    allowed_dirs: Optional[List[str]] = None,
) -> dict:
    """
    Read a file from disk (sandboxed).

    Args:
        file_path: Path to file (relative or absolute, within allowed dirs)
        encoding: Text encoding (utf-8, ascii, etc.)
        max_size_mb: Maximum file size to read (default 10MB)
        allowed_dirs: Allowed base directories for sandboxing

    Returns:
        {
            "status": "success" | "error",
            "file_path": str,
            "size_bytes": int,
            "content": str,
            "content_hash": str (SHA256),
            "error": str (if failed)
        }
    """
    # Validate path
    is_valid, reason = _validate_path(file_path, allowed_dirs)
    if not is_valid:
        return {
            "status": "error",
            "error": reason,
            "message": "Access denied: path outside allowed directories",
        }

    # Check if file exists
    abs_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(abs_path):
        return {
            "status": "error",
            "error": "file_not_found",
            "file_path": abs_path,
        }

    if not os.path.isfile(abs_path):
        return {
            "status": "error",
            "error": "path_is_not_file",
            "file_path": abs_path,
        }

    # Check file size
    file_size = os.path.getsize(abs_path)
    max_bytes = max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        return {
            "status": "error",
            "error": "file_too_large",
            "size_bytes": file_size,
            "max_bytes": max_bytes,
            "file_path": abs_path,
        }

    # Check encoding support
    if encoding not in ("utf-8", "ascii", "latin-1", "utf-16"):
        return {
            "status": "error",
            "error": "unsupported_encoding",
            "encoding": encoding,
        }

    try:
        with open(abs_path, "r", encoding=encoding) as f:
            content = f.read()

        # Calculate hash
        content_hash = hashlib.sha256(content.encode(encoding)).hexdigest()

        return {
            "status": "success",
            "file_path": abs_path,
            "size_bytes": file_size,
            "content": content,
            "content_hash": content_hash,
            "encoding": encoding,
        }

    except PermissionError:
        return {
            "status": "error",
            "error": "permission_denied",
            "file_path": abs_path,
        }
    except UnicodeDecodeError as e:
        return {
            "status": "error",
            "error": "encoding_error",
            "file_path": abs_path,
            "message": str(e),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": "read_failed",
            "file_path": abs_path,
            "message": str(e),
        }


async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = False,
    max_size_mb: int = 100,
    allowed_dirs: Optional[List[str]] = None,
) -> dict:
    """
    Write content to a file (sandboxed).

    Args:
        file_path: Path to file (within allowed dirs)
        content: Content to write
        encoding: Text encoding
        create_dirs: Whether to create parent directories
        max_size_mb: Maximum file size (default 100MB)
        allowed_dirs: Allowed base directories for sandboxing

    Returns:
        {
            "status": "success" | "error",
            "file_path": str,
            "bytes_written": int,
            "content_hash": str (SHA256),
            "error": str (if failed)
        }
    """
    # Validate path
    is_valid, reason = _validate_path(file_path, allowed_dirs)
    if not is_valid:
        return {
            "status": "error",
            "error": reason,
            "message": "Access denied: path outside allowed directories",
        }

    # Validate content size
    content_bytes = content.encode(encoding)
    max_bytes = max_size_mb * 1024 * 1024
    if len(content_bytes) > max_bytes:
        return {
            "status": "error",
            "error": "content_too_large",
            "content_size_bytes": len(content_bytes),
            "max_bytes": max_bytes,
        }

    # Check encoding support
    if encoding not in ("utf-8", "ascii", "latin-1", "utf-16"):
        return {
            "status": "error",
            "error": "unsupported_encoding",
            "encoding": encoding,
        }

    abs_path = os.path.abspath(os.path.expanduser(file_path))
    parent_dir = os.path.dirname(abs_path)

    try:
        # Create parent directories if needed
        if create_dirs and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Check parent directory exists
        if not os.path.exists(parent_dir):
            return {
                "status": "error",
                "error": "parent_directory_not_found",
                "parent_dir": parent_dir,
            }

        # Write file
        with open(abs_path, "w", encoding=encoding) as f:
            f.write(content)

        # Calculate hash
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        return {
            "status": "success",
            "file_path": abs_path,
            "bytes_written": len(content_bytes),
            "content_hash": content_hash,
            "encoding": encoding,
        }

    except PermissionError:
        return {
            "status": "error",
            "error": "permission_denied",
            "file_path": abs_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": "write_failed",
            "file_path": abs_path,
            "message": str(e),
        }


async def list_directory(
    dir_path: str,
    recursive: bool = False,
    allowed_dirs: Optional[List[str]] = None,
) -> dict:
    """
    List contents of a directory (sandboxed).

    Args:
        dir_path: Path to directory
        recursive: Whether to list recursively
        allowed_dirs: Allowed base directories for sandboxing

    Returns:
        {
            "status": "success" | "error",
            "dir_path": str,
            "files": list of {"name", "type", "size_bytes", "path"},
            "error": str (if failed)
        }
    """
    # Validate path
    is_valid, reason = _validate_path(dir_path, allowed_dirs)
    if not is_valid:
        return {
            "status": "error",
            "error": reason,
            "message": "Access denied: path outside allowed directories",
        }

    abs_path = os.path.abspath(os.path.expanduser(dir_path))

    if not os.path.exists(abs_path):
        return {
            "status": "error",
            "error": "directory_not_found",
            "dir_path": abs_path,
        }

    if not os.path.isdir(abs_path):
        return {
            "status": "error",
            "error": "path_is_not_directory",
            "dir_path": abs_path,
        }

    try:
        files = []

        if recursive:
            for root, dirs, filenames in os.walk(abs_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(file_path)
                        files.append({
                            "name": filename,
                            "type": "file",
                            "size_bytes": size,
                            "path": file_path,
                        })
                    except (OSError, PermissionError):
                        pass

                for dirname in dirs:
                    dir_full_path = os.path.join(root, dirname)
                    files.append({
                        "name": dirname,
                        "type": "directory",
                        "size_bytes": 0,
                        "path": dir_full_path,
                    })
        else:
            for item in os.listdir(abs_path):
                item_path = os.path.join(abs_path, item)
                try:
                    if os.path.isdir(item_path):
                        files.append({
                            "name": item,
                            "type": "directory",
                            "size_bytes": 0,
                            "path": item_path,
                        })
                    else:
                        size = os.path.getsize(item_path)
                        files.append({
                            "name": item,
                            "type": "file",
                            "size_bytes": size,
                            "path": item_path,
                        })
                except (OSError, PermissionError):
                    pass

        return {
            "status": "success",
            "dir_path": abs_path,
            "file_count": len([f for f in files if f["type"] == "file"]),
            "dir_count": len([f for f in files if f["type"] == "directory"]),
            "files": files,
        }

    except PermissionError:
        return {
            "status": "error",
            "error": "permission_denied",
            "dir_path": abs_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": "list_failed",
            "dir_path": abs_path,
            "message": str(e),
        }


async def delete_file(
    file_path: str,
    allowed_dirs: Optional[List[str]] = None,
) -> dict:
    """
    Delete a file (sandboxed).

    Args:
        file_path: Path to file
        allowed_dirs: Allowed base directories for sandboxing

    Returns:
        {
            "status": "success" | "error",
            "file_path": str,
            "error": str (if failed)
        }
    """
    # Validate path
    is_valid, reason = _validate_path(file_path, allowed_dirs)
    if not is_valid:
        return {
            "status": "error",
            "error": reason,
            "message": "Access denied: path outside allowed directories",
        }

    abs_path = os.path.abspath(os.path.expanduser(file_path))

    if not os.path.exists(abs_path):
        return {
            "status": "error",
            "error": "file_not_found",
            "file_path": abs_path,
        }

    if not os.path.isfile(abs_path):
        return {
            "status": "error",
            "error": "path_is_not_file",
            "file_path": abs_path,
        }

    try:
        os.remove(abs_path)
        return {
            "status": "success",
            "file_path": abs_path,
        }
    except PermissionError:
        return {
            "status": "error",
            "error": "permission_denied",
            "file_path": abs_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": "delete_failed",
            "file_path": abs_path,
            "message": str(e),
        }
