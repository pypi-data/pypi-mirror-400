"""Sentence boundary detection helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from nltk import data as nltk_data
from nltk import download as nltk_download
from nltk.tokenize import PunktSentenceTokenizer

from .tokens import _ensure_text_sequence, normalize_quotes

_SENTENCE_CACHE: Dict[str, PunktSentenceTokenizer] = {}
_PUNKT_RESOURCES = ("punkt", "punkt_tab")

# Common NLTK Punkt languages - not exhaustive but covers most use cases
_COMMON_PUNKT_LANGUAGES = {
    "czech", "danish", "dutch", "english", "estonian", "finnish", "french",
    "german", "greek", "italian", "norwegian", "polish", "portuguese",
    "slovene", "spanish", "swedish", "turkish"
}


@dataclass(slots=True)
class Sentencizer:
    """
    Sentence splitter backed by NLTK's Punkt models.

    Parameters
    ----------
    fix_curly_quotes : bool, optional
        When ``True`` (default) normalize curly quotes before tokenization.
    strip_whitespace : bool, optional
        Remove leading/trailing whitespace from each detected sentence.
    drop_empty : bool, optional
        Omit empty strings that can result from aggressive stripping.
    language : str, optional
        Language identifier used when loading the Punkt model. Defaults to
        ``"english"``. Common supported languages include: czech, danish,
        dutch, english, estonian, finnish, french, german, greek, italian,
        norwegian, polish, portuguese, slovene, spanish, swedish, turkish.
        The tokenizer will attempt to download the model if not available.
    """

    fix_curly_quotes: bool = True
    strip_whitespace: bool = True
    drop_empty: bool = True
    language: str = "english"

    def split(self, text: str | Sequence[str]) -> List[str]:
        """
        Split raw text (or text chunks) into sentences.

        Parameters
        ----------
        text : str | Sequence[str]
            Full document or iterable of text segments to process.

        Returns
        -------
        list[str]
            Sentences extracted by the configured Punkt model.
        """
        chunks = _ensure_text_sequence(text)
        tokenizer = _get_sentence_tokenizer(self.language)
        sentences: List[str] = []
        for chunk in chunks:
            if not chunk:
                continue
            if self.fix_curly_quotes:
                chunk = normalize_quotes(chunk)
            for sentence in tokenizer.tokenize(chunk):
                cleaned = sentence.strip() if self.strip_whitespace else sentence  # noqa: E501
                if not cleaned and self.drop_empty:
                    continue
                sentences.append(cleaned)
        return sentences


def sentencize(
        text: str | Sequence[str],
        **kwargs: object
) -> List[str]:
    """
    Return sentence boundaries using a temporary :class:`Sentencizer`.

    Parameters
    ----------
    text : str | Sequence[str]
        Input text to split into sentences.
    **kwargs : object
        Keyword arguments forwarded to :class:`Sentencizer`.

    Returns
    -------
    list[str]
        Sentences yielded by the configured splitter.
    """
    return Sentencizer(**kwargs).split(text)


def _get_sentence_tokenizer(language: str) -> PunktSentenceTokenizer:
    cached = _SENTENCE_CACHE.get(language)
    if cached is not None:
        return cached
    tokenizer = _load_sentence_tokenizer(language)
    _SENTENCE_CACHE[language] = tokenizer
    return tokenizer


def _load_sentence_tokenizer(language: str) -> PunktSentenceTokenizer:
    resource = f"tokenizers/punkt/{language}.pickle"
    for _ in range(2):
        try:
            tokenizer = nltk_data.load(resource)
            if not isinstance(tokenizer, PunktSentenceTokenizer):
                raise TypeError(
                    "NLTK resource is not a PunktSentenceTokenizer"
                    )
            return tokenizer
        except LookupError:
            _download_punkt_resources()

    # Provide helpful error message if language still can't be loaded
    if language not in _COMMON_PUNKT_LANGUAGES:
        common = ", ".join(sorted(_COMMON_PUNKT_LANGUAGES))
        raise LookupError(
            f"Unable to load NLTK Punkt tokenizer for language '{language}'. "
            f"Common supported languages: {common}. "
            f"Ensure the language name matches NLTK's naming convention."
        )
    raise LookupError(
        f"Unable to load NLTK Punkt tokenizer data for '{language}' "
        f"after attempting download. Check your internet connection or "
        f"manually download with: python -m nltk.downloader punkt punkt_tab"
    )


def _download_punkt_resources() -> None:
    for package in _PUNKT_RESOURCES:
        try:
            must_have = package == "punkt"
            nltk_download(package, quiet=True, raise_on_error=must_have)
        except Exception as exc:
            if package == "punkt":
                raise RuntimeError(
                    "Failed to download NLTK punkt data"
                    ) from exc
