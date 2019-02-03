# clubhouse-client
Python client for Clubhouse

## Installation

The package is available on [pypi](https://pypi.org/project/clubhouse/) and can
be installed like any other packages.

    $ pip install clubhouse

## Usage

Refer to [Clubhouse API Docs](https://clubhouse.io/api/rest/v2/) for more information.

```python
from clubhouse import ClubhouseClient

clubhouse = ClubhouseClient('your api key')

story = {'name': 'A new story', 'description': 'Do something!'}
clubhouse.post('stories', json=story)
```
