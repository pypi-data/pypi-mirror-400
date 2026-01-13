from typing import Dict, List, Optional

from orkg.out import OrkgResponse, OrkgUnpaginatedResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ContributionComparisonsClient(NamespacedClient):
    @query_params("page", "size", "sort", "desc")
    def by_ids(self, ids: List[str], params: Optional[Dict] = None) -> OrkgResponse:
        """
        Get contributions details given by their IDs.

        :param ids: the IDs of the contributions.
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: an OrkgResponse object containing the resource
        """

        self.client.backend._append_slash = False
        params["ids"] = ",".join(ids)
        response = self.client.backend("contribution-comparisons").contributions.GET(
            dict_to_url_params(params)
        )
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def by_ids_unpaginated(
        self,
        ids: List[str],
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        """
        Get all contributions details by all pages between start_page and end_page given by their IDs.

        :param ids: the IDs of the contributions.
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :param start_page: which page in the api results to start from, default is 0 (optional)
        :param end_page: which page in the api results to end on, default is -1 (final page) (optional)
        :return: an OrkgUnpaginatedResponse object
        """
        return self._call_pageable(
            self.by_ids,
            args={"ids": ids},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )
