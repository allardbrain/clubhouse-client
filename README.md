# clubhouse-client
A python wrapper for the Clubhouse API

## Installation
This package is available on [pypi](https://pypi.org/project/clubhouse/) and can
be installed like any other package:

    $ pip install clubhouse

## Usage

Refer to the [Clubhouse API Docs](https://clubhouse.io/api/rest/v3/) for information on required and optional parameters for each endpoint.

```python
from clubhouse import ClubhouseClient

conn = ClubhouseClient('your api key')
conn.list_milestones()
```
