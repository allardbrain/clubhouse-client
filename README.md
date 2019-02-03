# clubhouse-client
Python client for Clubhouse

## Usage

Refer to [Clubhouse API Docs](https://clubhouse.io/api/rest/v2/) for more information.

```python
from clubhouse import ClubhouseClient

clubhouse = ClubhouseClient('your api key')

story = {'name': 'A new story', 'description': 'Do something!'}
clubhouse.post('stories', json=story)
```
