from __future__ import annotations
import pandas as pd
from typing import Sequence, Literal
from .types import StatementStr, PeriodType, STATEMENT_TO_INT

class CompanyTypeMismatchError(ValueError):
    """Raised when symbols belong to multiple company types and on_mismatch='error'."""

def normalize_symbols(symbols: str | Sequence[str]) -> list[str]:
    if isinstance(symbols, str):
        s = symbols.strip().upper()
        if not s:
            raise ValueError("symbols is empty")
        return [s]
    out = [str(s).strip().upper() for s in symbols if str(s).strip()]
    if not out:
        raise ValueError("symbols list is empty")
    return out

def map_statement_to_int(statement: StatementStr) -> int:
    try:
        return STATEMENT_TO_INT[statement]
    except KeyError:
        raise ValueError(f"Unsupported statement: {statement!r}")

def attach_warning(df: pd.DataFrame, message: str | None) -> pd.DataFrame:
    if message and hasattr(df, "__dict__"):
        try:
            df.__dict__["_finlens_warning"] = message
        except Exception:
            pass
    return df
