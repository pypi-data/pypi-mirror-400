"""Helpers for loading dictionary-based lexicons from packaged resources."""
from __future__ import annotations

from dataclasses import dataclass
import os
import pickle
from pathlib import Path
from typing import BinaryIO, Dict, List, Mapping, MutableMapping

from importlib import resources

from .types import EmotionLexicon, LexiconMetadata, SentimentLexicon

_DEFAULT_RESOURCE_MAP: Mapping[str, tuple[str, str]] = {
    "afinn": ("afinn.pkl", "valence"),
    "bing": ("bing.pkl", "valence"),
    "syuzhet": ("syuzhet_dict.pkl", "valence"),
    "nrc": ("nrc.pkl", "emotion"),
}


@dataclass(slots=True)
class LexiconLoader:
    """
    Resolve lexicons by name, falling back to packaged CSV assets.
    """

    base_dir: Path | None = None
    registry: MutableMapping[str, tuple[str, str]] | None = None

    def __post_init__(self) -> None:
        if self.base_dir is None:
            self.base_dir = default_dictionary_root()
        if self.registry is None:
            self.registry = dict(_DEFAULT_RESOURCE_MAP)

    def register(self, name: str, file_path: str | Path, kind: str) -> None:
        self.registry[name] = (str(file_path), kind)

    def load(
            self, name: str,
            *,
            language: str = "english"
    ) -> SentimentLexicon | EmotionLexicon:
        descriptor = self._resolve(name)
        if descriptor is None:
            raise ValueError(f"Unknown lexicon: {name}")
        resource, kind = descriptor
        if kind == "valence":
            with self._open_resource(resource) as handle:
                return _load_valence(handle, name=name, language=language)
        if kind == "emotion":
            with self._open_resource(resource) as handle:
                return _load_emotion(handle, name=name, language=language)
        raise ValueError(f"Unsupported lexicon kind '{kind}' for '{name}'")

    def _resolve(self, name: str) -> tuple[str, str] | None:
        if self.registry is None:
            return None
        return self.registry.get(name)

    def _open_resource(self, filename: str) -> BinaryIO:
        candidate = Path(filename)
        if candidate.is_absolute():
            return candidate.open("rb")
        if self.base_dir is not None:
            path = Path(self.base_dir) / filename
            return path.open("rb")
        data_root = resources.files(
            "moodswing.data.lexicons"
            ).joinpath(filename)
        return data_root.open("rb")


def default_dictionary_root() -> Path | None:
    """Locate the directory that stores raw dictionary CSV files."""
    env_override = os.environ.get("MOODSWING_DICT_DIR")
    if env_override:
        candidate = Path(env_override)
        if candidate.exists():
            return candidate
    return None


def _load_valence(
        handle: BinaryIO,
        *,
        name: str, language: str
        ) -> SentimentLexicon:
    values: Dict[str, float] = {}
    for row in _load_rows(handle):
        word = row.get("word") if isinstance(row, dict) else None
        value = row.get("value") if isinstance(row, dict) else None
        if not word or value is None:
            continue
        try:
            values[word.strip()] = float(value)
        except (TypeError, ValueError):
            continue
    metadata = LexiconMetadata(name=name, language=language)
    return SentimentLexicon(metadata=metadata, values=values)


def _load_emotion(
        handle: BinaryIO,
        *,
        name: str,
        language: str
) -> EmotionLexicon:
    """
    Load an emotion lexicon from pickled data.

    Filters rows to match the specified language and validates data format.
    Invalid rows (wrong type, missing fields, or non-numeric values) are
    silently skipped.
    """
    matrix: Dict[str, Dict[str, float]] = {}
    normalized_language = language.lower()
    total_rows = 0
    skipped_language = 0
    skipped_invalid = 0

    for row in _load_rows(handle):
        total_rows += 1
        if not isinstance(row, dict):
            skipped_invalid += 1
            continue
        lang = row.get("lang")
        if lang is None or lang.lower() != normalized_language:
            skipped_language += 1
            continue
        word = row.get("word")
        sentiment = row.get("sentiment")
        value = row.get("value")
        if not word or not sentiment or value is None:
            skipped_invalid += 1
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            skipped_invalid += 1
            continue
        entry = matrix.setdefault(word.strip(), {})
        entry[str(sentiment).strip()] = numeric_value

    # Log statistics if debugging or if result is suspiciously small
    if not matrix:
        import warnings
        warnings.warn(
            f"Emotion lexicon '{name}' for language '{language}' is empty. "
            f"Processed {total_rows} rows: {skipped_language} wrong language, "
            f"{skipped_invalid} invalid format.",
            UserWarning,
            stacklevel=3
        )

    metadata = LexiconMetadata(name=name, language=language)
    return EmotionLexicon(metadata=metadata, matrix=matrix)


def _load_rows(handle: BinaryIO) -> List[Mapping[str, object]]:
    rows = pickle.load(handle)
    if not isinstance(rows, list):  # pragma: no cover - defensive
        raise TypeError(
            f"Expected list-based pickle payload, received {type(rows)!r}"
        )
    return rows
