from __future__ import annotations

"""
finlens.clients.intraday.stock
=======================

Cung cấp lớp `StockIntraday` — tập trung các endpoint Intraday dành cho từng mã cổ phiếu riêng lẻ.  
Bao gồm dữ liệu OHLCV (Open, High, Low, Close, Volume) và
hỗ trợ các khoảng thời gian khác nhau (1 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 4 giờ).

Notes
-----
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Tự động kiểm tra và chuẩn hóa ngày bắt đầu/kết thúc, validate interval.
"""

from datetime import date, timedelta
from typing import TYPE_CHECKING

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

def _normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("symbol must not be empty.")
    return cleaned


def _ohlcv_cache_key(symbol: str, start: str, end: str, interval: str) -> CacheKey:
    return (_normalize_symbol(symbol), start, end, interval)


def _orderbook_cache_key(symbol: str, target_date: str) -> CacheKey:
    return (_normalize_symbol(symbol), target_date)


_INTERVAL_TO_PANDAS_FREQ: dict[str, str] = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1H": "1H",
    "4H": "4H",
}


class StockIntraday(BaseCacheMixin, BaseClient, _IntradayMixin):
    """
    Cung cấp các endpoint intraday cho từng mã cổ phiếu (equity symbol).

    Lớp này cho phép truy vấn dữ liệu giá, khối lượng và chỉ báo kỹ thuật
    ở cấp mã cổ phiếu.

    Parameters
    ----------
    session : HttpSession

    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo lớp `StockIntraday` với session HTTP đã được xác thực.

        Parameters
        ----------
        session : HttpSession

        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: str,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1m",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều mã cổ phiếu.

        Parameters
        ----------
        symbol : str
            Mã cổ phiếu cần lấy dữ liệu (VD: `"HPG"`).
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ tự động lấy ngược về theo khoảng mặc định.
        end : str, optional
            Ngày kết thúc, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, mặc định là ngày hiện tại.

        interval : Interval, default "1m"
            Khoảng thời gian dữ liệu cần lấy:

            - `"1m"`: theo 1 phút
            - `"5m"`: theo 5 phút
            - `"15m"`: theo 15 phút
            - `"30m"`: theo 30 phút
            - `"1H"`: theo giờ
            - `"4H"`: theo 4 giờ

        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột:

            - `symbol`: mã cổ phiếu  
            - `date`: ngày giao dịch  
            - `open`, `high`, `low`, `close`, `volume`  

        Raises
        ------
        ValueError
            Khi tham số `start` > `end`, hoặc `interval` không hợp lệ.
        ApiRequestError
            Khi backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        ```python
        from finlens import client
        cli = client(api_key="sk_live_...")
        df = cli.intraday.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
        df.head()
        ```
        
        >>> # Output
            symbol               date    open    high     low   close    volume
        0      HPG  2024-01-02 09:15:00  27200  27500  26900  27400  15300000

        Notes
        -----
        - Tự động validate khoảng thời gian (`start <= end`).
        """
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        live = is_today(end)
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
            live=live,
            fetcher=_fetch,
            ttl_live=ttl_intraday_live(),
            ttl_history=ttl_intraday_history(),
            params=params,
        )
    def orderbook(
        self,
        symbol: str,
        target_date: DateStr = None,
    ) -> "DataFrame":
        """
        Lấy dữ liệu Orderbook cho một mã cổ phiếu.

        Parameters
        ----------
        symbol : str
            Mã cổ phiếu cần lấy dữ liệu (VD: `"HPG"`).
        target_date : str, optional
            Ngày giao dịch, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ tự động lấy ngày làm việc gần nhất (trong tuần).
        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột:

            - `symbol`: mã cổ phiếu  
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
        df = cli.intraday.stock.orderbook("HPG", target_date="2024-01-01")
        df.head()
        ```
        
        >>> # Output
            symbol               date    close    volume     type   
        0      HPG  2024-01-02 09:15:00  27200       1500         B

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
        symbol: str,
        target_date: DateStr = None,
        interval: Interval = "1m",
    ) -> "DataFrame":
        """
        Tính Net Active Value (B - S) theo từng khoảng thời gian.

        Giá trị mỗi lệnh được xác định bằng công thức `value = close * volume`.
        Các lệnh bán chủ động (`type = "S"`) bị đổi dấu để phản ánh dòng tiền âm.

        Parameters
        ----------
        symbol : str
            Mã cổ phiếu cần tính toán (VD: `"HPG"`).
        target_date : str, optional
            Ngày giao dịch (`"YYYY-MM-DD"`). Nếu không truyền sẽ là ngày làm việc gần nhất.
        interval : Interval, default "1m"
            Khoảng thời gian gom nhóm trước khi tính tổng giá trị thuần.

        Returns
        -------
        DataFrame
            Bảng gồm các cột:

            - `symbol`
            - `date`: mốc thời gian đã gom theo interval
            - `value`: tổng giá trị thuần trong interval (B - S) (đvt tỷ đồng)
            - `value_cumsum`: lũy kế giá trị thuần theo thời gian (đvt tỷ đồng)
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
        frame["value"] = frame["close"] * frame["volume"]/10**6
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


