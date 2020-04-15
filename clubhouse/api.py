import json
import logging
from os import path
from typing import Dict
from urllib.parse import urlparse

import requests

ENDPOINT_HOST = "https://api.clubhouse.io"
ENDPOINT_PATH = "/api/v3"

ClubhouseStory = Dict[str, object]
ClubhouseUser = Dict[str, object]
ClubhouseComment = Dict[str, str]
ClubhouseTask = Dict[str, str]
ClubhouseLabel = Dict[str, str]
ClubhouseFile = Dict[str, str]

logger = logging.getLogger("clubhouse")


class ClubhouseClient(object):
    def __init__(self, api_key, ignored_status_codes=None):
        self.ignored_status_codes = ignored_status_codes or []
        self.api_key = api_key

    def get(self, *segments, **kwargs):
        return self._request("get", *segments, **kwargs)

    def post(self, *segments, **kwargs):
        return self._request("post", *segments, **kwargs)

    def put(self, *segments, **kwargs):
        return self._request("put", *segments, **kwargs)

    def delete(self, *segments, **kwargs):
        return self._request("delete", *segments, **kwargs)

    def _request(self, method, *segments, **kwargs):
        if not segments[0].startswith(ENDPOINT_PATH):
            segments = [ENDPOINT_PATH, *segments]

        url = path.join(ENDPOINT_HOST, *[str(s).strip("/") for s in segments])

        # See the docs for more details on how the prefix is determined
        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        prefix = "&" if urlparse(url)[4] else "?"

        headers = {"Content-Type": "application/json"}

        response = requests.request(
            method, url + f"{prefix}token={self.api_key}", **kwargs,
            headers=headers
        )
        if (
            response.status_code > 299
            and response.status_code not in self.ignored_status_codes
        ):
            logger.error(
                f"Status code: {response.status_code}, Content: {response.text}"
            )
            response.raise_for_status()
        if response.status_code == 204:
            return {}

        return response

    def _list_items(self, method, *segments, **kwargs):
        result = self._request(method, *segments, **kwargs)
        items = result.json()
        while result.next:
            result = self._request(method, result.next)
            items.extend(result.json())
        return items

    def list_milestones(self):
        return self._list_items("get", "milestones")
