from typing import Any, Dict, List, Literal, Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class ComparisonsClient(NamespacedClient):
    def create(
        self,
        title: str,
        description: str,
        contributions: List[str],
        research_fields: List[str],
        config: Dict[str, Any],
        data: Dict[str, Any],
        sdgs: Optional[List[str]] = None,
        visualizations: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
        organizations: Optional[List[str]] = None,
        observatories: Optional[List[str]] = None,
        is_anonymized: bool = False,
        extraction_method: Literal["UNKNOWN", "MANUAL", "AUTOMATIC"] = "UNKNOWN",
        authors: Optional[List[Dict[str, Any]]] = None,
    ) -> OrkgResponse:
        """
        Create a new comparison with the given parameters.

        :param title: The title of the comparison
        :param description: The description of the comparison
        :param contributions: The ids of the contributions the comparison compares
        :param research_fields: The list of research fields the comparison will be assigned to
        :param config: The configuration of the comparison (contains: predicates, contributions, transpose, type)
        :param data: The data contained in the comparison
        :param sdgs: The set of ids of sustainable development goals (optional)
        :param visualizations: The list of IDs of visualizations assigned to the comparison (optional)
        :param references: The references to external sources that the comparison refers to (optional)
        :param organizations: The list of IDs of the organizations (optional)
        :param observatories: The list of IDs of the observatories (optional)
        :param is_anonymized: Whether the comparison should be displayed as anonymous (default: False)
        :param extraction_method: The method used to extract the comparison resource (default: UNKNOWN)
        :param authors: The list of authors that contributed to the comparison (optional)
        :return: The response of the request
        """
        payload = {
            "title": title,
            "description": description,
            "contributions": contributions,
            "research_fields": research_fields,
            "config": config,
            "data": data,
            "is_anonymized": is_anonymized,
            "extraction_method": extraction_method,
            "sdgs": sdgs if sdgs else [],
            "visualizations": visualizations if visualizations else [],
            "references": references if references else [],
            "organizations": organizations if organizations else [],
            "observatories": observatories if observatories else [],
            "authors": authors if authors else [],
        }

        self.client.backend._append_slash = False
        headers = {
            "Content-Type": "application/vnd.orkg.comparison.v2+json;charset=UTF-8",
            "Accept": "application/vnd.orkg.comparison.v2+json",
        }
        headers.update(self.auth)
        response = self.client.backend.comparisons.POST(json=payload, headers=headers)
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def publish(
        self,
        comparison_id: str,
        subject: str,
        description: str,
        authors: List[Dict[str, Any]],
        assign_doi: bool = False,
    ) -> OrkgResponse:
        """
        Publish an existing comparison with the given parameters.

        :param comparison_id: The ID of the comparison to publish
        :param subject: The subject of the comparison
        :param description: The description of the comparison
        :param authors: The list of authors that contributed to the comparison
        :param assign_doi: Whether to assign a new DOI for the comparison (default: False)
        :return: The response of the request
        """
        payload = {
            "subject": subject,
            "description": description,
            "authors": authors,
            "assign_doi": assign_doi,
        }

        self.client.backend._append_slash = False
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers.update(self.auth)
        response = self.client.backend.comparisons(comparison_id).publish.POST(
            json=payload, headers=headers
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def in_research_field(
        self,
        research_field_id: str,
        include_subfields: Optional[bool] = False,
        params: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Get all comparisons in a research field
        :param research_field_id: the id of the research field
        :param include_subfields: True/False whether to include comparisons from subfields, default is False (optional)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        url = self.client.backend("research-fields")(research_field_id)
        if include_subfields:
            url = url.subfields.comparisons
        else:
            url = url.comparisons
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = url.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = url.GET()
        return self.client.wrap_response(response)
