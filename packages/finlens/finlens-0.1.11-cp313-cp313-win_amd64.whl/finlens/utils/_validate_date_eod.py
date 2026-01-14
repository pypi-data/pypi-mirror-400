from datetime import datetime
from typing import Optional
def _validate_date_eod(val: Optional[str], name: str):
    if val is None:
        return
    try:
        datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Tham số '{name}' phải có định dạng YYYY-MM-DD, ví dụ '2023-01-01'.")
