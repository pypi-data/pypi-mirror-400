"""Helpers for working with spaCy pipelines.

This module provides utilities for loading and configuring spaCy language
models, ensuring they have the necessary components for moodswing's
sentiment analysis workflows.

Key functions:
    - :func:`load_spacy_model`: Load a spaCy model with caching
    - :func:`ensure_sentence_boundaries`: Add sentence segmentation if needed
    - :func:`ensure_sentiment_component`: Add TextBlob sentiment if available

Caching behavior:
    The ``load_spacy_model`` function caches up to 8 models using
    ``@lru_cache(maxsize=8)``. This prevents reloading models on every
    analyzer instantiation. Models are cached by their name/path string,
    so loading the same model multiple times returns the cached instance.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import spacy
from spacy.language import Language

_SPACYTEXTBLOB_CLASS: Any | None | bool = None

_DEFAULT_MODEL = "en_core_web_sm"


@lru_cache(maxsize=8)
def load_spacy_model(model: str = _DEFAULT_MODEL) -> Language:
    """
    Return a spaCy language pipeline, caching instances for reuse.

    Up to 8 models are cached. This prevents expensive reloading when
    the same model is used repeatedly. If you need more than 8 different
    models in a single session, the least recently used will be evicted.
    """
    try:
        return spacy.load(model)
    except OSError:
        # Fallback to a lightweight English pipeline when the default
        # model is not available locally. Users can always install the
        # official model for higher quality predictions.
        if model != _DEFAULT_MODEL:
            raise
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp


def ensure_sentence_boundaries(nlp: Language) -> None:
    """Guarantee that the provided pipeline can emit sentence spans."""
    if {"parser", "senter"}.intersection(nlp.pipe_names):
        return
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")


def ensure_sentiment_component(nlp: Language) -> bool:
    """Attach a lightweight sentiment component if possible.

    Returns True when a helper such as spaCyTextBlob is active.
    """

    cls = _resolve_spacytextblob()
    if cls is None:
        return False

    if "spacytextblob" in nlp.pipe_names:
        return True

    try:
        nlp.add_pipe("spacytextblob")
        return True
    except Exception:
        try:
            nlp.add_pipe(cls(nlp))  # type: ignore[misc]
            return True
        except Exception:
            return False


def _resolve_spacytextblob() -> Any | None:
    global _SPACYTEXTBLOB_CLASS
    if _SPACYTEXTBLOB_CLASS is None:
        try:
            from spacytextblob.spacytextblob import SpacyTextBlob as _cls
        except Exception:
            _SPACYTEXTBLOB_CLASS = False
        else:
            _SPACYTEXTBLOB_CLASS = _cls
    return None if _SPACYTEXTBLOB_CLASS is False else _SPACYTEXTBLOB_CLASS
