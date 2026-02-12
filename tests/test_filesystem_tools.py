"""Tests for sandboxed filesystem tools."""

import os
import tempfile
import pytest

from anse.tools.filesystem import (
    read_file,
    write_file,
    list_directory,
    delete_file,
    _validate_path,
    DEFAULT_ALLOWED_DIRS,
)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestPathValidation:
    """Test path validation security."""

    def test_validate_path_valid(self):
        """Test validation of valid paths."""
        # Use a test-specific allowed dir
        allowed = [tempfile.gettempdir()]
        is_valid, _ = _validate_path(os.path.join(tempfile.gettempdir(), "test.txt"), allowed)
        assert is_valid

    def test_validate_path_invalid_escape(self):
        """Test that path escape attempts are blocked."""
        # Try to escape to parent directory
        allowed = [tempfile.gettempdir()]
        is_valid, _ = _validate_path("/etc/passwd", allowed)
        assert not is_valid

    def test_validate_path_with_symlink(self):
        """Test validation with symlinks (should follow symlinks)."""
        # Create a temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            allowed = [tmpdir]
            is_valid, _ = _validate_path(os.path.join(tmpdir, "subdir", "file.txt"), allowed)
            assert is_valid


class TestReadFile:
    """Test read_file functionality."""

    @pytest.mark.asyncio
    async def test_read_file_success(self, temp_workspace):
        """Test successful file read."""
        # Write a test file
        test_file = os.path.join(temp_workspace, "test.txt")
        test_content = "Hello, World!"
        with open(test_file, "w") as f:
            f.write(test_content)

        # Read it
        result = await read_file(test_file, allowed_dirs=[temp_workspace])
        assert result["status"] == "success"
        assert result["content"] == test_content
        assert result["size_bytes"] == len(test_content)
        assert "content_hash" in result

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, temp_workspace):
        """Test reading non-existent file."""
        result = await read_file(
            os.path.join(temp_workspace, "nonexistent.txt"),
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "error"
        assert result["error"] == "file_not_found"

    @pytest.mark.asyncio
    async def test_read_file_outside_allowed_dir(self, temp_workspace):
        """Test that reading outside allowed dirs is blocked."""
        result = await read_file("/etc/passwd", allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_outside_allowed_dirs"

    @pytest.mark.asyncio
    async def test_read_file_too_large(self, temp_workspace):
        """Test that oversized files are rejected."""
        # Create a 20MB file (exceeds 10MB default limit)
        test_file = os.path.join(temp_workspace, "large.txt")
        with open(test_file, "w") as f:
            f.write("x" * (20 * 1024 * 1024))

        result = await read_file(test_file, allowed_dirs=[temp_workspace], max_size_mb=10)
        assert result["status"] == "error"
        assert result["error"] == "file_too_large"

    @pytest.mark.asyncio
    async def test_read_file_custom_encoding(self, temp_workspace):
        """Test reading with custom encoding."""
        test_file = os.path.join(temp_workspace, "test.txt")
        test_content = "Hello, World!"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        result = await read_file(test_file, encoding="utf-8", allowed_dirs=[temp_workspace])
        assert result["status"] == "success"
        assert result["encoding"] == "utf-8"

    @pytest.mark.asyncio
    async def test_read_file_invalid_encoding(self, temp_workspace):
        """Test reading with invalid encoding."""
        test_file = os.path.join(temp_workspace, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        result = await read_file(test_file, encoding="invalid", allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "unsupported_encoding"

    @pytest.mark.asyncio
    async def test_read_directory_error(self, temp_workspace):
        """Test reading a directory returns error."""
        result = await read_file(temp_workspace, allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_is_not_file"


class TestWriteFile:
    """Test write_file functionality."""

    @pytest.mark.asyncio
    async def test_write_file_success(self, temp_workspace):
        """Test successful file write."""
        test_file = os.path.join(temp_workspace, "output.txt")
        content = "Test content"

        result = await write_file(test_file, content, allowed_dirs=[temp_workspace])
        assert result["status"] == "success"
        assert result["bytes_written"] == len(content)
        assert "content_hash" in result

        # Verify file was written
        with open(test_file) as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_write_file_create_dirs(self, temp_workspace):
        """Test creating parent directories."""
        test_file = os.path.join(temp_workspace, "subdir", "file.txt")
        content = "Test"

        result = await write_file(
            test_file,
            content,
            create_dirs=True,
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "success"
        assert os.path.exists(test_file)

    @pytest.mark.asyncio
    async def test_write_file_no_create_dirs(self, temp_workspace):
        """Test write fails when parent dir doesn't exist."""
        test_file = os.path.join(temp_workspace, "nonexistent", "file.txt")
        content = "Test"

        result = await write_file(
            test_file,
            content,
            create_dirs=False,
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "error"
        assert result["error"] == "parent_directory_not_found"

    @pytest.mark.asyncio
    async def test_write_file_outside_allowed_dir(self, temp_workspace):
        """Test that writing outside allowed dirs is blocked."""
        result = await write_file("/etc/test.txt", "content", allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_outside_allowed_dirs"

    @pytest.mark.asyncio
    async def test_write_file_too_large(self, temp_workspace):
        """Test that oversized content is rejected."""
        test_file = os.path.join(temp_workspace, "large.txt")
        content = "x" * (150 * 1024 * 1024)  # 150MB

        result = await write_file(
            test_file,
            content,
            max_size_mb=100,
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "error"
        assert result["error"] == "content_too_large"

    @pytest.mark.asyncio
    async def test_write_file_overwrite(self, temp_workspace):
        """Test overwriting existing file."""
        test_file = os.path.join(temp_workspace, "test.txt")
        
        # Write first version
        result1 = await write_file(test_file, "Version 1", allowed_dirs=[temp_workspace])
        assert result1["status"] == "success"

        # Overwrite with second version
        result2 = await write_file(test_file, "Version 2", allowed_dirs=[temp_workspace])
        assert result2["status"] == "success"

        # Verify content
        with open(test_file) as f:
            assert f.read() == "Version 2"


class TestListDirectory:
    """Test list_directory functionality."""

    @pytest.mark.asyncio
    async def test_list_directory_success(self, temp_workspace):
        """Test successful directory listing."""
        # Create some files
        open(os.path.join(temp_workspace, "file1.txt"), "w").close()
        open(os.path.join(temp_workspace, "file2.txt"), "w").close()
        os.mkdir(os.path.join(temp_workspace, "subdir"))

        result = await list_directory(temp_workspace, allowed_dirs=[temp_workspace])
        assert result["status"] == "success"
        assert result["file_count"] == 2
        assert result["dir_count"] == 1

    @pytest.mark.asyncio
    async def test_list_directory_recursive(self, temp_workspace):
        """Test recursive directory listing."""
        # Create nested structure
        open(os.path.join(temp_workspace, "file1.txt"), "w").close()
        os.mkdir(os.path.join(temp_workspace, "subdir"))
        open(os.path.join(temp_workspace, "subdir", "file2.txt"), "w").close()

        result = await list_directory(
            temp_workspace,
            recursive=True,
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "success"
        assert result["file_count"] >= 2  # At least file1.txt and file2.txt

    @pytest.mark.asyncio
    async def test_list_directory_not_found(self, temp_workspace):
        """Test listing non-existent directory."""
        result = await list_directory(
            os.path.join(temp_workspace, "nonexistent"),
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "error"
        assert result["error"] == "directory_not_found"

    @pytest.mark.asyncio
    async def test_list_directory_outside_allowed(self, temp_workspace):
        """Test listing outside allowed dirs is blocked."""
        result = await list_directory("/etc", allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_outside_allowed_dirs"

    @pytest.mark.asyncio
    async def test_list_file_error(self, temp_workspace):
        """Test listing a file returns error."""
        test_file = os.path.join(temp_workspace, "test.txt")
        open(test_file, "w").close()

        result = await list_directory(test_file, allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_is_not_directory"


class TestDeleteFile:
    """Test delete_file functionality."""

    @pytest.mark.asyncio
    async def test_delete_file_success(self, temp_workspace):
        """Test successful file deletion."""
        test_file = os.path.join(temp_workspace, "test.txt")
        open(test_file, "w").close()

        assert os.path.exists(test_file)

        result = await delete_file(test_file, allowed_dirs=[temp_workspace])
        assert result["status"] == "success"
        assert not os.path.exists(test_file)

    @pytest.mark.asyncio
    async def test_delete_file_not_found(self, temp_workspace):
        """Test deleting non-existent file."""
        result = await delete_file(
            os.path.join(temp_workspace, "nonexistent.txt"),
            allowed_dirs=[temp_workspace],
        )
        assert result["status"] == "error"
        assert result["error"] == "file_not_found"

    @pytest.mark.asyncio
    async def test_delete_directory_error(self, temp_workspace):
        """Test deleting a directory returns error."""
        subdir = os.path.join(temp_workspace, "subdir")
        os.mkdir(subdir)

        result = await delete_file(subdir, allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_is_not_file"

    @pytest.mark.asyncio
    async def test_delete_file_outside_allowed(self, temp_workspace):
        """Test that deleting outside allowed dirs is blocked."""
        result = await delete_file("/etc/test.txt", allowed_dirs=[temp_workspace])
        assert result["status"] == "error"
        assert result["error"] == "path_outside_allowed_dirs"


class TestIntegration:
    """Integration tests combining multiple operations."""

    @pytest.mark.asyncio
    async def test_write_read_cycle(self, temp_workspace):
        """Test writing and reading back."""
        test_file = os.path.join(temp_workspace, "cycle_test.txt")
        original_content = "Test content with special chars: äöü 中文 🎉"

        # Write
        write_result = await write_file(
            test_file,
            original_content,
            encoding="utf-8",
            allowed_dirs=[temp_workspace],
        )
        assert write_result["status"] == "success"

        # Read back
        read_result = await read_file(
            test_file,
            encoding="utf-8",
            allowed_dirs=[temp_workspace],
        )
        assert read_result["status"] == "success"
        assert read_result["content"] == original_content
        assert read_result["content_hash"] == write_result["content_hash"]

    @pytest.mark.asyncio
    async def test_list_and_delete_cycle(self, temp_workspace):
        """Test listing and deleting files."""
        # Create files
        for i in range(3):
            open(os.path.join(temp_workspace, f"file{i}.txt"), "w").close()

        # List
        list_result = await list_directory(temp_workspace, allowed_dirs=[temp_workspace])
        assert list_result["file_count"] == 3

        # Delete one
        delete_result = await delete_file(
            os.path.join(temp_workspace, "file0.txt"),
            allowed_dirs=[temp_workspace],
        )
        assert delete_result["status"] == "success"

        # List again
        list_result2 = await list_directory(temp_workspace, allowed_dirs=[temp_workspace])
        assert list_result2["file_count"] == 2
