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

    def get(self, *segments, **kwargs):
        '''Included for backwards compatibility.
        Not used in versions above 0.3.0.
        '''
        return self._request("get", *segments, **kwargs)

    def post(self, *segments, **kwargs):
        '''Included for backwards compatibility.
        Not used in versions above 0.3.0.
        '''
        return self._request("post", *segments, **kwargs)

    def put(self, *segments, **kwargs):
        '''Included for backwards compatibility.
        Not used in versions above 0.3.0.
        '''
        return self._request("put", *segments, **kwargs)

    def delete(self, *segments, **kwargs):
        '''Included for backwards compatibility.
        Not used in versions above 0.3.0.
        '''
        return self._request("delete", *segments, **kwargs)

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

    def _create_item(self, data, *segments, **kwargs):
        '''An internal helper method for calling any "Create"-related endpoint.

        Args:
            method (str): Must be "get", "post", "put" or "delete"
            data (dict): Can contain any of the body parameters listed in the
                API reference for the endpoint.
        Returns:
            A JSON object containing information about the new item
        '''
        result = self._request("post", data, *segments, **kwargs)
        return result.json()

    def _delete_item(self, *segments, **kwargs):
        '''An internal helper method for calling any "Delete"-related endpoint.

        Returns:
            A JSON object containing information about the updated item
        '''
        result = self._request("delete", None, *segments, **kwargs)
        return result

    def _get_item(self, *segments, **kwargs):
        '''An internal helper method for calling any "Get"-related endpoint.

        Args:
            method (str): Must be "get", "post", "put" or "delete"
            id (int): The requested item's ID
        Returns:
            A JSON object containing information about the requested item
        '''
        result = self._request("get", None, *segments, **kwargs)
        return result.json()

    def _list_items(self, *segments, **kwargs):
        '''An internal helper method for calling any "List"-related endpoint.

        Args:
            method (str): Must be "get"
        Returns:
            A list of dictionaries, where each dictionary is one item
        '''
        result = self._request("get", None, *segments, **kwargs)
        items = result.json()
        while result.next:
            result = self._request("get", None, result.next, **kwargs)
            items.extend(result.json())
        return items

    def _update_item(self, data, *segments, **kwargs):
        '''An internal helper method for calling any "Update"-related endpoint.

        Args:
            data (dict): Can contain any of the body parameters listed in the
                API reference for the endpoint.
        Returns:
            A JSON object containing information about the updated item
        '''
        result = self._request("put", data, *segments, **kwargs)
        return result.json()


    ###########
    #  Epics  #
    ###########

    def list_epics(self, **kwargs):
        '''List all Epics.
        https://clubhouse.io/api/rest/v3/#List-Epics

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_epics()

        Returns:
            A list of dictionaries, where each dictionary is one Epic.
        '''
        segments = ["epics"]
        return self._list_items(*segments, **kwargs)

    def create_epic(self, data, **kwargs):
        '''Create an Epic.
        https://clubhouse.io/api/rest/v3/#Create-Epic

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.create_epic({'name': 'TEST'})

        Args:
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.
        Returns:
            A JSON object containing information about the new Epic.
        '''
        segments = ["epics"]
        return self._create_item(data, *segments, **kwargs)

    def get_epic(self, id, **kwargs):
        '''Retrieve a specific Epic.
        https://clubhouse.io/api/rest/v3/#Get-Epic

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.get_epic(123)

        Args:
            id (int): The Epic ID

        Returns:
            A JSON object containing information about the requested Epic.
        '''
        segments = ["epics", id]
        return self._get_item(*segments, **kwargs)

    def update_epic(self, id, data, **kwargs):
        '''Update a specific Epic.
        https://clubhouse.io/api/rest/v3/#Update-Epic

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.update_epic(123)

        Args:
            id (int): The Epic ID
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the updated Epic.
        '''
        segments = ["epics", id]
        return self._update_item(data, *segments, **kwargs)

    def create_epic_comment(self, id, data, **kwargs):
        '''Create a Comment on an Epic.
        https://clubhouse.io/api/rest/v3/#Create-Epic-Comment

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.create_epic_comment(123)

        Args:
            id (int): The Epic ID
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the new Comment.
        '''
        segments = ["epics", id, "comments"]
        return self._create_item(data, *segments, **kwargs)

    def list_epic_comments(self, id, **kwargs):
        '''List all Comments on an Epic.
        https://clubhouse.io/api/rest/v3/#List-Epic-Comments

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_epic_comments(123)

        Returns:
            A list of dictionaries, where each dictionary is one Comment on the
            Epic.
        '''
        segments = ["epics", id, "comments"]
        return self._list_items(*segments, **kwargs)

    def get_epic_comment(self, epic_id, comment_id, **kwargs):
        '''Retrieve a specific Comment on an Epic.
        https://clubhouse.io/api/rest/v3/#Get-Epic-Comment

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.get_epic_comment(123)

        Args:
            epic_id (int): The Epic ID
            comment_id (int): The Comment ID

        Returns:
            A JSON object containing information about the requested Comment.
        '''
        segments = ["epics", epic_id, "comments", comment_id]
        return self._get_item(*segments, **kwargs)

    def update_epic_comment(self, epic_id, comment_id, data, **kwargs):
        '''Update a specific Comment on an Epic.
        https://clubhouse.io/api/rest/v3/#Update-Epic-Comment

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.update_epic_comment(123)

        Args:
            epic_id (int): The Epic ID
            comment_id (int): The Comment ID
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the updated Comment.
        '''
        segments = ["epics", epic_id, "comments", comment_id]
        return self._update_item(data, *segments, **kwargs)

    def create_epic_comment_comment(self, epic_id, comment_id, data, **kwargs):
        '''Reply to a Comment on an Epic. (Create a Comment on a Comment.)
        https://clubhouse.io/api/rest/v3/#Create-Epic-Comment-Comment

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.create_epic_comment_comment(123)

        Args:
            epic_id (int): The Epic ID
            comment_id (int): The parent Comment ID
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the new Comment.
        '''
        segments = ["epics", epic_id, "comments", comment_id]
        return self._create_item(data, *segments, **kwargs)

    def delete_epic_comment(self, epic_id, comment_id, **kwargs):
        '''Delete a Comment on an Epic.
        https://clubhouse.io/api/rest/v3/#Delete-Epic-Comment

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.delete_epic_comment(123)

        Args:
            epic_id (int): The Milestone ID
            comment_id (int): The Comment ID

        Returns:
            An empty dictionary
        '''
        segments = ["epics", epic_id, "comments", comment_id]
        return self._delete_item(*segments, **kwargs)

    def delete_epic(self, id, **kwargs):
        '''Delete a specific Epic.
        https://clubhouse.io/api/rest/v3/#Delete-Epic

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.delete_epic(123)

        Args:
            id (int): The Epic ID

        Returns:
            An empty dictionary
        '''
        segments = ["epics", id]
        return self._delete_item(*segments, **kwargs)

    def list_epic_stories(self, id, **kwargs):
        '''List all Stories in an Epic.
        https://clubhouse.io/api/rest/v3/#List-Epic-Stories

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_epic_stories(123)

        Returns:
            A list of dictionaries, where each dictionary is one Story in the
            Epic.
        '''
        segments = ["epics", id, "stories"]
        return self._list_items(*segments, **kwargs)


    ################
    #  Milestones  #
    ################

    def create_milestone(self, data, **kwargs):
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
        return self._create_item(data, *segments, **kwargs)

    def delete_milestone(self, id, **kwargs):
        '''Delete a specific Milestone.
        https://clubhouse.io/api/rest/v3/#Delete-Milestone

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.delete_milestone(123)

        Args:
            id (int): The Milestone ID

        Returns:
            An empty dictionary
        '''
        segments = ["milestones", id]
        return self._delete_item(*segments, **kwargs)

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
        return self._get_item(*segments, **kwargs)

    def list_milestone_epics(self, id, **kwargs):
        '''List all Milestone Epics.
        https://clubhouse.io/api/rest/v3/#List-Milestone-Epics

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_milestone_epics(123)

        Returns:
            A list of dictionaries, where each dictionary is one Epic of the
            requested Milestone.
        '''
        segments = ["milestones", id, "epics"]
        return self._list_items(*segments, **kwargs)

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
        return self._list_items(*segments, **kwargs)

    def update_milestone(self, id, data, **kwargs):
        '''Update a specific Milestone.
        https://clubhouse.io/api/rest/v3/#Update-Milestone

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.update_milestone(123)

        Args:
            id (int): The Milestone ID
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the updated Milestone.
        '''
        segments = ["milestones", id]
        return self._update_item(data, *segments, **kwargs)


    ##############
    #  Projects  #
    ##############

    def list_projects(self, **kwargs):
        '''List all Projects.
        https://clubhouse.io/api/rest/v3/#List-Projects

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_projects()

        Returns:
            A list of dictionaries, where each dictionary is one Project.
        '''
        segments = ["projects"]
        return self._list_items(*segments, **kwargs)

    def create_project(self, data, **kwargs):
        '''Create a Project.
        https://clubhouse.io/api/rest/v3/#Create-Project

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.create_project({'name': 'TEST', 'team_id': 123})

        Args:
            data (dict): Can contain any of the body parameters listed in the
                API reference linked above as keys.

        Returns:
            A JSON object containing information about the new Project.
        '''
        segments = ["projects"]
        return self._create_item(data, *segments, **kwargs)

    def get_project(self, id, **kwargs):
        '''Retrieve a specific Project.
        https://clubhouse.io/api/rest/v3/#Get-Project

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.get_project(123)

        Args:
            id (int): The Project ID

        Returns:
            A JSON object containing information about the requested Project.
        '''
        segments = ["projects", id]
        return self._get_item(*segments, **kwargs)


    ###########
    #  Teams  #
    ###########

    def list_teams(self, **kwargs):
        '''List all Teams.
        https://clubhouse.io/api/rest/v3/#List-Teams

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_teams()

        Returns:
            A list of dictionaries, where each dictionary is one Team, including
            its workflow and states.
        '''
        segments = ["teams"]
        return self._list_items(*segments, **kwargs)

    def get_team(self, id, **kwargs):
        '''Retrieve a specific Team.
        https://clubhouse.io/api/rest/v3/#Get-Team

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.get_team(123)

        Args:
            id (int): The Team ID

        Returns:
            A JSON object containing information about the requested Team, its
            workflow, and states.
        '''
        segments = ["teams", id]
        return self._get_item(*segments, **kwargs)


    ###############
    #  Workflows  #
    ###############

    def list_workflows(self, **kwargs):
        '''List all Workflows.
        https://clubhouse.io/api/rest/v3/#List-Workflows

        Example:
            from clubhouse import ClubhouseClient
            conn = ClubhouseClient(API_KEY)
            conn.list_workflows()

        Returns:
            A list of dictionaries, where each dictionary is one Workflow.
        '''
        segments = ["workflows"]
        return self._list_items(*segments, **kwargs)
