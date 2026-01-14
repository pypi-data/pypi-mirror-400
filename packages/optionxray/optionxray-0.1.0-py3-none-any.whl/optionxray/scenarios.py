"""Scenario engine for option pricing shocks."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

import pandas as pd

from .bs import price_bs
from .instruments import Option

_EPS = 1e-6


def _apply_scenario(option: Option, vol: float, scenario: dict) -> tuple[Option, float]:
    spot = option.spot
    if "dS_pct" in scenario:
        spot *= 1.0 + scenario["dS_pct"]
    if "dS_abs" in scenario:
        spot += scenario["dS_abs"]

    new_vol = vol
    if "dvol_pct" in scenario:
        new_vol *= 1.0 + scenario["dvol_pct"]
    if "dvol_abs" in scenario:
        new_vol += scenario["dvol_abs"]

    rate = option.rate + scenario.get("dr_abs", 0.0)
    dividend = option.dividend + scenario.get("dq_abs", 0.0)
    maturity = max(option.maturity - scenario.get("dT_days", 0.0) / 365.0, _EPS)

    shocked_option = replace(option, spot=spot, rate=rate, dividend=dividend, maturity=maturity)
    return shocked_option, max(new_vol, _EPS)


def run_scenarios(option: Option, vol: float, scenarios: Iterable[dict]) -> pd.DataFrame:
    """Run pricing scenarios and return a DataFrame of prices and P&L."""

    base_price = price_bs(option, vol)
    rows: list[dict[str, float | str]] = []
    for scenario in scenarios:
        name = scenario.get("name", "scenario")
        shocked_option, shocked_vol = _apply_scenario(option, vol, scenario)
        scenario_price = price_bs(shocked_option, shocked_vol)
        rows.append(
            {
                "name": name,
                "price": scenario_price,
                "pnl": scenario_price - base_price,
                "spot": shocked_option.spot,
                "vol": shocked_vol,
                "rate": shocked_option.rate,
                "dividend": shocked_option.dividend,
                "maturity": shocked_option.maturity,
            }
        )
    return pd.DataFrame(rows)


__all__ = ["run_scenarios"]
