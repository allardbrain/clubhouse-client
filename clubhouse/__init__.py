__version__ = "0.3.0"

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

    def search_stories(self, **kwargs):
        result = self._request("get", "search", "stories", json=kwargs)
        items = result["data"]
        while "next" in result and result["next"]:
            result = self._request("get", result["next"])
            items = [*items, *result["data"]]
        return items

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
        prefix = "&" if urlparse(url)[4] else "?"

        response = requests.request(
            method, url + f"{prefix}token={self.api_key}", **kwargs
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
        return response.json()
