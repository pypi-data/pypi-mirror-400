# %%

import pytest

from entsoe.config import get_config
from entsoe.Market import EnergyPrices
from entsoe.utils import extract_records


@pytest.mark.skipif(
    get_config().security_token is None,
    reason="ENTSOE_API environment variable not set",
)
def test_extract_records():
    EIC = "10YNL----------L"
    period_start = 202001010000
    period_end = 202001030000
    result = EnergyPrices(
        in_domain=EIC,
        out_domain=EIC,
        period_start=period_start,
        period_end=period_end,
    ).query_api()

    result_records = extract_records(result)  # Assert that we got a result back
    assert result_records is not None and len(result_records) > 0

    # Assert that result_records is a list of dicts (without nested structures)
    assert isinstance(result_records, list)
    assert all(isinstance(record, dict) for record in result_records)

    # Assert that each record is a non-nested dict.
    assert all(
        isinstance(value, (int, float, str, type(None)))
        for record in result_records
        for value in record.values()
    )

    result_records_ts = extract_records(
        result, domain="time_series"
    )  # Assert that we got a result back
    assert result_records_ts is not None and len(result_records_ts) > 0

    # Assert that result_records_ts is a list of dicts (without nested structures)
    assert isinstance(result_records_ts, list)
    assert all(isinstance(record, dict) for record in result_records_ts)

    # Assert that each record is a non-nested dict.
    assert all(
        isinstance(value, (int, float, str, type(None)))
        for record in result_records_ts
        for value in record.values()
    )
