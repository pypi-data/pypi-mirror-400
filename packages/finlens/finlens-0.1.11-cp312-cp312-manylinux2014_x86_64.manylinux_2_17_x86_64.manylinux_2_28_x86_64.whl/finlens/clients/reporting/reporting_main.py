from __future__ import annotations

"""
finlens.clients.reporting
=======================

Cung cấp facade `ReportingClient` hỗ trợ truy vấn báo cáo tài chính.
Client này thực hiện quy trình hai bước:
1) Gọi API validate để xác định loại doanh nghiệp phù hợp cho tập symbol.
2) Gọi API lấy giá trị báo cáo theo loại đã chọn và gom kết quả thành pandas.DataFrame.

Kết quả trả về gồm:
- `nodes`: DataFrame chứa toàn bộ cây chỉ tiêu và danh sách giá trị.
- `periods`: DataFrame mô tả chu kỳ báo cáo tương ứng với từng symbol.
- `meta`: metadata (tham số yêu cầu + thông tin validate).
- `raw`: payload gốc từ backend để người dùng tự xử lý khi cần.
"""

from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple, Literal

import pandas as pd

from private_core import financials_core

from ..base import BaseClient
from .helper import (
    CompanyTypeMismatchError,
    attach_warning,
    map_statement_to_int,
    normalize_symbols,
)
from .types import PeriodType, StatementStr

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession

    JsonDict = Dict[str, Any]
else:
    JsonDict = Dict[str, Any]


_MIN_YEAR = 1900
_ALLOWED_PERIODS: set[str] = {"year", "quarter"}
ValuesFormat = Literal["long", "cross"]


def _validate_year_range(start_year: int, end_year: int) -> None:
    if start_year < _MIN_YEAR:
        raise ValueError(f"start_year must be >= {_MIN_YEAR}.")
    if end_year < _MIN_YEAR:
        raise ValueError(f"end_year must be >= {_MIN_YEAR}.")
    if end_year < start_year:
        raise ValueError("end_year must be greater than or equal to start_year.")


def _ensure_period(period: str) -> str:
    if period not in _ALLOWED_PERIODS:
        raise ValueError(f"period must be one of {_ALLOWED_PERIODS}.")
    return period


def _to_frame(data: Iterable[MutableMapping[str, Any]], extra_columns: Dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(list(data))
    if frame.empty:
        # Preserve column order even when the backend returns no rows.
        for key, value in extra_columns.items():
            frame[key] = value
        return frame.iloc[0:0]

    for key, value in extra_columns.items():
        frame[key] = value
    return frame


def _build_nodes_frame(results: Sequence[JsonDict]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for result in results:
        nodes = result.get("nodes")
        if not isinstance(nodes, list):
            continue
        extra = {
            "symbol": result.get("symbol"),
            "company_type": result.get("company_type"),
            "statement_id": result.get("statement_id"),
            "statement_code": result.get("statement_code"),
            "period": result.get("period"),
            "start_year": result.get("start_year"),
            "end_year": result.get("end_year"),
            "period_count": result.get("period_count"),
        }
        frame = _to_frame(nodes, extra)
        frames.append(frame)
    if frames:
        return pd.concat(frames, ignore_index=True, sort=False)
    # Default columns when backend returns empty nodes.
    columns = [
        "symbol",
        "company_type",
        "statement_id",
        "statement_code",
        "period",
        "start_year",
        "end_year",
        "period_count",
        "id",
        "name",
        "parent_id",
        "level",
        "field",
        "order_index",
        "is_expanded",
        "has_children",
        "values",
    ]
    return pd.DataFrame(columns=columns)


def _build_periods_frame(results: Sequence[JsonDict]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for result in results:
        periods = result.get("periods")
        if not isinstance(periods, list):
            continue
        extra = {
            "symbol": result.get("symbol"),
            "company_type": result.get("company_type"),
        }
        frame = _to_frame(periods, extra)
        frames.append(frame)
    if frames:
        return pd.concat(frames, ignore_index=True, sort=False)
    return pd.DataFrame(columns=["symbol", "company_type", "year", "quarter", "period"])


def _unique_name(existing: set[str], name: Any, node_id: Any) -> str:
    base = str(name) if name not in (None, "") else f"node_{node_id}"
    candidate = base
    suffix = 1
    while candidate in existing:
        candidate = f"{base} ({suffix})"
        suffix += 1
    existing.add(candidate)
    return candidate


def _normalise_values(values: Sequence[Any], target_length: int) -> List[Any]:
    data = list(values)
    if len(data) < target_length:
        data.extend([None] * (target_length - len(data)))
    return data[:target_length]


def _build_values_long(results: Sequence[JsonDict]) -> pd.DataFrame:
    column_orders: Dict[str, Tuple[int, int]] = {}
    frames: List[pd.DataFrame] = []
    for result in results:
        periods = result.get("periods")
        nodes = result.get("nodes")
        if not isinstance(periods, list) or not isinstance(nodes, list) or not periods:
            continue

        base = pd.DataFrame(periods)
        if base.empty:
            continue

        if "year" not in base.columns:
            base["year"] = pd.NA
        if "quarter" not in base.columns:
            base["quarter"] = 0

        base.insert(0, "symbol", result.get("symbol"))
        base = base[["symbol", "year", "quarter"]]

        seen: set[str] = set()
        ordered_nodes: List[Tuple[int, int, Dict[str, Any]]] = []
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            values = node.get("values")
            if not isinstance(values, Sequence):
                continue
            order_index = node.get("order_index")
            if isinstance(order_index, (int, float)):
                order_key = int(order_index)
            else:
                order_key = 10**6 + idx
            ordered_nodes.append((order_key, idx, node))
        ordered_nodes.sort(key=lambda item: (item[0], item[1]))

        for _, _, node in ordered_nodes:
            values = node.get("values") or []
            column_name = _unique_name(seen, node.get("name"), node.get("id"))
            node_id = node.get("id")
            try:
                node_rank = int(node_id)
            except (TypeError, ValueError):
                node_rank = len(column_orders)
            order_key = node.get("order_index")
            if isinstance(order_key, (int, float)):
                order_rank = int(order_key)
            else:
                order_rank = 10**6
            column_orders[column_name] = min(
                column_orders.get(column_name, (order_rank, node_rank)),
                (order_rank, node_rank),
            )
            base[column_name] = _normalise_values(values, len(base))

        frames.append(base)

    if frames:
        combined = pd.concat(frames, ignore_index=True, sort=False)
        value_columns = [col for col in combined.columns if col not in {"symbol", "year", "quarter"}]
        value_columns.sort(key=lambda col: column_orders.get(col, (10**6, float("inf"))))
        return combined[["symbol", "year", "quarter", *value_columns]]

    return pd.DataFrame(columns=["symbol", "year", "quarter"])


def _format_period_label(period: Mapping[str, Any]) -> str:
    label = period.get("period")
    if label:
        return str(label)
    year = period.get("year")
    quarter = period.get("quarter")
    if quarter and quarter not in (0, "0"):
        return f"Q{quarter} {year}"
    return str(year)


def _build_values_cross(results: Sequence[JsonDict]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    period_orders: Dict[str, int] = {}

    for result in results:
        periods = result.get("periods")
        nodes = result.get("nodes")
        if not isinstance(periods, list) or not isinstance(nodes, list) or not periods:
            continue

        period_labels: List[str] = []
        seen_labels: set[str] = set()
        for position, period in enumerate(periods):
            label = _format_period_label(period)
            if label in seen_labels:
                label = _unique_name(seen_labels, label, f"period_{position}")
            else:
                seen_labels.add(label)
            period_labels.append(label)
            period_orders[label] = min(period_orders.get(label, position), position)

        rows: List[Dict[str, Any]] = []
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            values = node.get("values")
            if not isinstance(values, Sequence):
                continue

            row: Dict[str, Any] = {
                "symbol": result.get("symbol"),
                # "company_type": result.get("company_type"),
                # "statement_id": result.get("statement_id"),
                # "statement_code": result.get("statement_code"),
                "node_id": node.get("id"),
                "name": node.get("name"),
                # "parent_id": node.get("parent_id"),
                # "level": node.get("level"),
                "order_index": node.get("order_index"),
                # "field": node.get("field"),
            }
            normalised = _normalise_values(values, len(period_labels))
            for label, value in zip(period_labels, normalised):
                row[label] = value
            rows.append(row)

        if not rows:
            continue
        frame = pd.DataFrame(rows)
        frame = frame.sort_values(
            by=["symbol", "order_index", "node_id"], kind="mergesort"
        ).reset_index(drop=True)
        frame.drop(columns=["order_index","node_id"], inplace=True)
        frames.append(frame)

    if frames:
        combined = pd.concat(frames, ignore_index=True, sort=False)
        meta_columns = [
            "symbol",
            "name",
            "node_id",
            "parent_id",
            "level",
            "order_index",
            "field",
            "company_type",
            "statement_id",
            "statement_code",
        ]
        meta_columns = [col for col in meta_columns if col in combined.columns]
        value_columns = [col for col in combined.columns if col not in meta_columns]
        value_columns.sort(key=lambda col: period_orders.get(col, 10**6))
        return combined[meta_columns + value_columns]

    return pd.DataFrame(
        columns=[
            "symbol",
            "name",
            "node_id",
            "parent_id",
            "level",
            "order_index",
            "field",
            "company_type",
            "statement_id",
            "statement_code",
        ]
    )


def _build_values_frame(results: Sequence[JsonDict], values_format: ValuesFormat) -> pd.DataFrame:
    if values_format == "long":
        return _build_values_long(results)
    if values_format == "cross":
        return _build_values_cross(results)
    raise ValueError(f"Unsupported values_format: {values_format!r}")


class ReportingClient(BaseClient):
    """Facade cung cấp  báo cáo tài chính."""

    def __init__(self, session: "HttpSession") -> None:
        super().__init__(session=session)

    def statement(
        self,
        symbol: str | Sequence[str],
        statement: StatementStr,
        start_year: int,
        end_year: int,
        period: PeriodType,
        values_format: ValuesFormat = "long",
    ) -> pd.DataFrame:
        """
        Lấy dữ liệu giá trị báo cáo tài chính theo chuỗi symbol đã cung cấp.

        Quy trình:
        1) Chuẩn hóa symbol và validate tham số năm/kỳ.
        2) Validate loại doanh nghiệp; khi thất bại -> raise ``CompanyTypeMismatchError``.
        3) Tự động loại bỏ symbol sai loại (nếu có) & tiếp tục gọi API lấy giá trị báo cáo.
        4) Trả về dictionary chứa DataFrame và metadata phục vụ hiển thị/phan tích.

        Parameters
        ----------
        symbol : str | Sequence[str]
            Mã cổ phiếu hoặc danh sách mã.
        statement : StatementStr
            Loại báo cáo: ``"balance"``, ``"income"``, ``"cflow_direct"``, ``"cflow_indirect"``.
        start_year : int
            Năm bắt đầu (>= 1900).
        end_year : int
            Năm kết thúc (>= start_year).
        period : PeriodType
            Chu kỳ báo cáo (`"year"` hoặc `"quarter"`).
        values_format : {"long", "cross"}, default "long"
            Định dạng bảng giá trị trả về.
            - `"long"`: mỗi hàng tương ứng một kỳ (`symbol`, `year`, `quarter`) với các chỉ tiêu trải ngang.
            - `"cross"`: mỗi hàng là một chỉ tiêu, các cột tương ứng từng kỳ báo cáo.

        Returns
        -------
            DataFrame
            
        Examples
        --------
        ```python
        from finlens import client
        cli = client(api_key="sk_live_...")
        results=cli.reporting.statement(
            symbol=['HPG','vds'],
            statement='balance',
            period='quarter',
            start_year=2018,
            end_year=2023,
            values_format='cross'
        )
        ```
        """
        symbols = normalize_symbols(symbol)
        _validate_year_range(start_year, end_year)
        period_value = _ensure_period(period)
        if values_format not in ("long", "cross"):
            raise ValueError("values_format must be 'long' hoặc 'cross'.")
        statement_id = map_statement_to_int(statement)

        validation = financials_core.validate_company_types(self.session, symbols)
        if not validation.get("ok"):
            raise CompanyTypeMismatchError(validation.get("message") or "Không xác định được loại doanh nghiệp cho danh sách symbol.")
        if validation.get("ok") :
            removed_symbols= validation.get("removed_symbols",None)
            if isinstance(removed_symbols,list) and len(removed_symbols)>0:
                print(validation.get("message") or f"Đã loại bỏ các symbol sai loại doanh nghiệp: {removed_symbols}")
        filtered_symbols = validation.get("filtered_symbols")
        if not isinstance(filtered_symbols, list) or not filtered_symbols:
            message = validation.get("message") or "Danh sách symbol hợp lệ rỗng sau bước lọc loại doanh nghiệp."
            raise CompanyTypeMismatchError(message)

        filtered_symbols = normalize_symbols(filtered_symbols)

        statement_payload = financials_core.fetch_statement_values(
            self.session,
            symbols=filtered_symbols,
            statement_id=statement_id,
            start_year=start_year,
            end_year=end_year,
            period=period_value,
        )

        if not statement_payload.get("ok", False):
            raise CompanyTypeMismatchError(
                statement_payload.get("message")
                or "Backend trả về ok=false cho request statements/values."
            )
        warning=statement_payload.get('warning',None)
        if warning is not None:
            print(warning)
        results = statement_payload.get("results") or []
        if not isinstance(results, list):
            raise CompanyTypeMismatchError("Payload statements/values không đúng định dạng mong đợi.")

        nodes_df = _build_nodes_frame(results)
        periods_df = _build_periods_frame(results)
        values_df = _build_values_frame(results, values_format)
        nodes_df = attach_warning(nodes_df, validation.get("message"))
        values_df = attach_warning(values_df, validation.get("message"))

        meta = {
            "validation": validation,
            "parameters": statement_payload.get("parameters"),
            "filtered_symbols": filtered_symbols,
        }
        values_df.dropna(axis=1,how='all',inplace=True)
        # {
        #     "nodes": nodes_df,
        #     "values": values_df,
        #     "periods": periods_df,
        #     "meta": meta,
        #     "raw": statement_payload,
        # }
        return values_df