# finlens\clients\eod\helper.py
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import ClassVar, Iterable, Literal, Optional, TypeAlias,Union,Sequence

import pandas as pd

from ...utils import _validate_date_eod

DateStr: TypeAlias = Optional[str]
Interval = Literal["1D", "1W", "1M", "3M", "6M", "1Y"]
InterValInvestor= Literal["1D", "1W", "1M"]
SymbolArg = Union[str, Sequence[str]]  # Stock
MarketArg = Union[
    Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"],
    Sequence[Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"]],
]

class _EodMixin:
    """Common helpers shared across EOD namespaces."""

    _DEFAULT_LOOKBACK_DAYS: ClassVar[int] = 30
    _ALLOWED_INTERVALS: ClassVar[set[str]] = {"1D", "1W", "1M", "3M", "6M", "1Y"}

    def _normalize_range(self, start: DateStr, end: DateStr) -> tuple[str, str]:
        """Return a validated (start, end) date pair in ISO format."""
        today = date.today()

        if end is None:
            end_date = today
        else:
            _validate_date_eod(end, "end")
            end_date = datetime.strptime(end, "%Y-%m-%d").date()

        if start is None:
            start_date = end_date - timedelta(days=self._DEFAULT_LOOKBACK_DAYS)
        else:
            _validate_date_eod(start, "start")
            start_date = datetime.strptime(start, "%Y-%m-%d").date()

        if start_date > end_date:
            raise ValueError(
                f"start date ({start_date:%Y-%m-%d}) cannot be after end date ({end_date:%Y-%m-%d})."
            )

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def _validate_interval(self, interval: Interval) -> Interval:
        """Ensure the provided interval value is supported by the backend."""
        if interval not in self._ALLOWED_INTERVALS:
            allowed = ", ".join(sorted(self._ALLOWED_INTERVALS))
            raise ValueError(f"interval must be one of {{{allowed}}}, received {interval!r}.")
        return interval

    @staticmethod
    def _to_dataframe(rows: Iterable[dict]) -> pd.DataFrame:
        """Materialise raw rows into a sorted pandas.DataFrame."""
        frame = pd.DataFrame(rows)
        if frame.empty:
            return frame

        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")

        sort_cols = [column for column in ("symbol", "date") if column in frame.columns]
        if sort_cols:
            frame = frame.sort_values(sort_cols).reset_index(drop=True)

        return frame
