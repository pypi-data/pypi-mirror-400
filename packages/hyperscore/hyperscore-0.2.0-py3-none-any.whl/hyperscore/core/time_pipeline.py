from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from hyperscore.core.time import TimeSpan

TimeSpanTransform = Callable[[TimeSpan], Iterable[TimeSpan]]


@dataclass(frozen=True)
class TimeSpanPipeline:
    """
    Immutable pipeline for transforming and expanding TimeSpan objects.

    A TimeSpanPipeline represents a pure, composable sequence of
    transformations from a single TimeSpan to zero or more TimeSpans.

    Each transform is a function of the form::

        TimeSpan -> Iterable[TimeSpan]

    This allows a pipeline to:
    - modify a TimeSpan (1 → 1)
    - drop a TimeSpan (1 → 0)
    - duplicate or split a TimeSpan (1 → N)

    Notes
    -----
    - The pipeline is immutable and holds no internal state.
    - Transformations are applied left-to-right.
    - Flattening of intermediate results is handled internally.
    - No global temporal ordering is enforced.
    - TimeSpan objects are treated as immutable values.

    Typical use cases include:
    - time-domain transformations (shift, stretch)
    - structural expansion (duplication, subdivision)
    - rhythmic generation and variation
    - stochastic or conditional filtering
    """

    transforms: tuple[TimeSpanTransform, ...] = ()

    # ---------------- core ----------------

    def apply(self, span: TimeSpan) -> list[TimeSpan]:
        """
        Apply the pipeline to a single TimeSpan.

        Parameters
        ----------
        span : TimeSpan
            Input TimeSpan.

        Returns
        -------
        list of TimeSpan
            Zero or more TimeSpans produced by the pipeline.
        """
        cur: list[TimeSpan] = [span]
        for t in self.transforms:
            nxt: list[TimeSpan] = []
            for s in cur:
                nxt.extend(list(t(s)))
            cur = nxt
        return cur

    def apply_all(self, spans: Iterable[TimeSpan]) -> list[TimeSpan]:
        """
        Apply the pipeline to an iterable of TimeSpans.

        Parameters
        ----------
        spans : iterable of TimeSpan
            Input TimeSpans.

        Returns
        -------
        list of TimeSpan
            All TimeSpans produced by applying the pipeline
            to each input span.
        """
        out: list[TimeSpan] = []
        for s in spans:
            out.extend(self.apply(s))
        return out

    # ---------------- composition ----------------

    def then(self, *more: TimeSpanTransform) -> TimeSpanPipeline:
        """
        Return a new pipeline with additional transforms appended.

        This method does not modify the original pipeline.

        Parameters
        ----------
        *more : callable
            Additional TimeSpan transforms.

        Returns
        -------
        TimeSpanPipeline
            A new composed pipeline.
        """
        return TimeSpanPipeline(self.transforms + more)

    def __or__(self, other: TimeSpanPipeline) -> TimeSpanPipeline:
        """
        Compose two pipelines using the ``|`` operator.

        The resulting pipeline applies this pipeline first,
        then the other pipeline.

        Returns
        -------
        TimeSpanPipeline
            Composed pipeline.
        """
        return TimeSpanPipeline(self.transforms + other.transforms)
