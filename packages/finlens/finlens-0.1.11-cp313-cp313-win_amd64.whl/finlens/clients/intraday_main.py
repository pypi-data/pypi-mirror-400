#finlens\clients\eod_main.py
from __future__ import annotations

"""
finlens.clients.intraday
=================

Cung cấp lớp `IntradayClient` — giao diện bậc cao (facade) cho toàn bộ nhóm
chức năng liên quan đến dữ liệu Intraday.  
Mỗi nhóm con (`stock`, `market`, `sector`, `derivative`) tương ứng với một loại dữ liệu Intraday
cụ thể và được đóng gói trong các lớp `StockIntraday`, `MarketIntraday`, `SectorIntraday`, `DerivativeIntraday`.

Notes
-----

- Các phương thức trong `StockIntraday`, `MarketIntraday`, `SectorIntraday`, `DerivativeIntraday` đều trả về `pandas.DataFrame`
  hoặc `dict` tùy theo tham số `as_dataframe`.

See Also
--------
FinLensClient
    Entry point chính của SDK, dùng để khởi tạo `IntradayClient`.
BaseClient
    Lớp cơ sở quản lý session và xử lý logic chung.
"""

from typing import TYPE_CHECKING

from .base import BaseClient
from .intraday import StockIntraday, MarketIntraday, DerivativeIntraday

if TYPE_CHECKING:
    from private_core.http_core import HttpSession

__all__ = ["IntradayClient"]


class IntradayClient(BaseClient):
    """
    Lớp facade cấp cao tập hợp các namespace dữ liệu intraday.

    Cho phép người dùng truy cập nhanh vào các nhóm dữ liệu:
    
    - `IntradayClient.stock`: dữ liệu intraday của từng mã cổ phiếu.
    - `IntradayClient.market`: dữ liệu chỉ số thị trường (VNINDEX, HNXINDEX, UPCOM...).
    - `IntradayClient.derivative`: dữ liệu intraday phái sinh.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `FinLensClient`.

    Attributes
    ----------
    stock : StockIntraday
        Namespace xử lý dữ liệu intraday của cổ phiếu (OHLCV, phân tích kỹ thuật, v.v.).
    market : MarketIntraday
        Namespace cho dữ liệu thị trường chung (VNINDEX, HNX, UPCOM).
    derivative : DerivativeIntraday
        Namespace cho dữ liệu phái sinh trong phiên giao dịch.

    Examples
    --------
    ```python
    from finlens import client
    with client(api_key="sk_live_...") as cli:
        df = cli.intraday.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")

    ```

    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo các namespace INTRADAY con (stock, market, sector).

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP đã xác thực từ `FinLensClient`.
        """
        super().__init__(session=session)
        self.stock: StockIntraday = StockIntraday(session=self.session)
        """
        Namespace dữ liệu intraday cho **cổ phiếu (Stock-level)**.

        Cung cấp các endpoint chuyên biệt để truy xuất dữ liệu Intraday
        cho từng mã cổ phiếu riêng lẻ — phù hợp cho các tác vụ như:
        - Phân tích giá lịch sử (OHLCV)
        - Tính toán chỉ báo kỹ thuật (MA, RSI, MACD, Bollinger, v.v.)
        - So sánh hiệu suất cổ phiếu giữa các mã trong khung thời gian ngắn

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1m")`
            → Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) theo 1 phút, 5 phút, 15 phút…

        Parameters
        ----------
        symbol : str or list[str]
            Mã cổ phiếu (VD: `"HPG"`)

        Examples
        --------
        ```python
        cli.intraday.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
        ```
        """

        self.market: MarketIntraday = MarketIntraday(session=self.session)
        """
        Namespace dữ liệu intraday cho **chỉ số thị trường (Market-level)**.

        Cung cấp dữ liệu tổng hợp cho các chỉ số thị trường phổ biến như:
        - VNINDEX (sàn HOSE)
        - VN30 (rổ 30 cổ phiếu vốn hóa lớn)
        - HNX, HNX30 (sàn Hà Nội)
        - UPCOM (thị trường UPCOM)

        Dữ liệu này giúp phân tích xu hướng toàn thị trường, đo lường biến động,
        và so sánh hiệu suất giữa các sàn.

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1m")`
            → Lấy dữ liệu OHLCV của các chỉ số (VNINDEX, VN30, HNX, …)

        Parameters
        ----------
        symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} 

        Examples
        --------
        ```python
        cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
        ```
        """

        self.derivative: DerivativeIntraday = DerivativeIntraday(session=self.session)
        """
        Namespace dữ liệu intraday cho **hợp đồng tương lai (Derivative-level)**.

        Cung cấp dữ liệu tổng hợp cho các hợp đồng tương lai như VN30F, VN100F.
        Dữ liệu này giúp phân tích xu hướng hợp đồng tương lai, đo lường biến động,
        và so sánh hiệu suất giữa các hợp đồng.

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1m")`

        Parameters
        ----------
        symbol : str
            Tên hợp đồng tương lai (VD: `"VN30F1M"`, `"VN100F2Q"`).

        Examples
        --------
        ```python
        cli.intraday.derivative.ohlcv("VN30F1M", start="2024-01-01", end="2024-06-30")
        ```

        """

