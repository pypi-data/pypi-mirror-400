from typing import Dict, Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ListsClient(NamespacedClient):
    def by_id(self, list_id: str) -> OrkgResponse:
        """
        Lookup a list by ID to find the label and the IDs of its elements.
        :param list_id: the id of the list to lookup
        :return: an OrkgResponse object containing the list
        """
        is_list = "List" in self.client.resources.by_id(list_id).content["classes"]
        if not is_list:
            raise ValueError("the ID provided does not correspond to a list!")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.lists(list_id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_elements(self, list_id: str, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Get the complete representations of the elements in a list.
        :param list_id: the id of the list to lookup
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: an OrkgResponse object containing the elements in the list
        """
        is_list = "List" in self.client.resources.by_id(list_id).content["classes"]
        if not is_list:
            raise ValueError("the ID provided does not correspond to a list!")
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.lists(list_id).elements.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.lists(list_id).elements.GET()
        return self.client.wrap_response(response)

    @query_params("label", "elements")
    def add(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Create a new list with the given label and elements.
        :param label: string of the label of the list
        :param elements: list of string ids for the elements of the list
        :return: an OrkgResponse object containing the list
        """
        if len(params) != 2:
            raise ValueError("a label and a list of elements must be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.lists.POST(json=params, headers=self.auth)
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("label", "elements")
    def update(self, list_id: str, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Replace the current label and/or elements of an existing list with new values.
        Does not return the modified list in the body of the response.
        :param list_id: the id of the list to lookup
        :param label: string of the new label of the list (optional)
        :param elements: list of string ids for the new elements of the list (optional)
        :return: an OrkgResponse object indicating success or failure
        """
        if len(params) == 0:
            raise ValueError("either a label or a list of elements must be provided")
        is_list = "List" in self.client.resources.by_id(list_id).content["classes"]
        if not is_list:
            raise ValueError("the ID provided does not correspond to a list!")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.lists(list_id).PATCH(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)
