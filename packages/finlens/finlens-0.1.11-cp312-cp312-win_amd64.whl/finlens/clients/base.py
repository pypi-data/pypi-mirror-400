# finlens\clients\base.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from private_core.http_core import HttpSession


class BaseClient:
    """Base class for all FinLens client modules providing shared HTTP session access."""

    def __init__(self, session: "HttpSession") -> None:
        self._session = session

    @property
    def session(self) -> "HttpSession":
        return self._session
