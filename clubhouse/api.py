import json
import logging
from os import path
from urllib.parse import urlparse

import requests

ENDPOINT_HOST = "https://api.clubhouse.io"
ENDPOINT_PATH = "/api/v3"

logger = logging.getLogger("clubhouse")


class ClubhouseClient(object):
    def __init__(self, api_key, ignored_status_codes=None):
        self.ignored_status_codes = ignored_status_codes or []
        self.api_key = api_key

    def _request(self, method, data=None, *segments, **kwargs):
        '''An internal helper method for calling any endpoint.

        Args:
            method (str): Must be "get", "post", "put" or "delete"
            data (dict): Can contain any of the body parameters listed in the
                API reference for the endpoint. Defaults to None.
        Returns:
            A response object
        '''

        if not segments[0].startswith(ENDPOINT_PATH):
            segments = [ENDPOINT_PATH, *segments]

        url = path.join(ENDPOINT_HOST, *[str(s).strip("/") for s in segments])

        # See the docs for more details on how the prefix is determined
        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        prefix = "&" if urlparse(url)[4] else "?"

        headers = {"Content-Type": "application/json"}
        data = json.dumps(data)

        # https://requests.readthedocs.io/en/master/api/#requests.request
        response = requests.request(
            method, url + f"{prefix}token={self.api_key}", headers=headers,
            data=data, **kwargs
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

    #############
    #  Actions  #
    #############

    def _create_item(self, method, data, *segments, **kwargs):
        '''An internal helper method for calling any "Create"-related endpoint.

        Args:
            method (str): Must be "get", "post", "put" or "delete"
            data (dict): Can contain any of the body parameters listed in the
                API reference for the endpoint.
        Returns:
            A JSON object containing information about the new item
        '''
        result = self._request(method, data, *segments, **kwargs)
        return result.json()

    def _get_item(self, method, *segments, **kwargs):
        '''An internal helper method for calling any "Get"-related endpoint.

        Args:
            method (str): Must be "get", "post", "put" or "delete"
            id (int): The requested item's ID
        Returns:
            A JSON object containing information about the requested item
        '''
        result = self._request(method, None, *segments, **kwargs)
        return result.json()

    def _list_items(self, method, *segments, **kwargs):
        '''An internal helper method for calling any "List"-related endpoint.

        Args:
            method (str): Must be "get"
        Returns:
            A list of dictionaries, where each dictionary is one item
        '''
        result = self._request(method, None, *segments, **kwargs)
        items = result.json()
        while result.next:
            result = self._request(method, None, result.next, **kwargs)
            items.extend(result.json())
        return items

    ################
    #  Milestones  #
    ################

    def create_milestone(self, id, **kwargs):
        '''Create a Milestone.
        https://clubhouse.io/api/rest/v3/#Create-Milestone

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.create_milestone({'name': 'TEST'})

        Args:
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.
        Returns:
            A JSON object containing information about the new Milestone.
        '''
        segments = ["milestones"]
        return self._create_item("post", data, *segments, **kwargs)

    def get_milestone(self, id, **kwargs):
        '''Retrieve a specific Milestone.
        https://clubhouse.io/api/rest/v3/#Get-Milestone

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.get_milestone(123)

        Args:
            id (int): The Milestone ID

        Returns:
            A JSON object containing information about the requested Milestone.
        '''
        segments = ["milestones", id]
        return self._get_item("get", *segments, **kwargs)

    def list_milestones(self, **kwargs):
        '''List all Milestones.
        https://clubhouse.io/api/rest/v3/#List-Milestones

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_milestones()

        Returns:
            A list of dictionaries, where each dictionary is one Milestone.
        '''
        segments = ["milestones"]
        return self._list_items("get", *segments, **kwargs)
