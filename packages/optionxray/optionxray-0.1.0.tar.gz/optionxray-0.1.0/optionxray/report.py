"""Generate explanation reports for option pricing."""

from __future__ import annotations

import pandas as pd


def _format_pct(value: float) -> str:
    return f"{value:.2%}"


def _top_greeks(greeks: dict[str, float], top_n: int = 3) -> list[tuple[str, float]]:
    return sorted(greeks.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n]


def _scenario_highlights(scenarios_df: pd.DataFrame, top_n: int = 3) -> list[dict]:
    if scenarios_df.empty:
        return []
    ranked = scenarios_df.reindex(scenarios_df["pnl"].abs().sort_values(ascending=False).index)
    return ranked.head(top_n).to_dict(orient="records")


def generate_report(
    *,
    option_details: dict,
    market_price: float | None,
    theo_price: float,
    implied_vol: float | None,
    intrinsic: float,
    extrinsic: float,
    greeks: dict[str, float],
    scenarios_df: pd.DataFrame,
) -> str:
    """Create a plain English explanation report."""

    lines: list[str] = []
    lines.append("OptionXRay Report")
    lines.append("=")
    lines.append("Option details:")
    for key, value in option_details.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append(f"Theoretical price (BS): {theo_price:.4f}")
    if market_price is not None:
        lines.append(f"Market price: {market_price:.4f}")
    if implied_vol is not None:
        lines.append(f"Implied volatility: {_format_pct(implied_vol)}")

    lines.append(f"Intrinsic value: {intrinsic:.4f}")
    lines.append(f"Extrinsic value: {extrinsic:.4f}")

    lines.append("")
    lines.append("Key drivers (largest Greeks):")
    for greek, value in _top_greeks(greeks):
        direction = "increases" if value > 0 else "decreases"
        lines.append(f"- {greek} {direction} price by {abs(value):.4f} per unit move")

    highlights = _scenario_highlights(scenarios_df)
    if highlights:
        lines.append("")
        lines.append("Scenario highlights:")
        for row in highlights:
            pnl = row.get("pnl", 0.0)
            impact = "increase" if pnl > 0 else "decrease"
            lines.append(f"- {row.get('name')}: {impact} of {pnl:.4f} (price {row.get('price'):.4f})")

    return "\n".join(lines)


__all__ = ["generate_report"]
