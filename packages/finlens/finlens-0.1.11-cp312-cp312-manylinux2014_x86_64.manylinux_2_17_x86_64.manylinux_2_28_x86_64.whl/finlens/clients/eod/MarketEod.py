from __future__ import annotations

"""
finlens.clients.eod.market
========================

Cung cấp lớp `MarketEod` — tập hợp các endpoint EOD (End-of-Day)
dành cho **chỉ số thị trường** như VNINDEX, VN30, HNX, HNX30 và UPCOM.

Notes
-----
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Có thể truy vấn nhiều chỉ số cùng lúc.

"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Union, cast

from private_core import eod_core
from private_core.cache_core import CacheKey
from private_core.cache_mixin import BaseCacheMixin
from private_core.cache_policy import (
    touches_latest_trading_day,
    ttl_eod_history,
    ttl_eod_latest,
)
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin
from .investor import investor as _investor_module

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession
    from .investor.MarketInvestor import MarketInvestor

MarketArg = Union[
    Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"],
    Sequence[Literal["VNINDEX", "VN30", "HNXINDEX", "UPINDEX"]],
]
INDEXS = {"VNINDEX", "VN30", "HNXINDEX", "UPINDEX"}


def _normalize_markets(arg: MarketArg) -> tuple[str, ...]:
    if isinstance(arg, str):
        symbol = arg.strip().upper()
        if symbol not in INDEXS:
            raise ValueError(f"Ch��% s��` '{arg}' khA'ng h���p l���. Vui lA�ng ch��?n trong {INDEXS}")
        return (symbol,)
    if isinstance(arg, Sequence):
        cleaned: set[str] = set()
        for item in arg:
            if not isinstance(item, str):
                raise TypeError("All market symbols must be strings.")
            symbol = item.strip().upper()
            if symbol not in INDEXS:
                raise ValueError(f"Ch��% s��` '{item}' khA'ng h���p l���. Vui lA�ng ch��?n trong {INDEXS}")
            cleaned.add(symbol)
        if not cleaned:
            raise ValueError("symbol sequence must contain at least one valid market index.")
        return tuple(sorted(cleaned))
    raise TypeError("symbol must be a string or a sequence of strings.")


def _ohlcv_cache_key(symbol: MarketArg, start: str, end: str, interval: str) -> CacheKey:
    return (_normalize_markets(symbol), start, end, interval)


class MarketEod(BaseCacheMixin, BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho các chỉ số thị trường (Market Indices).

    Bao gồm các chỉ số phổ biến:
    - **VNINDEX**: chỉ số toàn thị trường HOSE  
    - **VN30**: nhóm 30 cổ phiếu vốn hóa lớn trên HOSE  
    - **HNXINDEX**: chỉ số sàn Hà Nội  
    - **UPINDEX**: thị trường UPCOM

    Parameters
    ----------
    session : HttpSession
    
    Notes
    -----
    - Hỗ trợ nhiều chỉ số trong cùng một lệnh truy vấn (`list[str]`).
    - Tự động kiểm tra tính hợp lệ của khoảng thời gian (`start <= end`).
    - Có thể lấy dữ liệu theo nhiều `interval` (ngày, tuần, tháng, v.v.).
    - Trả về dữ liệu OHLCV (Open, High, Low, Close, Volume) của chỉ số.
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo `MarketEod` với session HTTP đã xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP được chia sẻ từ `EodClient`.
        """
        super().__init__(session=session)
        self.investor = cast(
            "MarketInvestor",
            _investor_module._create_investor_client("MarketInvestor", self.session),
        )

    def ohlcv(
        self,
        symbol: MarketArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều chỉ số thị trường.

        Parameters
        ----------
        symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} or Sequence
            Chỉ số hoặc danh sách chỉ số cần lấy dữ liệu.
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ chọn mặc định (thường là 1 năm gần nhất).
        end : str, optional
            Ngày kết thúc, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, mặc định là ngày hiện tại.
        interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
            Khoảng thời gian dữ liệu:
            - `"1D"`: theo ngày  
            - `"1W"`: theo tuần  
            - `"1M"`: theo tháng  
            - `"3M"`, `"6M"`, `"1Y"`: theo quý, nửa năm hoặc năm

        Returns
        -------
        DataFrame
            Bảng dữ liệu OHLCV, gồm các cột:
            - `symbol`: tên chỉ số  
            - `Date`: ngày giao dịch  
            - `Open`, `High`, `Low`, `Close`, `Volume`

        Raises
        ------
        ValueError
            Nếu ngày bắt đầu > ngày kết thúc hoặc interval không hợp lệ.
        ApiRequestError
            Nếu backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        ```python
        from finlens import client
        cli = client(api_key="sk_live_...")
        df = cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
        df.head()
        ```
        -
        >>> # Output
            symbol        Date    Open    High     Low   Close   Volume
        0  VNINDEX  2024-01-02  1120.0  1125.6  1110.2  1119.4  612000000
        
        
        ```python
        # Lấy đồng thời nhiều chỉ số
        cli.eod.market.ohlcv(["VNINDEX", "VN30", "HNX"])
        ```
        
        Notes
        -----
        
        - Có thể dùng để so sánh biến động giữa các chỉ số thị trường.
        
        """
        _normalize_markets(symbol)
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        params = {
            "symbol": symbol,
            "start": start_date,
            "end": end_date,
            "interval": interval_value,
        }

        def _fetch() -> "DataFrame":
            payload = eod_core.fetch_ohlcv(
                self.session,
                symbol,
                start=start_date,
                end=end_date,
                interval=interval_value,
            )
            return self._to_dataframe(payload)

        return self._fetch_with_cache(
            "eod_ohlcv",
            _ohlcv_cache_key(symbol, start_date, end_date, interval_value),
            live=touches_latest_trading_day(end),
            fetcher=_fetch,
            ttl_live=ttl_eod_latest(),
            ttl_history=ttl_eod_history(),
            params=params,
        )
