"""Main XRay interface for option explanation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .bs import extrinsic_value, intrinsic_value, price_bs
from .greeks import greeks_bs
from .instruments import Market, Option
from .iv import implied_vol_bs
from .report import generate_report
from .scenarios import run_scenarios


@dataclass(frozen=True)
class XRayResult:
    summary_text: str
    base: dict
    scenarios_df: pd.DataFrame


class XRay:
    """Orchestrates pricing, Greeks, scenarios, and explanation."""

    def __init__(self, option: Option, market: Market, vol: float | None = None) -> None:
        self.option = option
        self.market = market
        self.vol = vol

    def run(self, model: str = "bs", scenarios: Iterable[dict] | None = None) -> XRayResult:
        if model != "bs":
            raise ValueError("Only Black-Scholes (bs) model is supported.")

        market_price = self.market.market_price
        implied = None
        vol = self.vol
        if vol is None and market_price is not None:
            implied = implied_vol_bs(self.option, market_price).implied_vol
            vol = implied
        elif vol is not None and market_price is not None:
            implied = implied_vol_bs(self.option, market_price).implied_vol

        if vol is None:
            raise ValueError("Provide vol or market price to infer implied volatility.")

        theo_price = price_bs(self.option, vol)
        greeks = greeks_bs(self.option, vol)
        intrinsic = intrinsic_value(self.option)
        extrinsic = extrinsic_value(self.option, vol)

        scenario_list = list(scenarios or [])
        scenarios_df = run_scenarios(self.option, vol, scenario_list) if scenario_list else pd.DataFrame()

        option_details = {
            "spot": self.option.spot,
            "strike": self.option.strike,
            "maturity": self.option.maturity,
            "rate": self.option.rate,
            "dividend": self.option.dividend,
            "type": self.option.option_type,
        }

        summary_text = generate_report(
            option_details=option_details,
            market_price=market_price,
            theo_price=theo_price,
            implied_vol=implied,
            intrinsic=intrinsic,
            extrinsic=extrinsic,
            greeks=greeks,
            scenarios_df=scenarios_df,
        )

        base = {
            "theo_price": theo_price,
            "market_price": market_price,
            "implied_vol": implied,
            "greeks": greeks,
            "intrinsic": intrinsic,
            "extrinsic": extrinsic,
        }
        return XRayResult(summary_text=summary_text, base=base, scenarios_df=scenarios_df)


__all__ = ["XRay", "XRayResult"]
