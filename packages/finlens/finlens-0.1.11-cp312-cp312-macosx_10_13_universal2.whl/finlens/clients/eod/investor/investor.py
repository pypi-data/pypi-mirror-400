# finlens/clients/eod/investor.py
from __future__ import annotations

import importlib
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Hashable,
    Iterable,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Union,
    runtime_checkable,
)
import pandas as pd

from ...base import BaseClient
from finlens.exceptions import HttpError
from ..helper import _EodMixin, DateStr, InterValInvestor
from private_core.cache_core import CacheKey
from private_core.cache_mixin import BaseCacheMixin
from private_core.cache_policy import (
    touches_latest_trading_day,
    ttl_eod_history,
    ttl_eod_latest,
)

if TYPE_CHECKING:
    from private_core.http_core import HttpSession

# =========================
# Type aliases theo namespace (giữ Union[str, Sequence[str]])
# =========================
SymbolArg = Union[str, Sequence[str]]  # Stock
MarketArg = Union[str, Sequence[str]]  # Market / Index (VNINDEX, VN30,...)
SectorArg = Union[str, Sequence[str]]  # ICB code (level 4/5)

InvestorGroup = Literal[
    "foreign",
    "proprietary",
    "local_institutional",
    "local_individual",
    "foreign_institutional",
    "foreign_individual",

] 


def _unwrap_http_error(exc: Exception) -> Optional[HttpError]:
    current: Optional[BaseException] = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, HttpError):
            return current
        current = current.__cause__ or current.__context__
    return None


def _format_http_detail(payload: Any, http_error: HttpError) -> str:
    detail: Optional[str] = None
    if isinstance(payload, dict):
        raw_detail = payload.get("detail")
        if raw_detail is None and "message" in payload:
            raw_detail = payload["message"]
        if raw_detail is not None:
            detail = str(raw_detail)
        elif payload:
            detail = str(payload)
    elif isinstance(payload, bytes):
        detail = payload.decode("utf-8", errors="replace")
    elif payload is not None:
        detail = str(payload)

    if detail is None:
        args = getattr(http_error, "args", ())
        if args:
            detail = str(args[0])
        else:
            detail = str(http_error)
    return detail

# =========================
# InvestorCoreProto (import chuẩn; có fallback Protocol cho môi trường chưa build private_core)
# =========================
try:
    # Đường dẫn chuẩn khi đóng gói private_core
    from private_core.investor.InvestorCoreProto import InvestorCoreProto  # type: ignore
except Exception:
    @runtime_checkable
    class InvestorCoreProto(Protocol):
        session: "HttpSession"

        def fetch_df(self, namespace: str, op: str, params: dict) -> pd.DataFrame: ...


# =========================
# _InvestorBase
# =========================
class _InvestorBase(BaseCacheMixin, BaseClient, _EodMixin):
    """
    Base cho namespace investor.* — KHÔNG dùng trực tiếp.

    Vai trò:
    - Chuẩn hóa/validate tham số chung (ids, group, start, end, interval).
    - Ủy quyền fetch sang private_core qua self._core.fetch_df(...).
    - Trả về đúng pandas.DataFrame (private_core chịu trách nhiệm build DataFrame).
    """

    _endpoint_root: Literal["stock", "market", "sector"]  # subclass phải set
    _core: InvestorCoreProto                               # injected từ subclass

    def __init__(self, session: "HttpSession", core: InvestorCoreProto):
        super().__init__(session)
        if not isinstance(core, InvestorCoreProto):
            raise TypeError(f"core must implement InvestorCoreProto; got {type(core).__name__}")
        if not hasattr(core, "session"):
            raise TypeError(
                f"core {type(core).__name__} must expose a 'session' attribute for injection."
            )
        core.session = session  # type: ignore[attr-defined]
        self._core = core

        if not hasattr(self, "_endpoint_root"):
            raise AttributeError("Subclass must define _endpoint_root = 'stock'|'market'|'sector'.")

    # ---------- Normalizers ----------
    @staticmethod
    def _normalize_ids(ids: Union[str, Sequence[str]], *, label: str = "symbol") -> list[str]:
        """
        Chuẩn hóa SymbolArg/MarketArg/SectorArg về list[str].
        - Chấp nhận str hoặc Sequence[str]
        - Loại phần tử rỗng/whitespace
        """
        if isinstance(ids, str):
            s = ids.strip()
            if not s:
                raise ValueError(f"{label} is empty.")
            return [s]

        if isinstance(ids, Iterable):
            out = [x.strip() for x in ids if isinstance(x, str) and x.strip()]
            if not out:
                raise ValueError(f"{label} list is empty.")
            return out

        raise TypeError(f"{label} must be str or Sequence[str].")

    @staticmethod
    def _normalize_group(group: InvestorGroup) -> InvestorGroup:
        allow: tuple[InvestorGroup, ...] = (
            "foreign",
            "proprietary",
            "local_institutional",
            "local_individual",
            "foreign_institutional",
            "foreign_individual",
            "all",
        )
        if group not in allow:
            raise ValueError(f"Invalid investor_group={group!r}. Allowed: {allow}.")
        return group

    # ---------- Range/Interval validators (tận dụng _EodMixin) ----------
    def _normalize_range_and_interval(
        self,
        *,
        start: DateStr,
        end: DateStr,
        interval: InterValInvestor,
    ) -> tuple[str, str, InterValInvestor]:
        """
        - Validate & chuẩn hóa `start`, `end` về 'YYYY-MM-DD'
        - Validate `interval` theo whitelist của backend
        """
        start_iso, end_iso = self._normalize_range(start, end)     # từ _EodMixin
        interval_ok = self._validate_interval(interval)            # từ _EodMixin
        return start_iso, end_iso, interval_ok

    # ---------- Build common params ----------
    def _build_params(
        self,
        *,
        ids: Union[str, Sequence[str]],
        label: str,
        group: InvestorGroup,
        start: DateStr,
        end: DateStr,
        interval: InterValInvestor,
        extra: Optional[dict] = None,
    ) -> dict:
        """
        Trả về dict params đã hợp lệ để pass sang private_core:

        {
          'ids': list[str],
          'group': InvestorGroup,
          'start': 'YYYY-MM-DD',
          'end': 'YYYY-MM-DD',
          'interval': InterValInvestor,
          **extra
        }
        """
        ids_list = self._normalize_ids(ids, label=label)
        group_ok = self._normalize_group(group)
        start_iso, end_iso, interval_ok = self._normalize_range_and_interval(
            start=start, end=end, interval=interval
        )

        params = {
            "ids": ids_list,
            "group": group_ok,
            "start": start_iso,
            "end": end_iso,
            "interval": interval_ok,
        }
        if extra:
            params.update(extra)
        return params

    # ---------- Core bridge ----------
    def _cache_namespace(self, op: str) -> str:
        return f"investor:{self._endpoint_root}:{op}"

    @staticmethod
    def _to_hashable(value: Any) -> Hashable:
        if isinstance(value, (str, bytes, int, float, bool, type(None))):
            return value
        if isinstance(value, (list, tuple)):
            return tuple(_InvestorBase._to_hashable(v) for v in value)
        if isinstance(value, dict):
            return tuple(
                sorted((k, _InvestorBase._to_hashable(v)) for k, v in value.items())
            )
        return str(value)

    def _cache_key_from_params(self, params: dict) -> CacheKey:
        ids_key = tuple(params.get("ids", ()))
        group = params.get("group")
        start = params.get("start")
        end = params.get("end")
        interval = params.get("interval")
        extra_items = tuple(
            sorted(
                (k, self._to_hashable(v))
                for k, v in params.items()
                if k not in {"ids", "group", "start", "end", "interval"}
            )
        )
        return (ids_key, group, start, end, interval, extra_items)
    def _fetch_df(self, *, op: str, params: dict) -> pd.DataFrame:
        """
        Ủy quyền private_core lấy dữ liệu và đảm bảo đầu ra là DataFrame.

        Parameters
        ----------
        op : {'flow','breakdown','foreign_room'}   (tùy namespace)
        params : dict                              (đÃ CHUẨN HÓA bởi _build_params)

        Returns
        -------
        pandas.DataFrame
        """
        namespace = self._cache_namespace(op)
        key = self._cache_key_from_params(params)
        live = touches_latest_trading_day(params.get("end"))

        def _fetch() -> pd.DataFrame:
            try:
                df = self._core.fetch_df(self._endpoint_root, op, params)
            except Exception as exc:
                http_error = _unwrap_http_error(exc)
                if http_error is not None:
                    status_code = getattr(http_error, "status_code", None)
                    payload = getattr(http_error, "payload", None)
                    detail = _format_http_detail(payload, http_error)
                    code_label = f"HTTP {status_code}" if status_code is not None else "HTTP error"
                    raise RuntimeError(
                        f"private_core fetch failed: namespace={self._endpoint_root!r}, op={op!r} -> {code_label}: {detail}"
                    ) from None
                raise RuntimeError(
                    f"private_core fetch failed: namespace={self._endpoint_root!r}, op={op!r} -> {exc}"
                ) from exc

            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"private_core must return pandas.DataFrame; got {type(df).__name__}")
            return df

        return self._fetch_with_cache(
            namespace,
            key,
            live=live,
            fetcher=_fetch,
            ttl_live=ttl_eod_latest(),
            ttl_history=ttl_eod_history(),
            params=params,
        )

    # ---------- Feature guard ----------
    def _feature_not_available(self, name: str) -> None:
        raise AttributeError(
            f"'{self.__class__.__name__}.{name}()' is not available for namespace '{self._endpoint_root}'."
        )


def _instantiate_investor_core(
    factory: Any,
    session: "HttpSession",
) -> InvestorCoreProto:
    """
    Try to instantiate an investor core implementation from the provided factory.
    Accepts callables or classes that expect the HTTP session.
    """
    if isinstance(factory, type):
        try:
            core = factory(session=session)  # type: ignore[call-arg]
        except TypeError:
            core = factory(session)  # type: ignore[call-arg]
    elif callable(factory):
        try:
            core = factory(session=session)
        except TypeError:
            core = factory(session)
    else:
        raise TypeError("Investor core factory must be callable or class-like.")
    return core  # type: ignore[return-value]


def _load_investor_core(session: "HttpSession") -> InvestorCoreProto:
    """
    Locate and instantiate the private_core investor implementation.
    """
    module_candidates = (
        "private_core.investor.core_impl",
        "private_core.investor.core",
        "private_core.investor",
    )
    last_error: Optional[Exception] = None

    for module_name in module_candidates:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            last_error = exc
            continue

        factories: list[Any] = []
        candidate = getattr(module, "InvestorCoreImpl", None)
        if candidate is not None:
            factories.append(candidate)
        for attr in ("build_investor_core", "get_investor_core", "load_investor_core"):
            alt = getattr(module, attr, None)
            if alt is not None:
                factories.append(alt)

        for factory in factories:
            try:
                core = _instantiate_investor_core(factory, session)
            except Exception as exc:
                last_error = exc
                continue
            if isinstance(core, InvestorCoreProto):
                return core

    message = (
        "private_core investor implementation is required but could not be loaded. "
        "Ensure your private_core package exposes an InvestorCoreImpl(session) factory."
    )
    if last_error is not None:
        raise RuntimeError(message) from last_error
    raise RuntimeError(message)


def _create_investor_client(class_name: str, session: "HttpSession") -> "_InvestorBase":
    """
    Dynamically import the requested investor client subclass and bind it with the private core.
    """
    module_name = f"finlens.clients.eod.investor.{class_name}"
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise RuntimeError(f"Unable to import investor client module {module_name!r}.") from exc

    investor_cls = getattr(module, class_name, None)
    if investor_cls is None:
        raise RuntimeError(f"Module {module_name!r} does not define {class_name!r}.")

    core = _load_investor_core(session)
    client = investor_cls(session=session, core=core)  # type: ignore[call-arg]
    if not isinstance(client, _InvestorBase):
        raise TypeError(f"{class_name} must inherit from _InvestorBase.")
    return client


sys.modules.setdefault("investor", sys.modules[__name__])
