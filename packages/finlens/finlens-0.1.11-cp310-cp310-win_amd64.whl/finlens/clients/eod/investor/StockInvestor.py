from investor import _InvestorBase,InvestorGroup
from ..helper import DateStr,InterValInvestor,SymbolArg
import pandas as pd 

class StockInvestor(_InvestorBase):
    _endpoint_root = "stock"

    def flow(
        self,
        symbol: SymbolArg,
        *,
        group: InvestorGroup = "foreign",
        start: DateStr = None,
        end: DateStr = None,
        interval: InterValInvestor = "1D",
    ) -> pd.DataFrame:
        """
        Lấy dữ liệu **dòng tiền ròng (net buy/sell flow)** theo nhóm nhà đầu tư 
        cho từng mã cổ phiếu hoặc danh sách mã.

        Hàm này cho phép theo dõi hoạt động mua bán ròng của từng nhóm nhà đầu tư 
        (cá nhân, tổ chức, nước ngoài, tự doanh...) trong một khoảng thời gian xác định.  
        Dữ liệu trả về giúp nhận biết xu hướng dòng tiền — ai đang mua, ai đang bán, 
        và cường độ dòng vốn vào/ra khỏi mã cổ phiếu.

        Parameters
        ----------
        symbol : str or Sequence[str]
            Mã cổ phiếu hoặc danh sách mã cần lấy dữ liệu 
            (ví dụ: `"HPG"` hoặc `["HPG", "VCB", "FPT"]`).
        group : InvestorGroup, optional
            Nhóm nhà đầu tư cần lấy dữ liệu. Choices:
            
            - "foreign" — Nhà đầu tư nước ngoài (tổng hợp)
            - "proprietary" — Tự doanh CTCK
            - "local_institutional" — Tổ chức trong nước
            - "local_individual" — Cá nhân trong nước
            - "foreign_institutional" — Tổ chức nước ngoài
            - "foreign_individual" — Cá nhân nước ngoài
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống tự động lấy theo giới hạn mặc định.
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
            - `symbol` : mã cổ phiếu  
            - `Date` : ngày giao dịch  
            - `net_value` : giá trị mua ròng (VNĐ)  
            - `net_volume` : khối lượng mua ròng  
            - Các cột khác (nếu có) như `buy_value`, `sell_value`, `buy_volume`, `sell_volume`.

        Raises
        ------
        ValueError
            Nếu `group` hoặc `interval` không hợp lệ.
        RuntimeError
            Nếu quá trình truy vấn từ private_core thất bại.

        Notes
        -----
        - Dữ liệu được chuẩn hóa dưới dạng `pandas.DataFrame`.
        - Dùng để đánh giá hành vi mua/bán ròng theo nhóm nhà đầu tư cho từng cổ phiếu.

        Examples
        --------
        ```python
        from finlens import client

        cli = client(api_key="sk_live_...")
        investor = cli.eod.stock.investor

        # Lấy dòng tiền ròng của cổ phiếu HPG trong 6 tháng đầu năm 2024
        df = investor.flow("HPG", start="2024-01-01", end="2024-06-30, group='foreign", interval='1D')

        # Lấy dòng tiền ròng của nhóm nhà đầu tư nước ngoài cho nhiều mã
        df = investor.flow(["HPG", "VCB", "FPT"], group="foreign", interval="1W")
        ```
        """
        if isinstance(interval, str):
            interval=interval.upper()
        else:
            print(f"🚫 Lỗi kiểu dữ liệu interval: {interval}\nℹ️  Vui lòng chọn đúng 1 trong các option sau: {InterValInvestor}. Ví dụ: interval='1D'")
            return 
        params = self._build_params(
            ids=symbol, label="symbol", group=group, start=start, end=end, interval=interval
        )
    
        return self._fetch_df(op="flow", params=params)
