from typing import Dict, Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ResearchProblemsClient(NamespacedClient):
    @query_params("page", "size", "sort", "desc")
    def in_research_field(
        self,
        research_field_id: str,
        include_subfields: Optional[bool] = False,
        params: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Get all problems in a research field
        :param research_field_id: the id of the research field
        :param include_subfields: True/False whether to include problems from subfields, default is False (optional)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        url = self.client.backend("research-fields")(research_field_id)
        if include_subfields:
            url = url.subfields("research-problems")
        else:
            url = url.problems
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = url.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = url.GET()
        return self.client.wrap_response(response)
