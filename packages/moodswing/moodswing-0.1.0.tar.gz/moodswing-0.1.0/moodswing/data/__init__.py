"""Helpers for accessing packaged sample texts and local corpora.

This module provides utilities for loading text data, either from the
bundled sample corpus or from local files/directories. The bundled texts
are cached in memory on first access for performance.

Key functions:
    - :func:`list_sample_texts`: List available bundled sample text IDs
    - :func:`load_sample_text`: Load a specific bundled text by ID
    - :func:`iter_sample_texts`: Iterate over all bundled texts
    - :func:`load_text_file`: Read a single .txt file
    - :func:`load_text_directory`: Read all .txt files from a directory

Caching behavior:
    The bundled sample texts are loaded once and cached indefinitely using
    ``@lru_cache(maxsize=None)``. This means the first access reads from
    disk, but subsequent accesses return the cached data. If you modify
    the pickle file, you'll need to restart Python to see changes.
"""
from __future__ import annotations

import pickle
import re
import unicodedata
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, Iterator, Mapping, Tuple

from ..text.tokens import normalize_quotes

_TEXT_PACKAGE = "moodswing.data.text"
_DEFAULT_SAMPLE = "sample_novels.pkl"


@lru_cache(maxsize=None)
def _load_records(filename: str) -> Tuple[Mapping[str, Any], ...]:
    """
    Load and cache sample text records from bundled pickle.

    This function uses @lru_cache to ensure the pickle file is only
    read once per filename. The cached result persists for the lifetime
    of the Python process.
    """
    resource = resources.files(_TEXT_PACKAGE).joinpath(filename)
    with resource.open("rb") as handle:
        data = pickle.load(handle)
    if not isinstance(data, list):  # pragma: no cover - defensive
        raise TypeError(
            f"Expected a list of records in {filename}, got {type(data)!r}"
        )
    # Convert to tuple so the cached value is immutable.
    return tuple(data)


def _normalize_entry(entry: Mapping[str, Any]) -> Tuple[str, str] | None:
    doc_id = str(entry.get("doc_id") or "doc").strip()
    text = str(entry.get("text") or "").strip()
    if not text:
        return None
    return (doc_id or "doc", text)


def iter_sample_texts(
        filename: str = _DEFAULT_SAMPLE
) -> Iterator[Tuple[str, str]]:
    """
    Yield ``(doc_id, text)`` pairs from the bundled sample corpus.

    Parameters
    ----------
    filename : str, optional
        Name of the pickled corpus file to load.

    Yields
    ------
    tuple[str, str]
        Document ID and text content pairs.
    """

    for entry in _load_records(filename):
        normalized = _normalize_entry(entry)
        if normalized is None:
            continue
        yield normalized


def list_sample_texts(
        filename: str = _DEFAULT_SAMPLE
) -> list[str]:
    """
    Return a list of available document IDs from the bundled sample corpus.

    Parameters
    ----------
    filename : str, optional
        Name of the pickled corpus file to query.

    Returns
    -------
    list[str]
        Document IDs of all available sample texts.

    Examples
    --------
    >>> from moodswing.data import list_sample_texts
    >>> available = list_sample_texts()
    >>> print(available)
    ['madame_bovary', 'portrait_of_the_artist', ...]
    """
    return [doc_id for doc_id, _ in iter_sample_texts(filename)]


def load_sample_text(
        doc_id: str | None = None,
        *,
        filename: str = _DEFAULT_SAMPLE
) -> Tuple[str, str]:
    """
    Return a single ``(doc_id, text)`` pair from the bundled sample corpus.

    Parameters
    ----------
    doc_id : str, optional
        Specific document ID to retrieve. If ``None``, returns the first
        available text.
    filename : str, optional
        Name of the pickled corpus file to load.

    Returns
    -------
    tuple[str, str]
        Document ID and text content.

    Raises
    ------
    ValueError
        If the requested ``doc_id`` is not found in the corpus.
    RuntimeError
        If the corpus is empty.

    Examples
    --------
    >>> from moodswing.data import load_sample_text, list_sample_texts
    >>> # See what's available
    >>> print(list_sample_texts())
    >>> # Load a specific text
    >>> doc_id, text = load_sample_text("madame_bovary")
    """

    for current_id, text in iter_sample_texts(filename):
        if doc_id is None or current_id == doc_id:
            return current_id, text
    available = ", ".join(doc for doc, _ in iter_sample_texts(filename))
    if doc_id is None:
        raise RuntimeError("No bundled sample texts are available.")
    raise ValueError(
        f"Sample text '{doc_id}' not found. Available IDs: {available or 'none'}. "  # noqa: E501
        f"Use list_sample_texts() to see all available texts."
    )


def load_text_file(
        path: str | Path,
        *,
        strict_ascii: bool = True
) -> dict[str, str]:
    """
    Read a single ``.txt`` file and return a cleaned ``{doc_id, text}`` record.

    Parameters
    ----------
    path : str | Path
        File to read.
    strict_ascii : bool, optional
        Drop non-ASCII bytes when ``True`` (default) to sidestep spaCy model
        quirks on unusual characters.
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    if not file_path.is_file():
        raise ValueError(f"'{file_path}' is not a file")
    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    cleaned = _clean_text(raw, strict_ascii=strict_ascii)
    return {"doc_id": _build_doc_id(file_path), "text": cleaned}


def load_text_directory(
        directory: str | Path,
        *,
        strict_ascii: bool = True
) -> list[dict[str, str]]:
    """
    Read every ``.txt`` file placed directly inside ``directory``.

    Parameters
    ----------
    directory : str | Path
        Folder containing text files. Subdirectories are ignored for safety.
    strict_ascii : bool, optional
        Passed through to :func:`load_text_file`.
    """

    base = Path(directory)
    if not base.exists():
        raise FileNotFoundError(base)
    if not base.is_dir():
        raise NotADirectoryError(base)
    records: list[dict[str, str]] = []
    for child in sorted(base.iterdir()):
        if not child.is_file():
            continue
        if child.suffix.lower() != ".txt":
            continue
        records.append(load_text_file(child, strict_ascii=strict_ascii))
    return records


def _clean_text(text: str, *, strict_ascii: bool) -> str:
    text = normalize_quotes(text)
    text = " ".join(text.split())
    text = text.strip()
    if strict_ascii:
        normalized = unicodedata.normalize("NFKD", text)
        text = normalized.encode("ascii", "ignore").decode("ascii")
    return text


def _build_doc_id(path: Path) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "_", path.stem.strip())
    slug = slug.strip("_")
    return slug.lower() or "doc"
