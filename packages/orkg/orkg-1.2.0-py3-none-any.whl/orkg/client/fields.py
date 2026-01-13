from typing import Dict, Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ResearchFieldsClient(NamespacedClient):
    @query_params("page", "size", "sort", "desc")
    def with_benchmarks(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Get all the research fields with benchmarks
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend("research-fields").benchmarks.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend("research-fields").benchmarks.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_subfields(
        self, field_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        """
        Get the subfield(s) immediately below the given research field
        :param field_id: id of the research field
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend("research-fields")(field_id).children.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend("research-fields")(field_id).children.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_superfields(
        self, field_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        """
        Get the superfield(s) immediately above the given research field
        :param field_id: id of the research field
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend("research-fields")(field_id).parents.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend("research-fields")(field_id).parents.GET()
        return self.client.wrap_response(response)

    def get_root(self, field_id: str) -> OrkgResponse:
        """
        Get the root research field of the given subfield
        :param field_id: id of the subfield
        :return: OrkgResponse object
        """
        self.client.backend._append_slash = True
        response = self.client.backend("research-fields")(field_id).roots.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_all_roots(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Get a list of all root research fields
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend("research-fields").roots.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend("research-fields").roots.GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_hierarchy(
        self, field_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        """
        Get a list of all research fields in the hierarchy above and including the given subfield
        :param field_id: id of the subfield
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend("research-fields")(field_id).hierarchy.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend("research-fields")(field_id).hierarchy.GET()
        return self.client.wrap_response(response)

    @query_params("include_subfields")
    def get_stats(self, field_id: str, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Get the number of papers within the given research field, optionally including all subfields
        :param field_id: id of the subfield
        :param include_subfields: True/False whether to include subfields in stats, default is False (optional)
        :return: OrkgResponse object
        """
        params_to_send = {
            "research_field": field_id,
            "include_subfields": params.get("include_subfields", False),
        }
        self.client.backend._append_slash = False
        response = self.client.backend.statistics("content-types")("paper-count").GET(
            dict_to_url_params(params_to_send)
        )
        return self.client.wrap_response(response)
