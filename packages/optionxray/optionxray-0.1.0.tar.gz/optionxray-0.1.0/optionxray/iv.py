"""Implied volatility solver."""

from __future__ import annotations

from dataclasses import dataclass

from .bs import price_bs
from .instruments import Option

try:
    from scipy.optimize import brentq
except ImportError:  # pragma: no cover - scipy is required but keep fallback
    brentq = None


@dataclass(frozen=True)
class ImpliedVolResult:
    implied_vol: float
    iterations: int


def _bisection(option: Option, market_price: float, vol_low: float, vol_high: float, tol: float, max_iter: int) -> ImpliedVolResult:
    """Bisection solver for implied volatility."""

    low = vol_low
    high = vol_high
    price_low = price_bs(option, low) - market_price
    price_high = price_bs(option, high) - market_price
    if price_low * price_high > 0:
        raise ValueError("Market price outside vol bracket.")

    for i in range(1, max_iter + 1):
        mid = 0.5 * (low + high)
        diff = price_bs(option, mid) - market_price
        if abs(diff) < tol:
            return ImpliedVolResult(mid, i)
        if diff * price_low > 0:
            low = mid
            price_low = diff
        else:
            high = mid
            price_high = diff
    return ImpliedVolResult(mid, max_iter)


def implied_vol_bs(option: Option, market_price: float, *, vol_low: float = 1e-6, vol_high: float = 5.0, tol: float = 1e-8, max_iter: int = 200) -> ImpliedVolResult:
    """Solve for implied volatility given a market price."""

    if market_price <= 0:
        raise ValueError("Market price must be positive.")

    if brentq is not None:
        def objective(vol: float) -> float:
            return price_bs(option, vol) - market_price

        price_low = objective(vol_low)
        price_high = objective(vol_high)
        if price_low * price_high > 0:
            raise ValueError("Market price outside vol bracket.")
        implied = brentq(objective, vol_low, vol_high, xtol=tol, maxiter=max_iter)
        return ImpliedVolResult(implied, max_iter)

    return _bisection(option, market_price, vol_low, vol_high, tol, max_iter)


__all__ = ["implied_vol_bs", "ImpliedVolResult"]
