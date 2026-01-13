"""CLI for generating sample sentiment trajectory plots."""
from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ..data import iter_sample_texts
from ..sentiment import DictionarySentimentAnalyzer, SpaCySentimentAnalyzer
from ..transforms import DCTTransform
from ..viz import TrajectoryComponents, plot_trajectory, prepare_trajectory


def iter_texts(path: Path | None) -> Iterator[Tuple[str, str]]:
    """
    Yield doc id / text pairs from a pickled corpus or the bundled sample.
    """

    if path is None:
        yield from iter_sample_texts()
        return

    for record in _load_pickled_corpus(path):
        normalized = _normalize_record(record)
        if normalized is None:
            continue
        yield normalized


def _load_pickled_corpus(path: Path) -> Sequence[Mapping[str, Any]]:
    with path.open("rb") as handle:
        records = pickle.load(handle)
    if isinstance(records, list):
        return records
    raise TypeError(
        f"Expected a list of corpus records in {path}, got {type(records)!r}"
    )


def _normalize_record(record: Mapping[str, Any]) -> Tuple[str, str] | None:
    doc_id = str(record.get("doc_id") or "doc").strip()
    text = str(record.get("text") or "").strip()
    if not text:
        return None
    return (doc_id or "doc", text)


def build_trajectory(
        scores: Iterable[float],
        *,
        points: int,
        low_pass: int,
        rolling_ratio: float,
        normalize: str | None = None,
) -> TrajectoryComponents | None:
    values = list(scores)
    if not values:
        return None
    low_pass_size = max(1, min(low_pass, len(values), points))
    transform = DCTTransform(
        low_pass_size=low_pass_size, output_length=points, scale_range=True
        )
    window = max(3, int(len(values) * rolling_ratio))
    normalize_mode = None
    if normalize:
        normalized = normalize.lower()
        if normalized not in {"range", "zscore"}:
            raise ValueError("normalize must be 'range' or 'zscore'")
        normalize_mode = normalized
    trajectory = prepare_trajectory(
        values,
        rolling_window=window,
        dct_transform=transform,
        normalize=normalize_mode,
    )
    return trajectory


def make_plot(
        doc_id: str,
        trajectory: TrajectoryComponents,
        *,
        output_dir: Path | None = None,
        method: str
) -> Path | Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    plot_trajectory(trajectory, ax=ax, title=f"{doc_id} ({method})")
    ax.set_ylim(-1.05, 1.05)
    fig.tight_layout()
    if output_dir is None:
        return fig
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = doc_id.replace("/", "_").replace(" ", "_")
    target = output_dir / f"{safe_name}.png"
    fig.savefig(target, dpi=200)
    plt.close(fig)
    return target


def parse_args(
        argv: Sequence[str] | None = None
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate sentiment trajectory plots for sample texts."
        )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Pickled list of {doc_id, text} records (defaults to the bundled sample).",  # noqa: E501
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sample_plots"),
        help="Directory where PNG plots will be written (relative to the current working directory).",  # noqa: E501
    )
    parser.add_argument(
        "--analyzer",
        choices=["dictionary", "spacy"],
        default="dictionary",
        help="Choose between dictionary or spaCy-based analyzers.",
    )
    parser.add_argument(
        "--method",
        default="syuzhet",
        help="Dictionary method (only used when --analyzer=dictionary).",
    )
    parser.add_argument(
        "--spacy-model",
        default="en_core_web_sm",
        help="spaCy model to load when --analyzer=spacy.",
    )
    parser.add_argument(
        "--spacy-positive-label",
        default="POSITIVE",
        help="spaCy category treated as positive when --analyzer=spacy.",
    )
    parser.add_argument(
        "--spacy-negative-label",
        default="NEGATIVE",
        help="spaCy category treated as negative when --analyzer=spacy.",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=200,
        help="Number of interpolation points for the DCT trajectory.",
    )
    parser.add_argument(
        "--low-pass",
        type=int,
        default=10,
        help="Low-pass components to retain in the DCT smoother.",
    )
    parser.add_argument(
        "--rolling-ratio",
        type=float,
        default=0.1,
        help="Rolling mean window expressed as a fraction of total sentences.",
    )
    parser.add_argument(
        "--normalize",
        choices=["range", "zscore", "none"],
        default="range",
        help="Rescale plotted signals (range=-1..1, zscore=standardize, none=raw).",  # noqa: E501
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for number of documents to process (0 = all).",
    )
    return parser.parse_args(argv)


def resolve_scorer(args: argparse.Namespace):
    if args.analyzer == "spacy":
        analyzer = SpaCySentimentAnalyzer(
            model=args.spacy_model,
            positive_label=args.spacy_positive_label,
            negative_label=args.spacy_negative_label,
        )

        def spacy_scores(text: str) -> Iterable[float]:
            return analyzer.text_scores(text)

        return spacy_scores

    analyzer = DictionarySentimentAnalyzer()

    def dictionary_scores(text: str) -> Iterable[float]:
        return analyzer.text_scores(text, method=args.method)

    return dictionary_scores


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    score_fn = resolve_scorer(args)

    # Count total texts if limit is set or for progress reporting
    texts_list = list(iter_texts(args.input))
    total = len(texts_list) if not args.limit else min(args.limit, len(texts_list))  # noqa: E501

    print(f"Processing {total} text(s)...")
    processed = 0

    for doc_id, text in texts_list:
        scores = score_fn(text)
        trajectory = build_trajectory(
            scores,
            points=args.points,
            low_pass=args.low_pass,
            rolling_ratio=args.rolling_ratio,
            normalize=None if args.normalize == "none" else args.normalize,
        )
        if trajectory is None:
            continue
        output_path = make_plot(
            doc_id, trajectory, output_dir=args.output, method=args.method
        )
        processed += 1
        print(f"[{processed}/{total}] Wrote {output_path}")

        if args.limit and processed >= args.limit:
            break

    print(f"\nCompleted: {processed} plot(s) written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
