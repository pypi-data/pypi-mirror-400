"""Tokenization helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from nltk.tokenize import TreebankWordTokenizer

_QUOTE_TABLE = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201C": '"',
    "\u201D": '"',
})
_TREEBANK = TreebankWordTokenizer()


def normalize_quotes(text: str) -> str:
    """Convert curly quotes to ASCII equivalents."""
    return text.translate(_QUOTE_TABLE)


def _ensure_text_sequence(text: str | Sequence[str]) -> List[str]:
    if isinstance(text, str):
        return [text]
    return [str(item) for item in text]


def _looks_like_word(token: str) -> bool:
    return any(char.isalpha() for char in token)


@dataclass(slots=True)
class Tokenizer:
    """Word tokenizer backed by NLTK's Treebank rules.

    Parameters
    ----------
    lowercase : bool, optional
        Lowercase emitted tokens when ``True`` (default).
    strip_whitespace : bool, optional
        Trim text chunks prior to tokenization.
    drop_empty : bool, optional
        Omit empty tokens created during cleanup.
    """

    lowercase: bool = True
    strip_whitespace: bool = True
    drop_empty: bool = True

    def tokenize(
            self, text: str | Sequence[str]
    ) -> List[str]:
        """
        Split text into normalized word tokens.

        Parameters
        ----------
        text : str | Sequence[str]
            String or iterable of segments to tokenize.

        Returns
        -------
        list[str]
            Tokens filtered to likely word shapes (alphabetic characters).
        """
        chunks = _ensure_text_sequence(text)
        tokens: List[str] = []
        for chunk in chunks:
            if not chunk:
                continue
            if self.strip_whitespace:
                chunk = chunk.strip()
            if not chunk:
                continue
            normalized = normalize_quotes(chunk)
            for candidate in _TREEBANK.tokenize(normalized):
                if not candidate:
                    if self.drop_empty:
                        continue
                    tokens.append(candidate)
                    continue
                candidate = candidate.strip("'\"")
                if not candidate:
                    if self.drop_empty:
                        continue
                    tokens.append(candidate)
                    continue
                if self.lowercase:
                    candidate = candidate.lower()
                if not _looks_like_word(candidate):
                    continue
                tokens.append(candidate)
        return tokens


def tokenize_words(
        text: str | Sequence[str],
        **kwargs: object
) -> List[str]:
    """
    Return tokens using a temporary :class:`Tokenizer`.

    Parameters
    ----------
    text : str | Sequence[str]
        Input text to tokenize.
    **kwargs : object
        Configuration passed to :class:`Tokenizer`.

    Returns
    -------
    list[str]
        Normalized tokens emitted by the configured tokenizer.
    """
    return Tokenizer(**kwargs).tokenize(text)
