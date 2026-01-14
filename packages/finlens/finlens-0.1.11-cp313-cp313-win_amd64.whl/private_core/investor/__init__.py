"""
Investor namespace bridge for the FinLens private core.

Exports the default implementation expected by ``finlens.clients``.
"""

from .core_impl import InvestorCoreImpl

__all__ = ["InvestorCoreImpl"]
