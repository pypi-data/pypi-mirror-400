"""Instrument dataclasses for option valuation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OptionType = Literal["call", "put"]


@dataclass(frozen=True)
class Option:
    """Vanilla European option contract details."""

    spot: float
    strike: float
    maturity: float
    rate: float = 0.0
    dividend: float = 0.0
    option_type: OptionType = "call"


@dataclass(frozen=True)
class Market:
    """Market observation for an option."""

    market_price: float | None = None
