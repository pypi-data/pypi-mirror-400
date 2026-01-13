"""High-level package interface for moodswing."""
from __future__ import annotations

from ._version import __version__
from .lexicons import LexiconLoader, default_dictionary_root
from .sentiment import (
    DictionarySentimentAnalyzer,
    MixedMessageResult,
    SpaCySentimentAnalyzer
)
from .data import (
    iter_sample_texts,
    list_sample_texts,
    load_sample_text,
    load_text_directory,
    load_text_file
)
from .text import (
    Sentencizer,
    SpaCySentencizer,
    Tokenizer,
    sentencize,
    tokenize_words
    )
from .transforms import DCTTransform, rolling_mean
from .viz import (
    TrajectoryComponents,
    plot_trajectory,
    prepare_trajectory,
    trajectory_to_dataframe
)

__all__ = [
    "__version__",
    "DictionarySentimentAnalyzer",
    "DCTTransform",
    "LexiconLoader",
    "MixedMessageResult",
    "Sentencizer",
    "SpaCySentencizer",
    "SpaCySentimentAnalyzer",
    "Tokenizer",
    "TrajectoryComponents",
    "default_dictionary_root",
    "iter_sample_texts",
    "list_sample_texts",
    "load_sample_text",
    "load_text_directory",
    "load_text_file",
    "plot_trajectory",
    "prepare_trajectory",
    "rolling_mean",
    "sentencize",
    "tokenize_words",
    "trajectory_to_dataframe",
]
