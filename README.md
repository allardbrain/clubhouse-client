# shortcut-client
Python client for Clubhouse

## Installation

The package is available on [pypi](https://pypi.org/project/shortcut/) and can
be installed like any other packages.

    $ pip install shortcut

## Usage

Refer to [Clubhouse API Docs](https://shortcut.io/api/rest/v2/) for more information.

```python
from shortcut import ClubhouseClient

shortcut = ClubhouseClient('your api key')

story = {'name': 'A new story', 'description': 'Do something!'}
shortcut.post('stories', json=story)
```
