"""Black-Scholes pricing utilities."""

from __future__ import annotations

import math

from .instruments import Option

_EPS = 1e-12


def _norm_cdf(x: float) -> float:
    """Standard normal CDF using erf for stability."""

    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    """Standard normal PDF."""

    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _d1_d2(option: Option, vol: float) -> tuple[float, float]:
    """Compute Black-Scholes d1 and d2 with edge-case handling."""

    t = max(option.maturity, _EPS)
    vol = max(vol, _EPS)
    fwd = option.spot * math.exp((option.rate - option.dividend) * t)
    log_fk = math.log(max(fwd, _EPS) / option.strike)
    vol_sqrt = vol * math.sqrt(t)
    d1 = (log_fk + 0.5 * vol * vol * t) / vol_sqrt
    d2 = d1 - vol_sqrt
    return d1, d2


def intrinsic_value(option: Option) -> float:
    """Return intrinsic value for a vanilla option."""

    if option.option_type == "call":
        return max(option.spot - option.strike, 0.0)
    return max(option.strike - option.spot, 0.0)


def price_bs(option: Option, vol: float) -> float:
    """Price a European option using Black-Scholes."""

    t = max(option.maturity, _EPS)
    df_r = math.exp(-option.rate * t)
    df_q = math.exp(-option.dividend * t)
    if vol <= _EPS:
        forward = option.spot * df_q / df_r
        if option.option_type == "call":
            return df_r * max(forward - option.strike, 0.0)
        return df_r * max(option.strike - forward, 0.0)

    d1, d2 = _d1_d2(option, vol)
    if option.option_type == "call":
        return option.spot * df_q * _norm_cdf(d1) - option.strike * df_r * _norm_cdf(d2)
    return option.strike * df_r * _norm_cdf(-d2) - option.spot * df_q * _norm_cdf(-d1)


def extrinsic_value(option: Option, vol: float) -> float:
    """Return extrinsic value using Black-Scholes."""

    return max(price_bs(option, vol) - intrinsic_value(option), 0.0)


__all__ = ["price_bs", "intrinsic_value", "extrinsic_value", "_norm_cdf", "_norm_pdf", "_d1_d2"]
