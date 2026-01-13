"""spaCy-powered sentence segmentation utilities."""
from __future__ import annotations

from typing import List, Sequence

from spacy.language import Language

from ..spacy_support import ensure_sentence_boundaries, load_spacy_model
from .sentences import _ensure_text_sequence


class SpaCySentencizer:
    """
    Sentence splitter that delegates to a spaCy pipeline.
    """

    def __init__(
        self,
        *,
        nlp: Language | None = None,
        model: str = "en_core_web_sm",
        strip_whitespace: bool = True,
        drop_empty: bool = True,
    ) -> None:
        self._nlp = nlp or load_spacy_model(model)
        self.strip_whitespace = strip_whitespace
        self.drop_empty = drop_empty
        ensure_sentence_boundaries(self._nlp)

    def split(
            self,
            text: str | Sequence[str]
    ) -> List[str]:
        """
        Split raw text (or text chunks) into sentences.

        Parameters
        ----------
        text : str | Sequence[str]
            Full document or iterable of text segments to process.

        Returns
        -------
        list[str]
            Sentences extracted by the spaCy pipeline.
        """
        sentences: List[str] = []
        for chunk in _ensure_text_sequence(text):
            if not chunk:
                continue
            doc = self._nlp(chunk)
            for sent in doc.sents:
                content = sent.text.strip() if self.strip_whitespace else sent.text  # noqa: E501
                if not content and self.drop_empty:
                    continue
                sentences.append(content)
        return sentences
