"""spaCy-powered sentiment analysis helpers."""
from __future__ import annotations

from typing import Callable, List, Sequence

from spacy.language import Language
from spacy.tokens import Doc

from ..spacy_support import (
    ensure_sentence_boundaries,
    ensure_sentiment_component,
    load_spacy_model,
)
from ..text.spacy_sentences import SpaCySentencizer

ScoreFn = Callable[[Doc], float]


class SpaCySentimentAnalyzer:
    """
    Derive per-sentence sentiment values from a spaCy pipeline.

    Parameters
    ----------
    nlp : Language, optional
        Pre-loaded spaCy pipeline. If provided, the ``model`` parameter
        is ignored.
    model : str, optional
        Name of a spaCy model to load (e.g., ``"en_core_web_sm"``) or
        path to a local model directory. Defaults to ``"en_core_web_sm"``.
        Only used if ``nlp`` is not provided.
    positive_label : str, optional
        Label to use for positive sentiment when extracting from
        ``doc.cats``. Defaults to ``"POSITIVE"``.
    negative_label : str, optional
        Label to use for negative sentiment when extracting from
        ``doc.cats``. Defaults to ``"NEGATIVE"``.
    scorer : callable, optional
        Custom scoring function that takes a spaCy ``Doc`` and returns
        a float sentiment score. If provided, overrides default
        sentiment extraction.
    strip_whitespace : bool, optional
        Remove leading/trailing whitespace from sentences.
    drop_empty : bool, optional
        Omit empty sentences from processing.

    Examples
    --------
    >>> # Use a model name
    >>> analyzer = SpaCySentimentAnalyzer(model="en_core_web_sm")
    >>>
    >>> # Use a local model path
    >>> analyzer = SpaCySentimentAnalyzer(model="/path/to/my_model")
    >>>
    >>> # Use a pre-loaded pipeline
    >>> import spacy
    >>> nlp = spacy.load("en_core_web_lg")
    >>> analyzer = SpaCySentimentAnalyzer(nlp=nlp)
    """

    def __init__(
        self,
        *,
        nlp: Language | None = None,
        model: str = "en_core_web_sm",
        positive_label: str = "POSITIVE",
        negative_label: str = "NEGATIVE",
        scorer: ScoreFn | None = None,
        strip_whitespace: bool = True,
        drop_empty: bool = True,
    ) -> None:
        self._nlp = nlp or load_spacy_model(model)
        ensure_sentence_boundaries(self._nlp)
        ensure_sentiment_component(self._nlp)
        self._sentencizer = SpaCySentencizer(
            nlp=self._nlp,
            strip_whitespace=strip_whitespace,
            drop_empty=drop_empty,
        )
        self._score_override = scorer
        self.strip_whitespace = strip_whitespace
        self.drop_empty = drop_empty
        self._positive_label = positive_label.lower()
        self._negative_label = negative_label.lower()

    def sentence_scores(
            self,
            sentences: Sequence[str]
    ) -> List[float]:
        """
        Score a pre-tokenized list of sentences using spaCy.

        Parameters
        ----------
        sentences : Sequence[str]
            Sentences to feed through the spaCy pipeline.

        Returns
        -------
        list[float]
            One sentiment score per sentence.
        """
        texts: List[str] = []
        for sentence in sentences:
            if sentence is None:
                continue
            content = sentence.strip() if self.strip_whitespace else sentence
            if not content and self.drop_empty:
                continue
            texts.append(content)
        if not texts:
            return []
        return [self._score_doc(doc) for doc in self._nlp.pipe(texts)]

    def text_scores(
            self,
            text: str | Sequence[str]
    ) -> List[float]:
        """
        Split raw text into sentences and score each one.

        Parameters
        ----------
        text : str | Sequence[str]
            Full document or iterable of segments to analyze.

        Returns
        -------
        list[float]
            Sentiment score per detected sentence.
        """
        sentences = self._sentencizer.split(text)
        if not sentences:
            return []
        return self.sentence_scores(sentences)

    def _score_doc(
            self,
            doc: Doc
    ) -> float:
        """
        Extract a numeric polarity from a spaCy Doc.
        """
        if self._score_override is not None:
            return float(self._score_override(doc))

        underscore = getattr(doc, "_", None)
        has_attr = getattr(underscore, "has", None)
        if callable(has_attr):
            if underscore.has("blob"):
                blob = getattr(underscore, "blob", None)
                polarity = getattr(blob, "polarity", None)
                if polarity is not None:
                    return float(polarity)
                sentiment = getattr(blob, "sentiment", None)
                if sentiment is not None:
                    polarity = getattr(sentiment, "polarity", None)
                    if polarity is not None:
                        return float(polarity)
            if underscore.has("polarity"):
                return float(underscore.polarity)  # type: ignore[attr-defined]
            if underscore.has("sentiment"):
                value = underscore.sentiment  # type: ignore[attr-defined]
                if isinstance(value, (list, tuple)):
                    value = value[0] if value else 0.0
                return float(value)

        if hasattr(doc, "sentiment") and doc.sentiment:
            try:
                return float(doc.sentiment)
            except (TypeError, ValueError):
                pass

        cats = getattr(doc, "cats", None) or {}
        if cats:
            normalized = {key.lower(): score for key, score in cats.items()}
            has_named = False
            positive = 0.0
            negative = 0.0
            if self._positive_label in normalized:
                positive = float(normalized[self._positive_label])
                has_named = True
            if self._negative_label in normalized:
                negative = float(normalized[self._negative_label])
                has_named = True
            if has_named:
                return positive - negative
            # Fallback to the dominant class
            # if specific labels are unavailable.
            return float(max(normalized.values(), default=0.0))

        return 0.0
