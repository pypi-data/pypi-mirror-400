# ENTSO-E API Python Package

A Python library for accessing ENTSO-E Transparency Platform API endpoints.

## Highlights

- Easy access to all ENTSO-E Transparency Platform API endpoints
- Well-documented, easy to use and highly consistent with the API
- Automatically splits up large requests into multiple smaller calls to the API
- Intelligent retry mechanism with exponential backoff for connection errors and service unavailability
- Returns meaningful error messages if something goes wrong

## Install

Install the package from [pypi](https://pypi.org/project/entsoe-apy/) using pip:

```sh
pip install entsoe-apy
```

## Quick Start

### API Key

You need an ENTSOE API Key (also called token) refer to the [official documentation](https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token) on how to obtain it. The package expects an environment variable called `ENTSOE_API` to be set with your API key. See [Configuration](https://entsoe-apy.berrisch.biz/configuration) for more details and options.

### Query Day-Ahead Prices

The package structure mirrors the [official ENTSO-E API docs](https://documenter.getpostman.com/view/7009892/2s93JtP3F6). So for querying "12.1.D Energy Prices" we need the `entsoe.Market` module and use the `EnergyPrices` class.

After initializing the class, we can query the data using the query_data method.

```python
from pandas import DataFrame
from entsoe.Market import EnergyPrices
from entsoe.utils import extract_records, add_timestamps

# Query energy prices
result = EnergyPrices(
    in_domain="10YNL----------L", # Netherlands
    out_domain="10YNL----------L",
    period_start=202012312300,
    period_end=202101022300,
).query_api()

# Convert to DataFrame-ready records
records = extract_records(result)
records = add_timestamps(records)
df = DataFrame(records)
```

| period_time_interval.start | time_series.period.point.position | time_series.period.point.price_amount | time_series.business_type | time_series.currency_unit_name | time_series.price_measure_unit_name | time_series.period.resolution |
| :------------------------- | --------------------------------: | ------------------------------------: | :------------------------ | :----------------------------- | :---------------------------------- | :---------------------------- |
| 2018-09-30T22:00Z          |                                 1 |                                  49.3 | A62                       | EUR                            | MWH                                 | PT15M                         |
| 2018-09-30T22:00Z          |                                 2 |                                 44.38 | A62                       | EUR                            | MWH                                 | PT15M                         |
| 2018-09-30T22:00Z          |                                 3 |                                 36.99 | A62                       | EUR                            | MWH                                 | PT15M                         |
| 2018-09-30T22:00Z          |                                 4 |                                 35.54 | A62                       | EUR                            | MWH                                 | PT15M                         |
| 2018-09-30T22:00Z          |                                 5 |                                  46.5 | A62                       | EUR                            | MWH                                 | PT15M                         |


The structure of the `result` object depends on the queried data. See the [examples](https://entsoe-apy.berrisch.biz/examples) for more details.

## Next Steps

- [ENTSOE](https://entsoe-apy.berrisch.biz/ENTSOE/index) - Class documentation
- [Mappings](https://entsoe-apy.berrisch.biz/mappings) - EIC codes and area mappings
- [Examples](https://entsoe-apy.berrisch.biz/examples) - Practical examples and use cases
- [Utilities](https://entsoe-apy.berrisch.biz/utilities) - Utility functions for data processing


## Contributions

Contributions are welcome! Please open an issue or submit a pull request.