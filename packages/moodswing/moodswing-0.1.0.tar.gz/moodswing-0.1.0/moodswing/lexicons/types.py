"""
Data structures for representing sentiment lexicons.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, MutableMapping


@dataclass(frozen=True)
class LexiconMetadata:
    """
    Lightweight metadata bundle for a lexicon.
    """

    name: str
    language: str = "english"
    source: str | None = None
    license: str | None = None
    description: str | None = None
    version: str | None = None


@dataclass(slots=True)
class SentimentLexicon:
    """
    Dictionary-based valence lexicon.
    """

    metadata: LexiconMetadata
    values: Mapping[str, float]

    def score(self, token: str) -> float:
        return float(self.values.get(token, 0.0))

    def batch_score(self, tokens: Iterable[str]) -> float:
        return float(sum(self.score(token) for token in tokens))


@dataclass(slots=True)
class EmotionLexicon:
    """
    Lexicon that maps tokens to multiple emotion categories.
    """

    metadata: LexiconMetadata
    matrix: Mapping[str, Mapping[str, float]]
    _categories: tuple[str, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        categories: Dict[str, None] = {}
        for entry in self.matrix.values():
            for category in entry.keys():
                categories[category] = None
        object.__setattr__(
            self, "_categories", tuple(sorted(categories.keys()))
            )

    @property
    def categories(self) -> tuple[str, ...]:
        return self._categories

    def emotions_for(self, token: str) -> Mapping[str, float]:
        return self.matrix.get(token, {})

    def aggregate(
            self,
            tokens: Iterable[str],
            categories: Iterable[str] | None = None
    ) -> Dict[str, float]:
        selected = tuple(categories) if categories is not None else self._categories  # noqa: E501
        totals: MutableMapping[str, float] = {cat: 0.0 for cat in selected}
        for token in tokens:
            values = self.matrix.get(token)
            if not values:
                continue
            for category, weight in values.items():
                if category in totals:
                    totals[category] += weight
        return dict(totals)
