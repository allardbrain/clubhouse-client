# shortcut-client
Python client for Shortcut

## Installation

The package is available on [pypi](https://pypi.org/project/shortcut/) and can
be installed like any other packages.

    $ pip install shortcut

## Usage

Refer to [Shortcut API Docs](https://shortcut.com/api/rest/v3) for more information.

```python
from shortcut import ShortcutClient

shortcut = ShortcutClient('your api key')

story = {'name': 'A new story', 'description': 'Do something!'}
shortcut.post('stories', json=story)
```
