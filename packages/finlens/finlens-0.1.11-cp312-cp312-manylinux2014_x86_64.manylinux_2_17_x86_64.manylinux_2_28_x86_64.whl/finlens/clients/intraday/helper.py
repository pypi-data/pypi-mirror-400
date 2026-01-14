# finlens\clients\eod\helper.py
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import ClassVar, Iterable, Literal, Optional, TypeAlias,Union,Sequence

import pandas as pd

from ...utils import _validate_date_eod

DateStr: TypeAlias = Optional[str]
Interval = Literal['1m','5m','15m','30m','1H','4H']
InterValInvestor= Literal["1D", "1W", "1M"]
SymbolArg = str
MarketArg = Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"]
    

    
class _IntradayMixin:
    """Common helpers shared across EOD namespaces."""

    _DEFAULT_LOOKBACK_DAYS: ClassVar[int] = 10
    _ALLOWED_INTERVALS: ClassVar[set[str]] = {"1m", "5m", "15m", "30m", "1H", "4H"}
    _MAX_WORKING_DAYS: ClassVar[int] = 10

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

        # Enforce intraday window to at most 10 working days (Mon-Fri)
        working_days = self._count_working_days(start_date, end_date)
        if working_days > self._MAX_WORKING_DAYS:
            raise ValueError(
                "date range cannot exceed 10 working days (Monday-Friday) "
                f"({start_date:%Y-%m-%d} → {end_date:%Y-%m-%d})."
            )

        return start_date.strftime("%Y-%m-%d 00:00:00"), end_date.strftime("%Y-%m-%d 23:59:59")

    def _validate_interval(self, interval: Interval) -> Interval:
        """Ensure the provided interval value is supported by the backend."""
        if interval not in self._ALLOWED_INTERVALS:
            allowed = ", ".join(sorted(self._ALLOWED_INTERVALS))
            raise ValueError(f"interval must be one of {{{allowed}}}, received {interval!r}.")
        return interval
    def _resolve_target_date(self, target_date: DateStr) -> str:
        """Return a validated trading date (defaults to most recent weekday)."""
        if target_date is not None:
            _validate_date_eod(target_date, "target_date")
            return target_date

        current = date.today()
        while current.weekday() >= 5:  # Saturday/Sunday fallback
            current -= timedelta(days=1)
        return current.strftime("%Y-%m-%d")
    @staticmethod
    def _count_working_days(start_date: date, end_date: date) -> int:
        """Count inclusive working days (Mon-Fri) between two dates."""
        total_days = (end_date - start_date).days + 1
        full_weeks, remainder = divmod(total_days, 7)
        working_days = full_weeks * 5

        start_weekday = start_date.weekday()
        for offset in range(remainder):
            if (start_weekday + offset) % 7 < 5:
                working_days += 1

        return working_days

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
