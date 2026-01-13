"""Dictionary-based sentiment scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable, List, Mapping, MutableSequence, Sequence

from ..lexicons import EmotionLexicon, LexiconLoader, SentimentLexicon
from ..text import Sentencizer, Tokenizer

_DEFAULT_METHOD = "syuzhet"
_NRC_POSITIVE = "positive"
_NRC_NEGATIVE = "negative"


@dataclass(frozen=True, slots=True)
class MixedMessageResult:
    """
    Result from analyzing mixed sentiment signals.

    Attributes
    ----------
    entropy : float
        Shannon entropy over positive/negative token distribution.
        Higher values indicate more mixed or ambiguous sentiment.
    normalized_entropy : float
        Entropy normalized by the total number of tokens, providing
        a length-independent measure of sentiment mixing.
    """

    entropy: float
    normalized_entropy: float


@dataclass(slots=True)
class DictionarySentimentAnalyzer:
    """
    Sentence-level sentiment scoring built on dictionary lookups.
    """

    loader: LexiconLoader = field(default_factory=LexiconLoader)
    tokenizer: Tokenizer = field(default_factory=Tokenizer)
    sentencizer: Sentencizer = field(default_factory=Sentencizer)

    def sentence_scores(
        self,
        sentences: Sequence[str],
        *,
        method: str = _DEFAULT_METHOD,
        language: str = "english",
        lexicon: SentimentLexicon | None = None,
    ) -> List[float]:
        """
        Return one sentiment score per sentence.

        Parameters
        ----------
        sentences : Sequence[str]
            Sentences that have already been split from the source text.
        method : str, optional
            Name of the dictionary lexicon to use
            (``syuzhet``, ``bing``, etc.).
        language : str, optional
            Language tag used when loading multilingual lexicons such as NRC.
        lexicon : SentimentLexicon, optional
            Preloaded lexicon. Provide this when you want to reuse the same
            instance across multiple calls to avoid I/O.

        Returns
        -------
        list[float]
            One numeric sentiment score for each input sentence.
        """
        if lexicon is None:
            lexicon = self._resolve_valence(method, language)
        scores: List[float] = []
        for sentence in sentences:
            tokens = self.tokenizer.tokenize(sentence)
            score = lexicon.batch_score(tokens)
            scores.append(score)
        return scores

    def text_scores(
        self,
        text: str | Sequence[str],
        *,
        method: str = _DEFAULT_METHOD,
        language: str = "english",
        lexicon: SentimentLexicon | None = None,
    ) -> List[float]:
        """
        Split full text into sentences and score each one.

        Parameters
        ----------
        text : str | Sequence[str]
            Either a single string (the full document) or an iterable of
            pre-separated paragraphs/segments.
        method : str, optional
            Lexicon name passed to :func:`sentence_scores`.
        language : str, optional
            Language tag used when loading the lexicon.
        lexicon : SentimentLexicon, optional
            Preloaded lexicon that overrides the automatic loader.

        Returns
        -------
        list[float]
            Sentiment score per detected sentence.
        """
        sentences = self.sentencizer.split(text)
        return self.sentence_scores(
            sentences, method=method, language=language, lexicon=lexicon
            )

    def nrc_emotions(
        self,
        sentences: Sequence[str],
        *,
        language: str = "english",
        lexicon: EmotionLexicon | None = None,
        categories: Iterable[str] | None = None,
    ) -> List[Mapping[str, float]]:
        """
        Aggregate NRC-style emotion counts for each sentence.

        Parameters
        ----------
        sentences : Sequence[str]
            Sentences to analyze.
        language : str, optional
            Language tag for loading NRC variants.
        lexicon : EmotionLexicon, optional
            Specific NRC emotion lexicon to reuse.
        categories : Iterable[str], optional
            Restrict the output to a subset of emotion labels.

        Returns
        -------
        list[dict[str, float]]
            Per-sentence mappings from emotion label to aggregated weight.

        Examples
        --------
        >>> from moodswing import DictionarySentimentAnalyzer
        >>> import pandas as pd
        >>>
        >>> analyzer = DictionarySentimentAnalyzer()
        >>> sentences = ["I love sunny days!", "The storm was terrifying."]
        >>> emotions = analyzer.nrc_emotions(sentences)
        >>>
        >>> # Convert to DataFrame for easy viewing
        >>> df = pd.DataFrame(emotions)
        >>> print(df[['joy', 'fear', 'positive', 'negative']])
        >>>
        >>> # Analyze only specific emotions
        >>> fear_joy = analyzer.nrc_emotions(
        ...     sentences,
        ...     categories=['fear', 'joy']
        ... )
        >>> df_fear_joy = pd.DataFrame(fear_joy)
        """
        if lexicon is None:
            lexicon = self._resolve_emotion(language)
        rows: List[Mapping[str, float]] = []
        for sentence in sentences:
            tokens = self.tokenizer.tokenize(sentence)
            rows.append(lexicon.aggregate(tokens, categories=categories))
        return rows

    def mixed_messages(
        self,
        text: str | Sequence[str],
        *,
        method: str = _DEFAULT_METHOD,
        drop_neutral: bool = True,
    ) -> MixedMessageResult:
        """
        Compute Shannon entropy to quantify mixed sentiment signals.

        Parameters
        ----------
        text : str | Sequence[str]
            Document (or sequence of segments) to analyze.
        method : str, optional
            Lexicon name to use when determining positive/negative tokens.
        drop_neutral : bool, optional
            When ``True`` (default), neutral words are excluded from the
            entropy calculation.

        Returns
        -------
        MixedMessageResult
            Named result containing ``entropy`` (Shannon entropy over
            positive/negative distribution) and ``normalized_entropy``
            (entropy divided by token count for length-independent measure).

        Examples
        --------
        >>> analyzer = DictionarySentimentAnalyzer()
        >>> result = analyzer.mixed_messages("I love it but I hate it.")
        >>> result.entropy  # Higher values indicate more mixing
        >>> result.normalized_entropy  # Length-normalized version
        """
        tokens = self.tokenizer.tokenize(text)
        lexicon = self._resolve_valence(method, language="english")
        sentiments: List[int] = []
        for token in tokens:
            score = lexicon.score(token)
            if score == 0 and drop_neutral:
                continue
            sentiments.append(
                int(math.copysign(1, score)) if score != 0 else 0
                )
        if not sentiments:
            return MixedMessageResult(entropy=0.0, normalized_entropy=0.0)
        freq_map: dict[int, float] = {}
        total = len(sentiments)
        for value in sentiments:
            freq_map[value] = freq_map.get(value, 0.0) + 1.0
        entropy = 0.0
        for count in freq_map.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        metric_entropy = entropy / max(len(tokens), 1)
        return MixedMessageResult(entropy=entropy, normalized_entropy=metric_entropy)  # noqa: E501

    def _resolve_valence(self, method: str, language: str) -> SentimentLexicon:
        lexicon_name = method.lower()
        lexicon = self.loader.load(lexicon_name, language=language)
        if isinstance(lexicon, EmotionLexicon):
            diff = _nrc_valence_projection(lexicon)
            return SentimentLexicon(metadata=lexicon.metadata, values=diff)
        return lexicon

    def _resolve_emotion(self, language: str) -> EmotionLexicon:
        lexicon = self.loader.load("nrc", language=language)
        if not isinstance(lexicon, EmotionLexicon):
            raise TypeError("The NRC lexicon must expose emotion categories")
        return lexicon


def _nrc_valence_projection(lexicon: EmotionLexicon) -> Mapping[str, float]:
    values: MutableSequence[tuple[str, float]] = []
    for word, categories in lexicon.matrix.items():
        positive = categories.get(_NRC_POSITIVE, 0.0)
        negative = categories.get(_NRC_NEGATIVE, 0.0)
        values.append((word, positive - negative))
    return dict(values)
