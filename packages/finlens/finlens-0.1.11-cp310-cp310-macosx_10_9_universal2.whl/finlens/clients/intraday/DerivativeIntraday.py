from __future__ import annotations

"""
finlens.clients.intraday.derivative
=================================

Cung cấp lớp `DerivativeIntraday` — tập trung các endpoint Intraday dành cho **hợp đồng tương lai**  
(VN30F*, VN100F*).  
Bao gồm dữ liệu OHLCV (Open, High, Low, Close, Volume) và hỗ trợ các khoảng thời gian khác nhau
(1 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 4 giờ).

Notes
-----
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Tự động kiểm tra và chuẩn hóa ngày bắt đầu/kết thúc, validate interval.
"""

from typing import TYPE_CHECKING, Literal

import pandas as pd

from private_core import intraday_core
from private_core.cache_core import CacheKey, is_today, to_date
from private_core.cache_mixin import BaseCacheMixin
from private_core.cache_policy import (
    ttl_intraday_history,
    ttl_intraday_live,
    ttl_orderbook_live,
)
from ..base import BaseClient
from .helper import DateStr, Interval, _IntradayMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession


DerivativeArg = Literal[
    "VN30F1M",
    "VN30F2M",
    "VN30F1Q",
    "VN30F2Q",
    "VN100F1M",
    "VN100F2M",
    "VN100F1Q",
    "VN100F2Q",
]


def _normalize_symbol(symbol: DerivativeArg) -> str:
    return symbol.strip().upper()


def _ohlcv_cache_key(symbol: DerivativeArg, start: str, end: str, interval: str) -> CacheKey:
    return (_normalize_symbol(symbol), start, end, interval)


def _orderbook_cache_key(symbol: DerivativeArg, target_date: str) -> CacheKey:
    return (_normalize_symbol(symbol), target_date)


_INTERVAL_TO_PANDAS_FREQ: dict[str, str] = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1H": "1H",
    "4H": "4H",
}


class DerivativeIntraday(BaseCacheMixin, BaseClient, _IntradayMixin):
    """
    Cung cấp các endpoint intraday cho **hợp đồng tương lai (derivatives/futures)**.

    Lớp này cho phép truy vấn dữ liệu giá, khối lượng và biến động intraday
    của các mã hợp đồng tương lai chuẩn (VN30F*, VN100F*).

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, dùng để gửi yêu cầu tới backend FinLens.
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo lớp `DerivativeIntraday` với session HTTP đã được xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP đã xác thực.

        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: DerivativeArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1m",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho **hợp đồng tương lai**.

        Parameters
        ----------
        symbol : DerivativeArg
            Mã hợp đồng tương lai cần lấy dữ liệu:

            - ``"VN30F1M"``, ``"VN30F2M"``, ``"VN30F1Q"``, ``"VN30F2Q"``  
            - ``"VN100F1M"``, ``"VN100F2M"``, ``"VN100F1Q"``, ``"VN100F2Q"``

        start : str, optional
            Ngày bắt đầu, định dạng ``"YYYY-MM-DD"``.  
            Nếu không truyền, hệ thống sẽ tự động lấy ngược về theo khoảng mặc định.

        end : str, optional
            Ngày kết thúc, định dạng ``"YYYY-MM-DD"``.  
            Nếu không truyền, mặc định là ngày hiện tại.

        interval : Interval, default "1m"
            Khung thời gian dữ liệu cần lấy:

            - ``"1m"``: theo 1 phút  
            - ``"5m"``: theo 5 phút  
            - ``"15m"``: theo 15 phút  
            - ``"30m"``: theo 30 phút  
            - ``"1H"``: theo giờ  
            - ``"4H"``: theo 4 giờ

        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột cơ bản:

            - ``symbol``: mã hợp đồng tương lai  
            - ``date``: thời điểm giao dịch  
            - ``open``, ``high``, ``low``, ``close``, ``volume``

            (Tuỳ backend, có thể kèm thêm các cột mở rộng như ``oi`` – open interest.)

        Raises
        ------
        ValueError
            Khi tham số ``start`` > ``end``, hoặc ``interval`` không hợp lệ.
        ApiRequestError
            Khi backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        >>> from finlens import client
        >>> cli = client(api_key="sk_live_...")
        >>> df = cli.intraday.derivative.ohlcv("VN30F1M", start="2024-01-01", end="2024-06-30")
        >>> df.head()
        >>> # Output (ví dụ)
        >>> #     symbol               date   open   high    low  close     volume
        >>> # 0  VN30F1M  2024-01-02 09:15:00  1110   1116   1105   1114   12345

        Notes
        -----
        - Tự động validate khoảng thời gian (``start <= end``).
        - Dữ liệu này phản ánh biến động intraday của các hợp đồng tương lai.
        """
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        params = {
            "symbol": symbol,
            "start": start_date,
            "end": end_date,
            "interval": interval_value,
        }

        def _fetch() -> "DataFrame":
            return intraday_core.fetch_ohlcv(
                self.session,
                symbol,
                start=start_date,
                end=end_date,
                interval=interval_value,
            )

        return self._fetch_with_cache(
            "ohlcv",
            _ohlcv_cache_key(symbol, start_date, end_date, interval_value),
            live=is_today(end),
            fetcher=_fetch,
            ttl_live=ttl_intraday_live(),
            ttl_history=ttl_intraday_history(),
            params=params,
        )
    def orderbook(
        self,
        symbol: DerivativeArg,
        target_date: DateStr = None,
    ) -> "DataFrame":
        """
        Lấy dữ liệu Orderbook cho hợp đồng phái sinh.

        Parameters
        ----------
        symbol : str
            Mã hợp đồng phái sinh cần lấy dữ liệu (VD: `"VN30F1M"`).
        target_date : str, optional
            Ngày giao dịch, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ tự động lấy ngày làm việc gần nhất (trong tuần).
        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột:

            - `symbol`: mã hợp đồng phái sinh  
            - `date`: ngày giao dịch  
            - `close`: giá đóng cửa
            - `volume`: khối lượng giao dịch
            - `type`: loại lệnh (B: Mua chủ động, S: Bán chủ động, N: Không xác định)

        Raises
        ------
        ValueError
            Khi tham số `target_date` không hợp lệ.
        ApiRequestError
            Khi backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        ```python
        from finlens import client
        cli = client(api_key="sk_live_...")
        df = cli.intraday.derivative.orderbook("VN30F1M", target_date="2024-01-01")
        df.head()
        ```
        
        >>> # Output
            symbol               date    close    volume     type   
        0      VN30F1M  2024-01-02 09:15:00  27200       1500         B

        """
        resolved_date = self._resolve_target_date(target_date)
        day_key = to_date(resolved_date).isoformat()
        params = {
            "symbol": symbol,
            "target_date": resolved_date,
        }

        def _fetch() -> "DataFrame":
            return intraday_core.fetch_orderbook(
                self.session,
                symbol,
                target_date=resolved_date,
            )

        return self._fetch_with_cache(
            "orderbook",
            _orderbook_cache_key(symbol, day_key),
            live=is_today(resolved_date),
            fetcher=_fetch,
            ttl_live=ttl_orderbook_live(),
            ttl_history=ttl_intraday_history(),
            params=params,
        )

    def net_active_value(
        self,
        symbol: DerivativeArg,
        target_date: DateStr = None,
        interval: Interval = "1m",
    ) -> "DataFrame":
        """
        Tính Net Active Value (NAV = B - S) cho hợp đồng tương lai.

        Giá trị mỗi record được xác định `value = close * volume`. Lệnh bán
        (`type = "S"`) được đổi dấu để phản ánh dòng tiền âm, đồng thời loại bỏ
        các bản ghi trung lập (`type = "N"`). (đvt tỷ đồng)

        Parameters
        ----------
        symbol : DerivativeArg
            Mã hợp đồng phái sinh cần tính toán.
        target_date : str, optional
            Ngày giao dịch, mặc định là ngày làm việc gần nhất.
        interval : Interval, default "1m"
            Khoảng thời gian gom nhóm trước khi tính tổng giá trị thuần.

        Returns
        -------
        DataFrame
            Bảng gồm `symbol`, `date`, `value` (B - S) và `value_cumsum` (lũy kế).
        """

        def _empty_frame() -> pd.DataFrame:
            return pd.DataFrame(columns=["symbol", "date", "value", "value_cumsum"])

        interval_value = self._validate_interval(interval)
        orderbook_df = self.orderbook(symbol=symbol, target_date=target_date)
        if orderbook_df.empty:
            return _empty_frame()

        required_columns = {"date", "close", "volume", "type"}
        missing_columns = required_columns - set(orderbook_df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"orderbook data missing required columns: {missing}.")

        frame = orderbook_df.copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
        frame["type"] = frame["type"].astype(str).str.upper()
        frame = frame.dropna(subset=["date", "close", "volume"])
        if frame.empty:
            return _empty_frame()

        frame = frame[frame["type"].isin({"B", "S"})].copy()
        if frame.empty:
            return _empty_frame()

        symbol_value = _normalize_symbol(symbol)
        frame["symbol"] = symbol_value
        frame["value"] = frame["close"] * frame["volume"]
        frame.loc[frame["type"] == "S", "value"] *= -1

        freq = _INTERVAL_TO_PANDAS_FREQ[interval_value]
        frame["bucket"] = frame["date"].dt.floor(freq)

        aggregated = (
            frame.groupby(["symbol", "bucket"], as_index=False)["value"]
            .sum()
            .rename(columns={"bucket": "date"})
            .sort_values("date")
            .reset_index(drop=True)
        )

        if aggregated.empty:
            return _empty_frame()

        aggregated["value_cumsum"] = aggregated.groupby("symbol")["value"].cumsum()
        return aggregated
