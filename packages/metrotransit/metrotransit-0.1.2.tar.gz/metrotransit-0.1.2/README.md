# Metro Transit Python SDK

A community-built Python SDK for accessing Metro Transit's NexTrip data.

```python
>>> from metrotransit import Client
>>> from metrotransit.api.nex_trip import get_nextrip_route_id_direction_id_place_code as get_details

>>> client = Client(base_url="https://svc.metrotransit.org")

# Get upcoming trips for the westbound Green Line at East Bank Station
>>> get_details.sync('902', 0, 'EABK', client=client)
NexTripResult(...)
```

[![Total Downloads](https://img.shields.io/pepy/dt/metrotransit)][pypi]
[![Supported Versions](https://img.shields.io/pypi/pyversions/metrotransit.svg)][pypi]
[![GitHub last commit](https://img.shields.io/github/last-commit/bsoyka/metrotransit-sdk)][github]

## Installation

The SDK is [available on PyPI][pypi].
Install it with your preferred package manager:

```sh
$ uv add metrotransit
$ pip install metrotransit
```

The SDK officially supports Python 3.10+.

## Documentation

Every path/method combo in the official spec is represented as a Python module with four functions, and all parameters can be provided with method arguments:
  - `sync`: Blocking request that returns parsed data (if successful) or `None`
  - `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
  - `asyncio`: Like `sync` but async instead of blocking
  - `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

[github]: https://github.com/bsoyka/metrotransit-sdk
[pypi]: https://pypi.org/project/metrotransit/
