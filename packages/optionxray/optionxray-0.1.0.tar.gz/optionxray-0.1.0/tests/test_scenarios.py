from optionxray.instruments import Option
from optionxray.scenarios import run_scenarios


def test_scenario_engine_pnl():
    option = Option(spot=100, strike=100, maturity=1.0, rate=0.01, dividend=0.0, option_type="call")
    scenarios = [
        {"name": "spot_up", "dS_abs": 5.0},
        {"name": "vol_up", "dvol_abs": 0.05},
    ]
    df = run_scenarios(option, 0.2, scenarios)

    assert df.shape[0] == 2
    assert set(df["name"].tolist()) == {"spot_up", "vol_up"}
    assert df["pnl"].abs().sum() > 0
