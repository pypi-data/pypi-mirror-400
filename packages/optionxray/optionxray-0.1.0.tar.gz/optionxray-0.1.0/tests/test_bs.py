import math

from optionxray.bs import price_bs
from optionxray.instruments import Option


def test_put_call_parity():
    option_call = Option(spot=100, strike=100, maturity=1.0, rate=0.02, dividend=0.01, option_type="call")
    option_put = Option(spot=100, strike=100, maturity=1.0, rate=0.02, dividend=0.01, option_type="put")
    vol = 0.2
    call_price = price_bs(option_call, vol)
    put_price = price_bs(option_put, vol)

    lhs = call_price - put_price
    rhs = option_call.spot * math.exp(-option_call.dividend * option_call.maturity) - option_call.strike * math.exp(-option_call.rate * option_call.maturity)

    assert abs(lhs - rhs) < 1e-6
