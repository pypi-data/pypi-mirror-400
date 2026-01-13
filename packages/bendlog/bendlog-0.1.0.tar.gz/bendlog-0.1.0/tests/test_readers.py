"""Tests for bendlog.readers module."""

import gzip
import io
import tarfile
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import zstandard as zstd

from bendlog.readers import read_lines


class TestReadLinesPlainText:
    """Tests for reading plain text files."""

    def test_read_simple_file(self, tmp_path: Path):
        """Read a simple text file."""
        file = tmp_path / "test.txt"
        file.write_text("line1\nline2\nline3\n")

        result = list(read_lines(str(file)))

        assert result == ["line1", "line2", "line3"]

    def test_read_file_without_trailing_newline(self, tmp_path: Path):
        """Read a file without trailing newline."""
        file = tmp_path / "test.txt"
        file.write_text("line1\nline2")

        result = list(read_lines(str(file)))

        assert result == ["line1", "line2"]

    def test_read_empty_file(self, tmp_path: Path):
        """Read an empty file."""
        file = tmp_path / "empty.txt"
        file.write_text("")

        result = list(read_lines(str(file)))

        assert result == []

    def test_read_file_with_crlf(self, tmp_path: Path):
        """Read a file with Windows line endings."""
        file = tmp_path / "test.txt"
        file.write_bytes(b"line1\r\nline2\r\n")

        result = list(read_lines(str(file)))

        assert result == ["line1", "line2"]

    def test_file_not_found(self):
        """Raise FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            list(read_lines("/nonexistent/file.txt"))


class TestReadLinesZstd:
    """Tests for reading zstandard compressed files."""

    def test_read_zstd_file(self, tmp_path: Path):
        """Read a zstd compressed file."""
        file = tmp_path / "test.log.zst"
        content = b"line1\nline2\nline3\n"

        cctx = zstd.ZstdCompressor()
        compressed = cctx.compress(content)
        file.write_bytes(compressed)

        result = list(read_lines(str(file)))

        assert result == ["line1", "line2", "line3"]

    def test_read_zstd_empty(self, tmp_path: Path):
        """Read an empty zstd compressed file."""
        file = tmp_path / "empty.zst"
        content = b""

        cctx = zstd.ZstdCompressor()
        compressed = cctx.compress(content)
        file.write_bytes(compressed)

        result = list(read_lines(str(file)))

        assert result == []


class TestReadLinesTarGz:
    """Tests for reading tar.gz archives."""

    def test_read_tar_gz_single_file(self, tmp_path: Path):
        """Read a tar.gz with single file."""
        archive = tmp_path / "test.tar.gz"
        content = b"line1\nline2\n"

        with tarfile.open(archive, 'w:gz') as tar:
            info = tarfile.TarInfo(name="test.log")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

        result = list(read_lines(str(archive)))

        assert result == ["line1", "line2"]

    def test_read_tar_gz_multiple_files(self, tmp_path: Path):
        """Read a tar.gz with multiple files."""
        archive = tmp_path / "test.tar.gz"
        content1 = b"file1_line1\nfile1_line2\n"
        content2 = b"file2_line1\n"

        with tarfile.open(archive, 'w:gz') as tar:
            info1 = tarfile.TarInfo(name="file1.log")
            info1.size = len(content1)
            tar.addfile(info1, io.BytesIO(content1))

            info2 = tarfile.TarInfo(name="file2.log")
            info2.size = len(content2)
            tar.addfile(info2, io.BytesIO(content2))

        result = list(read_lines(str(archive)))

        assert result == ["file1_line1", "file1_line2", "file2_line1"]

    def test_read_tgz_extension(self, tmp_path: Path):
        """Read a .tgz file (same as .tar.gz)."""
        archive = tmp_path / "test.tgz"
        content = b"line1\n"

        with tarfile.open(archive, 'w:gz') as tar:
            info = tarfile.TarInfo(name="test.log")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

        result = list(read_lines(str(archive)))

        assert result == ["line1"]

    def test_read_tar_gz_skips_directories(self, tmp_path: Path):
        """Skip directories in tar.gz archive."""
        archive = tmp_path / "test.tar.gz"
        content = b"line1\n"

        with tarfile.open(archive, 'w:gz') as tar:
            # Add a directory
            dir_info = tarfile.TarInfo(name="subdir")
            dir_info.type = tarfile.DIRTYPE
            tar.addfile(dir_info)

            # Add a file
            info = tarfile.TarInfo(name="subdir/test.log")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

        result = list(read_lines(str(archive)))

        assert result == ["line1"]


class TestReadLinesStdin:
    """Tests for reading from stdin."""

    def test_read_from_stdin_none(self):
        """Read from stdin when source is None."""
        mock_stdin = io.StringIO("line1\nline2\n")

        with mock.patch('sys.stdin', mock_stdin):
            result = list(read_lines(None))

        assert result == ["line1", "line2"]

    def test_read_from_stdin_dash(self):
        """Read from stdin when source is '-'."""
        mock_stdin = io.StringIO("line1\nline2\n")

        with mock.patch('sys.stdin', mock_stdin):
            result = list(read_lines('-'))

        assert result == ["line1", "line2"]
