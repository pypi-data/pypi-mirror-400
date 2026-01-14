#finlens\clients\eod_main.py
from __future__ import annotations

"""
finlens.clients.eod
=================

Cung cấp lớp `EodClient` — giao diện bậc cao (facade) cho toàn bộ nhóm
chức năng liên quan đến dữ liệu EOD (End-Of-Day).  
Mỗi nhóm con (`stock`, `market`, `sector`) tương ứng với một loại dữ liệu EOD
cụ thể và được đóng gói trong các lớp `StockEod`, `MarketEod`, `SectorEod`.

Notes
-----
- `EodClient` không trực tiếp gọi HTTP API, mà ủy quyền cho các lớp con.
- Mọi request được gửi thông qua `HttpSession` (đã được xác thực sẵn bởi `FinLensClient`).
- Các phương thức trong `StockEod`, `MarketEod`, `SectorEod` đều trả về `pandas.DataFrame`
  hoặc `dict` tùy theo tham số `as_dataframe`.

See Also
--------
FinLensClient
    Entry point chính của SDK, dùng để khởi tạo `EodClient`.
BaseClient
    Lớp cơ sở quản lý session và xử lý logic chung.
"""

from typing import TYPE_CHECKING

from .base import BaseClient
from .eod import MarketEod, SectorEod, StockEod

if TYPE_CHECKING:
    from private_core.http_core import HttpSession

__all__ = ["EodClient"]


class EodClient(BaseClient):
    """
    Lớp facade cấp cao tập hợp các namespace dữ liệu EOD (End-of-Day).

    Cho phép người dùng truy cập nhanh vào các nhóm dữ liệu:
    - `EodClient.stock`: dữ liệu EOD của từng mã cổ phiếu.
    - `EodClient.market`: dữ liệu chỉ số thị trường (VNINDEX, HNXINDEX, UPCOM...).
    - `EodClient.sector`: dữ liệu EOD tổng hợp theo ngành (ICB).

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `FinLensClient`.

    Attributes
    ----------
    stock : StockEod
        Namespace xử lý dữ liệu EOD của cổ phiếu (OHLCV, phân tích kỹ thuật, v.v.).
    market : MarketEod
        Namespace cho dữ liệu thị trường chung (VNINDEX, HNX, UPCOM).
    sector : SectorEod
        Namespace cho dữ liệu theo ngành, dùng để theo dõi chỉ số và hiệu suất ICB.

    Examples
    --------
    ```python
    from finlens import client
    with client(api_key="sk_live_...") as cli:
    ...     df = cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")

    ```

    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo các namespace EOD con (stock, market, sector).

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP đã xác thực từ `FinLensClient`.
        """
        super().__init__(session=session)
        self.stock: StockEod = StockEod(session=self.session)
        """
        Namespace dữ liệu EOD cho **cổ phiếu (Stock-level)**.

        Cung cấp các endpoint chuyên biệt để truy xuất dữ liệu End-of-Day (EOD)
        cho từng mã cổ phiếu riêng lẻ — phù hợp cho các tác vụ như:
        - Phân tích giá lịch sử (OHLCV)
        - Tính toán chỉ báo kỹ thuật (MA, RSI, MACD, Bollinger, v.v.)
        - So sánh hiệu suất cổ phiếu giữa các mã

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1D")`
            → Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) theo ngày, tuần, tháng…
        - `investor.flow("HPG", start="2024-01-01", end="2024-06-30, group='foreign", interval='1D')` 
        
        Parameters
        ----------
        symbol : str or list[str]
            Mã cổ phiếu hoặc danh sách mã (VD: `"HPG"`, `["HPG", "VCB"]`)

        Examples
        --------
        ```python
        cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
        cli.eod.stock.ohlcv(["HPG", "VCB", "FPT"], interval="1W")
        ```
        """

        self.market: MarketEod = MarketEod(session=self.session)
        """
        Namespace dữ liệu EOD cho **chỉ số thị trường (Market-level)**.

        Cung cấp dữ liệu tổng hợp cho các chỉ số thị trường phổ biến như:
        - VNINDEX (sàn HOSE)
        - VN30 (rổ 30 cổ phiếu vốn hóa lớn)
        - HNX, HNX30 (sàn Hà Nội)
        - UPCOM (thị trường UPCOM)

        Dữ liệu này giúp phân tích xu hướng toàn thị trường, đo lường biến động,
        và so sánh hiệu suất giữa các sàn.

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1D")`
            → Lấy dữ liệu OHLCV của các chỉ số (VNINDEX, VN30, HNX, …)

        Parameters
        ----------
        symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} or list
            Tên chỉ số hoặc danh sách chỉ số.

        Examples
        --------
        ```python
        cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
        cli.eod.market.ohlcv(["VNINDEX", "VN30", "HNX"])
        ```
        """

        self.sector: SectorEod = SectorEod(session=self.session)
        """
        Namespace dữ liệu EOD cho **ngành và nhóm ngành (Sector-level)**.

        Cung cấp dữ liệu tổng hợp theo mã ICB (Industry Classification Benchmark),
        phản ánh biến động và hiệu suất trung bình của từng ngành hoặc tiểu ngành.
        Thường dùng trong phân tích xoay vòng ngành (sector rotation) hoặc theo dõi
        xu hướng dòng tiền giữa các nhóm cổ phiếu.

        Methods chính
        --------------
        - `ohlcv(symbol, start=None, end=None, interval="1D")`
            → Lấy dữ liệu OHLCV trung bình theo ngành hoặc nhóm ngành.

        Parameters
        ----------
        symbol : str or list[str]
            Tên ngành (VD: `"Ngân hàng"`, `"Môi giới chứng khoán"`).

        Examples
        --------
        ```python
        cli.eod.sector.ohlcv("Ngân hàng", start="2024-01-01", end="2024-06-30")
        cli.eod.sector.ohlcv(["Ngân hàng", "Môi giới chứng khoán"], interval="1W")
        ```
        Notes
        -----
        - Dữ liệu ngành được tính theo trọng số vốn hóa.
        - Thường dùng để xác định nhóm ngành dẫn dắt thị trường.
        """

