"""File reading utilities for various input formats."""

import sys
import tarfile
from typing import Iterator

import zstandard as zstd


def read_lines(source: str | None) -> Iterator[str]:
    """Read lines from various input sources.

    Args:
        source: Input source. Can be:
            - None or '-': Read from stdin
            - 'file.txt': Plain text file
            - 'file.zst' or 'file.log.zst': Zstandard compressed file
            - 'file.tar.gz' or 'file.tgz': Tar gzip archive (yields lines from all files)

    Yields:
        Each line from the input (stripped of trailing newline).

    Raises:
        FileNotFoundError: If the specified file does not exist.
        zstandard.ZstdError: If zstd decompression fails.
        tarfile.TarError: If tar.gz extraction fails.
    """
    if source is None or source == '-':
        yield from _read_stdin()
    elif source.endswith('.zst'):
        yield from _read_zstd(source)
    elif source.endswith('.tar.gz') or source.endswith('.tgz'):
        yield from _read_tar_gz(source)
    else:
        yield from _read_text(source)


def _read_stdin() -> Iterator[str]:
    """Read lines from stdin."""
    for line in sys.stdin:
        yield line.rstrip('\n\r')


def _read_text(path: str) -> Iterator[str]:
    """Read lines from a plain text file."""
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.rstrip('\n\r')


def _read_zstd(path: str) -> Iterator[str]:
    """Read lines from a zstandard compressed file."""
    dctx = zstd.ZstdDecompressor()
    with open(path, 'rb') as f:
        with dctx.stream_reader(f) as reader:
            text_stream = reader.read().decode('utf-8')
            for line in text_stream.splitlines():
                yield line


def _read_tar_gz(path: str) -> Iterator[str]:
    """Read lines from all files in a tar.gz archive."""
    with tarfile.open(path, 'r:gz') as tar:
        for member in tar:
            if not member.isfile():
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            for line in f:
                yield line.decode('utf-8').rstrip('\n\r')
