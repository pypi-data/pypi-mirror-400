from __future__ import annotations

"""
finlens.clients.eod.sector
========================

Cung cấp lớp `SectorEod` — các endpoint EOD (End-of-Day) cho dữ liệu ngành (ICB Sector Aggregates).

Dữ liệu thể hiện hiệu suất, biến động, và khối lượng giao dịch trung bình của từng ngành
(ICB Code) hoặc nhóm ngành (Sub-sector). Phù hợp cho phân tích xoay vòng ngành (sector rotation)
và đánh giá xu hướng thị trường theo nhóm.

Notes
-----
- Tất cả kết quả trả về dạng `pandas.DataFrame`.
- Cho phép truy vấn nhiều mã ngành cùng lúc.
"""

from typing import TYPE_CHECKING, Sequence, Union, cast

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
from .icb_types import SectorArg, icbMap
if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession
    from .investor.SectorInvestor import SectorInvestor




def _sector_cache_key(codes: Sequence[str], start: str, end: str, interval: str) -> CacheKey:
    return (tuple(codes), start, end, interval)


class SectorEod(BaseCacheMixin, BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho nhóm ngành (ICB Sector/Industry).

    Lớp này giúp truy vấn dữ liệu tổng hợp cho từng ngành (ICB Code) theo ngày, tuần, tháng, v.v.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Cho phép lấy dữ liệu nhiều mã ngành cùng lúc (list[str]).
    - Hỗ trợ chuẩn hóa khoảng thời gian và kiểm tra `interval`.
    - Trả về OHLCV (Open, High, Low, Close, Volume) trung bình của từng ngành.
    - Các mã ngành tuân theo chuẩn phân loại ICB (ví dụ: `ICB01010`, `ICB03020`...).
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo `SectorEod` với session HTTP đã xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP dùng chung từ `EodClient`.
        """
        super().__init__(session=session)
        self.investor = cast(
            "SectorInvestor",
            _investor_module._create_investor_client("SectorInvestor", self.session),
        )

    def ohlcv(
        self,
        symbol: SectorArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều ngành ICB.

        Parameters
        ----------
        symbol : str or Sequence[str]
            Tên ngành hoặc danh sách tên ngành (ví dụ: `"Ngân hàng"`, `["Ngân hàng", "Môi giới chứng khoán"]`).
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
            Bảng dữ liệu OHLCV cho từng mã ngành, gồm:
            - `icbCode`: mã ngành  
            - `Date`: ngày giao dịch  
            - `Open`, `High`, `Low`, `Close`, `Volume`  
            - Có thể có thêm `MarketCap`, `TurnoverRatio` nếu backend hỗ trợ.

        Raises
        ------
        ValueError
            Nếu ngày bắt đầu > ngày kết thúc hoặc `interval` không hợp lệ.
        ApiRequestError
            Nếu backend trả lỗi khi gọi API.

        Examples
        --------
        ```python
        from finlens import client
        cli = client(api_key="sk_live_...")
        df = cli.eod.sector.ohlcv("ICB01010", start="2024-01-01", end="2024-06-30")
        df.head()
        ```
        -
        >>> # Output
            icbCode        Date     Open     High      Low    Close   Volume
        0   8777  2024-01-02  1320.25  1334.11  1305.21  1310.55  9.32e6
        
        
        ```python
        # Lấy đồng thời nhiều ngành
        cli.eod.sector.ohlcv(["Ngân hàng", "Môi giới chứng khoán"])
        ```

        Notes
        -----
        - Phù hợp để phân tích hiệu suất ngành theo thời gian.
        - Dữ liệu thường được tổng hợp từ trung bình trọng số theo vốn hóa.
        """
        icb_codes: list[str] = []
        if isinstance(symbol, list):
            for sec in symbol:
                if sec.lower() not in icbMap:
                    raise ValueError(f"Không tìm thấy ngành: '{sec}'")
                icb_codes.append(icbMap.get(sec.lower()))
        else:
            if symbol.lower() not in icbMap:
                raise ValueError(f"Không tìm thấy ngành: '{symbol}'")
            icb_codes.append(icbMap.get(symbol.lower()))

        if not icb_codes:
            raise ValueError(f"Không tìm thấy ngành: '{symbol}'")

        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        codes_tuple = tuple(icb_codes)
        params = {
            'symbol': symbol,
            'icb_codes': codes_tuple,
            'start': start_date,
            'end': end_date,
            'interval': interval_value,
        }

        def _fetch() -> 'DataFrame':
            payload = eod_core.fetch_ohlcv(
                self.session,
                icb_codes,
                start=start_date,
                end=end_date,
                interval=interval_value,
            )
            return self._to_dataframe(payload)

        return self._fetch_with_cache(
            'eod_ohlcv',
            _sector_cache_key(codes_tuple, start_date, end_date, interval_value),
            live=touches_latest_trading_day(end),
            fetcher=_fetch,
            ttl_live=ttl_eod_latest(),
            ttl_history=ttl_eod_history(),
            params=params,
        )
