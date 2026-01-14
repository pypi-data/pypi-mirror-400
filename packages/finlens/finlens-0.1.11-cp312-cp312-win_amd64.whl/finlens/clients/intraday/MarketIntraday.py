from __future__ import annotations

"""
finlens.clients.intraday.market
=============================

Cung cấp lớp `MarketIntraday` — tập trung các endpoint Intraday dành cho **chỉ số thị trường**  
(VNINDEX, VN30, HNXINDEX, UPCOM).  
Bao gồm dữ liệu OHLCV (Open, High, Low, Close, Volume) và
hỗ trợ các khoảng thời gian khác nhau (1 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 4 giờ).

Notes
-----
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Tự động kiểm tra và chuẩn hóa ngày bắt đầu/kết thúc, validate interval.
"""

from typing import TYPE_CHECKING, Literal

from private_core import intraday_core
from private_core.cache_core import CacheKey, is_today
from private_core.cache_mixin import BaseCacheMixin
from private_core.cache_policy import ttl_intraday_history, ttl_intraday_live
from ..base import BaseClient
from .helper import DateStr, Interval, _IntradayMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession


MarketArg = Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"]


def _normalize_symbol(symbol: MarketArg) -> str:
    return symbol.strip().upper()


def _ohlcv_cache_key(symbol: MarketArg, start: str, end: str, interval: str) -> CacheKey:
    return (_normalize_symbol(symbol), start, end, interval)


class MarketIntraday(BaseCacheMixin, BaseClient, _IntradayMixin):
    """
    Cung cấp các endpoint intraday cho **chỉ số thị trường (market index)**.

    Lớp này cho phép truy vấn dữ liệu giá, khối lượng và biến động
    của các chỉ số chính như VNINDEX, VN30, HNXINDEX, hoặc UPCOM.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, dùng để gửi yêu cầu tới backend FinLens.
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo lớp `MarketIntraday` với session HTTP đã được xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP đã xác thực.
            
        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: MarketArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1m",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho **chỉ số thị trường**.

        Parameters
        ----------
        symbol : MarketArg
            Mã chỉ số cần lấy dữ liệu:
            
            - `"VNINDEX"` — Chỉ số sàn HOSE  
            - `"VN30"` — Rổ 30 cổ phiếu vốn hóa lớn  
            - `"HNXINDEX"` — Chỉ số sàn Hà Nội  
            - `"UPINDEX"` — Chỉ số thị trường UPCOM  
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
            
            - `symbol`: mã chỉ số  
            - `date`: thời điểm giao dịch  
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
        df = cli.intraday.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
        df.head()
        ```

        >>> # Output
        >>> #    symbol               date    open    high     low   close    volume
        >>> # 0  VNINDEX  2024-01-02 09:15:00  1100   1110   1095   1108   225000000

        Notes
        -----
        - Tự động validate khoảng thời gian (`start <= end`).
        - Dữ liệu này phản ánh biến động intraday của toàn thị trường.
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
