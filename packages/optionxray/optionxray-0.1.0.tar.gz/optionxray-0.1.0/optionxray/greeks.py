"""Black-Scholes analytic Greeks."""

from __future__ import annotations

import math

from .bs import _d1_d2, _norm_cdf, _norm_pdf
from .instruments import Option

_EPS = 1e-12


def greeks_bs(option: Option, vol: float) -> dict[str, float]:
    """Return delta, gamma, vega, theta, rho for a European option."""

    t = max(option.maturity, _EPS)
    vol = max(vol, _EPS)
    df_r = math.exp(-option.rate * t)
    df_q = math.exp(-option.dividend * t)
    d1, d2 = _d1_d2(option, vol)

    delta_call = df_q * _norm_cdf(d1)
    delta_put = df_q * (_norm_cdf(d1) - 1.0)
    gamma = df_q * _norm_pdf(d1) / (option.spot * vol * math.sqrt(t))
    vega = option.spot * df_q * _norm_pdf(d1) * math.sqrt(t)

    term1 = -(option.spot * df_q * _norm_pdf(d1) * vol) / (2.0 * math.sqrt(t))
    if option.option_type == "call":
        theta = term1 - option.rate * option.strike * df_r * _norm_cdf(d2) + option.dividend * option.spot * df_q * _norm_cdf(d1)
        rho = option.strike * t * df_r * _norm_cdf(d2)
        delta = delta_call
    else:
        theta = term1 + option.rate * option.strike * df_r * _norm_cdf(-d2) - option.dividend * option.spot * df_q * _norm_cdf(-d1)
        rho = -option.strike * t * df_r * _norm_cdf(-d2)
        delta = delta_put

    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta,
        "rho": rho,
    }


__all__ = ["greeks_bs"]
