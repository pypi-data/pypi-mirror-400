from typing import Dict, Optional

from orkg.out import OrkgResponse, OrkgUnpaginatedResponse
from orkg.utils import NamespacedClient, admin_functionality, query_params


class ResourcesClient(NamespacedClient):
    def by_id(self, id: str) -> OrkgResponse:
        """
        Lookup a resource by id
        :param id: the id of the resource to lookup
        :return: an OrkgResponse object containing the resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.resources(id).GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc", "exclude", "include")
    def get(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Fetch a list of resources, with the possibility to paginate the results and filter them out based on label
        :param q: search term of the label of the resource (optional)
        :param exact: whether to check for the exact search term or not (optional) -> bool
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :param exclude: classes to be excluded in search (optional)
        :param include: classes to filter the resources by (optional)
        :return: an OrkgResponse object contains the list of resources
        """
        self.handle_sort_params(params)
        response = self.client.backend.resources.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("q", "exact", "page", "size", "sort", "desc", "exclude", "include")
    def get_unpaginated(
        self, start_page: int = 0, end_page: int = -1, params: Optional[Dict] = None
    ) -> OrkgUnpaginatedResponse:
        """
        Fetch all resources returned by all pages between start_page and end_page.

        :param q: search term of the label of the resource (optional)
        :param exact: whether to check for the exact search term or not (optional) -> bool
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :param exclude: classes to be excluded in search (optional)
        :param include: classes to filter the resources by (optional)

        :param start_page: page to start from. Defaults to 0 (optional)
        :param end_page: page to stop at. Defaults to -1 meaning non-stop (optional)
        :return: an OrkgUnpaginatedResponse object
        """
        return self._call_pageable(
            self.get, args={}, params=params, start_page=start_page, end_page=end_page
        )

    @query_params("id", "label", "classes", "extraction_method")
    def add(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Create a new resource in the ORKG instance
        :param id: the specific id to add (optional)
        :param label: the label of the new resource (optional)
        :param classes: list of classes to assign the resource to (optional)
        :param extraction_method: the extraction method of the resource (optional) one of [MANUAL, AUTOMATIC, UNKNOWN]
        :return: an OrkgResponse object containing the newly created resource
        """
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.resources.POST(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("id", "label", "classes", "extraction_method")
    def find_or_add(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        find or create a new resource in the ORKG instance
        :param id: the specific id to add (optional)
        :param label: the label of the new resource (optional)
        :param classes: list of classes to assign the resource to (optional)
        :param extraction_method: the extraction method of the resource (optional) one of [MANUAL, AUTOMATIC, UNKNOWN]
        :return: an OrkgResponse object containing the found or newly created resource
        """
        if len(params) == 0:
            raise ValueError("at least a label should be provided")
        else:
            if "id" in params:
                # check if a resource with this id is there
                found = self.by_id(params["id"])
                if found.succeeded:
                    return found
            if "label" in params and "classes" in params:
                class_id = params["classes"][0]
                # check if a resource exists with this label and the _first_ class from params class list
                found = self.client.classes.get_resource_by_class(
                    class_id, q=params["label"], exact=True, size=1
                )
                if found.succeeded:
                    if isinstance(found.content, list) and len(found.content) > 0:
                        found.content = found.content[0]
                        return found
            # if no class is passed, check if a resource with this label is there
            elif "label" in params:
                found = self.get(q=params["label"], exact=True, size=1)
                if found.succeeded:
                    if isinstance(found.content, list) and len(found.content) > 0:
                        found.content = found.content[0]
                        return found
            # None found, what the hell! let's create a new one
            self.client.backend._append_slash = True
            response = self.client.backend.resources.POST(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("label", "classes", "extraction_method")
    def update(self, id: str, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Update a resource with a specific id
        :param id: the id of the resource to update
        :param label: the new label (optional)
        :param classes: the updated list of classes (optional)
        :param extraction_method: the extraction method of the resource (optional) one of [MANUAL, AUTOMATIC, UNKNOWN]
        :return: an OrkgResponse object contains the newly updated resource
        """
        if len(params) == 0:
            raise ValueError("at least label should be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.resources(id).PUT(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @admin_functionality
    def update_observatory(
        self, id: str, observatory_id: str, organization_id: str
    ) -> OrkgResponse:
        """
        Update the observatory and the organization of a particular resource
        NOTE: this is a call only for admins
        :param id: The id of the resource to update
        :param observatory_id: the new observatory id
        :param organization_id: the new organization id
        :return: an OrkgResponse object contains the newly updated resource
        """
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = False
        content = {"observatory_id": observatory_id, "organization_id": organization_id}
        response = self.client.backend.resources(id).PUT(
            json=content, headers=self.auth
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def exists(self, id: str) -> bool:
        """
        Check if a resource exists in the graph
        :param id: the id of the resource to check
        :return: true if found, otherwise false
        """
        return self.by_id(id).succeeded

    @admin_functionality
    def delete(self, id: str) -> OrkgResponse:
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = True
        response = self.client.backend.resources(id).DELETE(headers=self.auth)
        return self.client.wrap_response(response)
