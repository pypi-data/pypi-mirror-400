from investor import _InvestorBase, InvestorGroup
from ..helper import DateStr, InterValInvestor, MarketArg
import pandas as pd


class MarketInvestor(_InvestorBase):
    """
    Namespace dữ liệu **nhà đầu tư** cho cấp độ **thị trường** (market-level).

    Cung cấp các endpoint để theo dõi hoạt động mua/bán ròng của từng nhóm
    nhà đầu tư trên các chỉ số thị trường như VNINDEX, VN30, HNX, hoặc UPCOM.

    Notes
    -----
    - `_endpoint_root = "market"` để định tuyến về namespace thị trường.
    - Phù hợp cho các phân tích dòng tiền tổng hợp (foreign flow, proprietary trading)
      giúp đánh giá xu hướng vốn trên toàn thị trường.
    """

    _endpoint_root = "market"

    def flow(
        self,
        symbol: MarketArg,
        *,
        group: InvestorGroup = "foreign",
        start: DateStr = None,
        end: DateStr = None,
        interval: InterValInvestor = "1D",
    ) -> pd.DataFrame:
        """
        Lấy dữ liệu **dòng tiền ròng (net buy/sell flow)** theo nhóm nhà đầu tư
        cho các chỉ số thị trường (VNINDEX, VN30, HNX, UPCOM...).

        Hàm này cung cấp cái nhìn tổng quan về xu hướng dòng vốn của từng nhóm nhà đầu tư
        (nước ngoài, tự doanh, tổ chức, cá nhân, ...) trên cấp độ toàn thị trường
        hoặc theo từng chỉ số cụ thể.

        Parameters
        ----------
        symbol : str or Sequence[str]
            Mã chỉ số thị trường hoặc danh sách mã chỉ số
            (ví dụ: "VNINDEX", "VN30", "HNXINDEX", "UPINDEX").
        group : InvestorGroup, optional
            Nhóm nhà đầu tư cần lấy dữ liệu. Choices:
            
            - `"foreign"` — Nhà đầu tư nước ngoài (tổng hợp)
            - `"proprietary"` — Tự doanh công ty chứng khoán
            - `"local_institutional"` — Tổ chức trong nước
            - `"local_individual"` — Cá nhân trong nước
            - `"foreign_institutional"` — Tổ chức nước ngoài
            - `"foreign_individual"` — Cá nhân nước ngoài
   
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
            - `symbol` : mã chỉ số thị trường  
            - `Date` : ngày giao dịch  
            - `net_value` : giá trị mua ròng (VNĐ)  
            - `net_volume` : khối lượng mua ròng  
            - Các cột khác như `buy_value`, `sell_value`, `buy_volume`, `sell_volume`.

        Raises
        ------
        ValueError
            Nếu `group` hoặc `interval` không hợp lệ.
        RuntimeError
            Nếu truy vấn từ private_core thất bại.

        Notes
        -----
        - Dữ liệu được chuẩn hóa về `pandas.DataFrame`.
        - Thường dùng trong phân tích dòng vốn toàn thị trường, xác định xu hướng
          mua/bán ròng của nhà đầu tư nước ngoài hoặc tự doanh.

        Examples
        --------
        ```python
        from finlens import client

        cli = client(api_key="sk_live_...")
        investor = cli.eod.market.investor

        # Dòng tiền ròng của nhà đầu tư nước ngoài trên VNINDEX trong quý 1/2024
        df = investor.flow("VNINDEX", group="foreign", start="2024-01-01", end="2024-03-31")

        # Dòng tiền ròng tổng hợp theo tuần trên nhiều chỉ số
        df = investor.flow(["VNINDEX", "VN30", "HNX"], interval="1W")
        ```
        """
        if isinstance(interval, str):
            interval=interval.upper()
        else:
            print(f"🚫 Lỗi kiểu dữ liệu interval: {interval}\nℹ️  Vui lòng chọn đúng 1 trong các option sau: {InterValInvestor}. Ví dụ: interval='1D'")
            return
        
        # if ((group not in ['foreign', 'proprietary']) and 'VNINDEX' not in symbol) or isinstance(symbol, list):
        #     print(f"🚫 {group} chỉ áp dụng với chỉ số VNINDEX.\nKiểm tra lại symbol: {symbol}")
        #     return
        params = self._build_params(
            ids=symbol, label="symbol", group=group, start=start, end=end, interval=interval
        )
        return self._fetch_df(op="flow", params=params)
