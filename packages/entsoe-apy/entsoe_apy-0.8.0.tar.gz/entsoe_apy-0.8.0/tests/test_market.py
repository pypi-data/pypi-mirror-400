import pytest

from entsoe.config import get_config
from entsoe.Market import EnergyPrices


@pytest.mark.skipif(
    get_config().security_token is None,
    reason="ENTSOE_API environment variable not set",
)
def test_energy_prices():
    EIC = "10YNL----------L"
    period_start = 202001010000
    period_end = 202501010000
    object = EnergyPrices(
        in_domain=EIC,
        out_domain=EIC,
        period_start=period_start,
        period_end=period_end,
    )

    result = object.query_api()
    # Assert that we got a result back
    assert result, "Expected non-empty result from query_api()"
