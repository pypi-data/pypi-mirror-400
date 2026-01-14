from optionxray.bs import price_bs
from optionxray.instruments import Option
from optionxray.iv import implied_vol_bs


def test_implied_vol_recovery():
    option = Option(spot=100, strike=105, maturity=0.5, rate=0.01, dividend=0.0, option_type="call")
    true_vol = 0.25
    market_price = price_bs(option, true_vol)
    result = implied_vol_bs(option, market_price)

    assert abs(result.implied_vol - true_vol) < 1e-4
