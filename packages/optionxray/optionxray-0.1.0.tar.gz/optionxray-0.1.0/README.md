# OptionXRay

OptionXRay is a production-ready Python package for pricing vanilla European options and explaining **why** the market price is what it is. It combines Black–Scholes pricing with implied volatility, Greeks, scenario analysis, and a plain-English report.

## Why options trade where they trade

Option prices are driven by the probability-weighted payoff of the option, discounted back to today. In practice, markets quote **implied volatility** rather than price: traders back out the volatility that makes a model price match the market price, then use that volatility as a quoting language across strikes and maturities.

Key drivers of price include:
- **Spot price**: higher spot makes calls more valuable and puts less valuable.
- **Volatility**: higher volatility increases the chance of large moves, usually raising both call and put prices.
- **Time**: more time generally increases option value because more paths can end in-the-money.
- **Rates and dividends**: the discounted value of the strike and the carry on the underlying.

## Intrinsic vs extrinsic value

Intrinsic value is the immediate payoff if exercised today (e.g., `max(S-K, 0)` for a call). Extrinsic value (time value) is everything beyond intrinsic value and reflects volatility, time, and rates. This package decomposes both.

## What the Greeks mean

- **Delta**: sensitivity to spot.
- **Gamma**: curvature of delta; higher gamma means delta changes quickly.
- **Vega**: sensitivity to volatility.
- **Theta**: sensitivity to time decay.
- **Rho**: sensitivity to interest rates.

Greeks tell you which drivers matter most in the current state of the world, and OptionXRay highlights the largest ones.

## Why Black–Scholes is used

Black–Scholes is not a perfect model, but it is a standard quoting language. Market participants use it to quote implied volatility surfaces so that pricing and risk can be compared across strikes and maturities.

## Installation

```bash
pip install optionxray
```

## Quickstart

```python
from optionxray import Market, Option, XRay

option = Option(spot=100, strike=105, maturity=0.5, rate=0.01, dividend=0.0, option_type="call")
market = Market(market_price=4.2)

scenarios = [
    {"name": "Spot +2%", "dS_pct": 0.02},
    {"name": "Vol +3 pts", "dvol_abs": 0.03},
    {"name": "Rates +50bp", "dr_abs": 0.005},
    {"name": "Time +10d", "dT_days": 10},
]

xray = XRay(option, market)
result = xray.run(scenarios=scenarios)

print(result.summary_text)
print(result.scenarios_df)
```

Example output (truncated):

```
OptionXRay Report
=
Option details:
- spot: 100
- strike: 105
- maturity: 0.5
- rate: 0.01
- dividend: 0.0
- type: call

Theoretical price (BS): 4.1876
Market price: 4.2000
Implied volatility: 24.91%
Intrinsic value: 0.0000
Extrinsic value: 4.1876

Key drivers (largest Greeks):
- vega increases price by 12.0810 per unit move
- delta increases price by 0.4295 per unit move
- theta decreases price by 4.2601 per unit move

Scenario highlights:
- Vol +3 pts: increase of 0.3662 (price 4.5538)
- Spot +2%: increase of 0.8453 (price 5.0329)
- Time +10d: decrease of -0.1064 (price 4.0812)
```

## API Overview

### Functional API

```python
from optionxray.bs import price_bs
from optionxray.iv import implied_vol_bs
from optionxray.greeks import greeks_bs
from optionxray.instruments import Option

option = Option(spot=100, strike=100, maturity=1.0, rate=0.02, dividend=0.01, option_type="call")
price = price_bs(option, vol=0.2)
ivs = implied_vol_bs(option, market_price=price)
print(ivs.implied_vol)
print(greeks_bs(option, vol=0.2))
```

### Scenario format

Each scenario is a dict with keys:
- `name` (required)
- `dS_pct` or `dS_abs`
- `dvol_abs` (vol points) or `dvol_pct`
- `dr_abs` (absolute rate change)
- `dq_abs` (absolute dividend yield change)
- `dT_days` (time passes forward)

## Development

Run tests with:

```bash
pytest
```

## License

MIT
