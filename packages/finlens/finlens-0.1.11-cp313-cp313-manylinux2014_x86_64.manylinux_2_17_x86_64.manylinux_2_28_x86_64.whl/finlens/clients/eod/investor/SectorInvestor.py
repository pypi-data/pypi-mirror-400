from investor import _InvestorBase, InvestorGroup
from typing import ClassVar, Iterable, Literal
from ..helper import DateStr, InterValInvestor
from ..icb_types import SectorArg, icbMap
import pandas as pd

InvestorGroupSector = Literal[
    "foreign",
    "proprietary",
]
class SectorInvestor(_InvestorBase):
    """
    Namespace dữ liệu **nhà đầu tư** cho cấp độ **ngành (sector-level)**.

    Cung cấp các endpoint để theo dõi hoạt động mua/bán ròng của từng nhóm nhà đầu tư
    trong các **ngành hoặc nhóm ngành** (ICB code).  
    Dữ liệu phản ánh dòng vốn giữa các nhóm ngành — cho phép đánh giá dòng tiền luân chuyển
    (sector rotation) trên toàn thị trường.

    Notes
    -----
    - Cho phép truyền **tên ngành tiếng Việt**.
    """

    _endpoint_root = "sector"

    def flow(
        self,
        symbol: SectorArg,
        *,
        group: InvestorGroupSector = "foreign",
        start: DateStr = None,
        end: DateStr = None,
        interval: InterValInvestor = "1D",
    ) -> pd.DataFrame:
        """
        Lấy dữ liệu **dòng tiền ròng (net buy/sell flow)** theo nhóm nhà đầu tư
        cho từng **ngành hoặc nhóm ngành** (ICB sector).

        Hàm này cho phép theo dõi xu hướng dòng vốn của các nhóm nhà đầu tư
        (nước ngoài, tự doanh, tổ chức, cá nhân...) giữa các ngành khác nhau.  
        Dữ liệu giúp xác định **ngành nào đang hút vốn hoặc bị rút vốn**, 
        hỗ trợ phân tích xoay vòng ngành (sector rotation).

        Parameters
        ----------
        symbol : str or Sequence[str]
            Tên ngành (có thể truyền nhiều giá trị).  
            Ví dụ: `"Ngân hàng"`, `"Công nghệ"`, hoặc `["Ngân hàng", "Dầu khí"]`.  
            Hàm tự động map tên ngành sang mã ICB thông qua `icbMap`.
        group : {"foreign", "proprietary"}, default "foreign"
            Nhóm nhà đầu tư cần lấy dữ liệu:
            
            - `"foreign"` — Nhà đầu tư nước ngoài (tổng hợp)
            - `"proprietary"` — Tự doanh công ty chứng khoán
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống tự động lấy theo khoảng mặc định.
        end : str, optional
            Ngày kết thúc, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, mặc định là ngày hiện tại.
        interval : {"1D", "1W", "1M"}, default "1D"
            Tần suất dữ liệu mong muốn:
            - `"1D"` — Theo ngày  
            - `"1W"` — Theo tuần  
            - `"1M"` — Theo tháng

        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột:
            - `symbol` : mã ngành (ICB code)  
            - `Date` : ngày giao dịch  
            - `net_value` : giá trị mua ròng (VNĐ)  
            - `net_volume` : khối lượng mua ròng  
            - Các cột khác (nếu có) như `buy_value`, `sell_value`, `buy_volume`, `sell_volume`.

        Raises
        ------
        ValueError
            Nếu không tìm thấy mã ngành hợp lệ trong `icbMap`,
            hoặc nếu `group`/`interval` không hợp lệ.
        RuntimeError
            Nếu truy vấn từ private_core thất bại.

        Notes
        -----
        - Wrapper của `private_core.investor.fetch_df(namespace="sector", op="flow")`.
        - Tự động ánh xạ tên ngành tiếng Việt sang mã ICB trước khi truy vấn.
        - Dữ liệu được chuẩn hóa về `pandas.DataFrame`.

        Examples
        --------
        ```python
        from finlens import client

        cli = client(api_key="sk_live_...")
        investor = cli.eod.sector.investor

        # Dòng tiền ròng của nhóm ngành "Ngân hàng" trong 6 tháng đầu năm 2024
        df = investor.flow("Ngân hàng", start="2024-01-01", end="2024-06-30")

        # Dòng tiền ròng theo tuần của các nhóm ngành Dầu khí và Công nghệ
        df = investor.flow(["Dầu khí", "Công nghệ"], group="foreign", interval="1W")
        ```
        """
        icb_codes = []
        if isinstance(symbol, list):
            for sec in symbol:
                if sec.lower() not in icbMap:
                    raise ValueError(f"Không tìm thấy mã ngành cho tên '{sec}'")
                icb_codes.append(icbMap.get(sec.lower()))
        else:
            if symbol.lower() not in icbMap:
                raise ValueError(f"Không tìm thấy mã ngành cho tên '{symbol}'")
            icb_codes.append(icbMap.get(symbol.lower()))

        if not symbol:
            raise ValueError(f"Không tìm thấy mã ngành cho tên '{symbol}'")
        if isinstance(interval, str):
            interval=interval.upper()
        else:
            print(f"🚫 Lỗi kiểu dữ liệu interval: {interval}\nℹ️  Vui lòng chọn đúng 1 trong các option sau: {InterValInvestor}. Ví dụ: interval='1D'")
            return
        if group not in ['foreign','proprietary']:
            print(f"🚫 Không có dữ liệu: {group} đối với cli.eod.sector.flow()\n group vui lòng là một trong các option sau: 'foreign' | 'proprietary'")
            return
       
        params = self._build_params(
            ids=icb_codes, label="symbol", group=group, start=start, end=end, interval=interval
        )

        return self._fetch_df(op="flow", params=params)
