import re
from ast import literal_eval
from typing import Dict, List, Optional, Tuple, Union

from requests import Response

from orkg.out import OrkgResponse, OrkgUnpaginatedResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class PapersClient(NamespacedClient):
    def by_id(self, id: str) -> OrkgResponse:
        """
        Lookup a paper by id
        :param id: the id of the paper to lookup
        :return: an OrkgResponse object containing the paper
        """
        self.client.backend._append_slash = True
        response = self.client.backend.papers(id).GET()
        return self.client.wrap_response(response)

    @query_params(
        "title",
        "exact",
        "doi",
        "visibility",
        "verified",
        "created_by",
        "created_at_start",
        "created_at_end",
        "observatory_id",
        "organization_id",
        "research_field",
        "include_subfields",
        "page",
        "size",
        "sort",
        "desc",
    )
    def get(self, params: Optional[Dict] = None) -> OrkgResponse:
        """
        Fetch a list of papers, with multiple options for searching and filtering results
        :param title: search term that must be contained in the title of the paper (optional)
        :param exact: whether title matching is exact or fuzzy (optional, default: false)
        :param doi: filter for the DOI of the paper (optional)
        :param visibility: possible values are "ALL_LISTED", "UNLISTED", "FEATURED", "NON_FEATURED", "DELETED" (optional)
        :param verified: filter for the verified flag of the paper (optional)
        :param created_by: filter for the UUID of the user or service who created this paper (optional)
        :param created_at_start: the oldest timestamp a returned paper can have (optional)
        :param created_at_end: the most recent timestamp a returned paper can have (optional)
        :param observatory_id: filter for the UUID of the observatory that the paper belongs to (optional)
        :param organization_id: filter for the UUID of the organization that the resource belongs to (optional)
        :param research_field: filter for research field id (optional)
        :param include_subfields: whether subfields are included or not (optional, default: false)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: an OrkgResponse object containing a list of papers
        """
        if len(params) > 0:
            self.handle_sort_params(params)
            self.client.backend._append_slash = False
            response = self.client.backend.papers.GET(
                params=params,
                headers={
                    "Content-Type": "application/vnd.orkg.paper.v2+json;charset=UTF-8",
                    "Accept": "application/vnd.orkg.paper.v2+json",
                },
            )
        else:
            self.client.backend._append_slash = False
            response = self.client.backend.papers.GET()
        return self.client.wrap_response(response)

    @query_params(
        "title",
        "exact",
        "doi",
        "visibility",
        "verified",
        "created_by",
        "created_at_start",
        "created_at_end",
        "observatory_id",
        "organization_id",
        "research_field",
        "include_subfields",
        "page",
        "size",
        "sort",
        "desc",
    )
    def get_unpaginated(
        self, start_page: int = 0, end_page: int = -1, params: Optional[Dict] = None
    ) -> OrkgUnpaginatedResponse:
        """
        Fetch a list of papers between start and end page, with multiple options for searching and filtering results
        :param start_page: page to start from. Defaults to 0 (optional)
        :param end_page: page to stop at. Defaults to -1 meaning non-stop (optional)
        :param title: search term that must be contained in the title of the paper (optional)
        :param exact: whether title matching is exact or fuzzy (optional, default: false)
        :param doi: filter for the DOI of the paper (optional)
        :param visibility: possible values are "ALL_LISTED", "UNLISTED", "FEATURED", "NON_FEATURED", "DELETED" (optional)
        :param verified: filter for the verified flag of the paper (optional)
        :param created_by: filter for the UUID of the user or service who created this paper (optional)
        :param created_at_start: the oldest timestamp a returned paper can have (optional)
        :param created_at_end: the most recent timestamp a returned paper can have (optional)
        :param observatory_id: filter for the UUID of the observatory that the paper belongs to (optional)
        :param organization_id: filter for the UUID of the organization that the resource belongs to (optional)
        :param research_field: filter for research field id (optional)
        :param include_subfields: whether subfields are included or not (optional, default: false)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: an OrkgUnpaginatedResponse object containing a list of papers
        """
        return self._call_pageable(
            self.get, args={}, params=params, start_page=start_page, end_page=end_page
        )

    def update(
        self,
        paper_id: str,
        title: Optional[str] = None,
        research_fields: Optional[List] = None,
        identifiers: Optional[Dict] = None,
        publication_info: Optional[Dict] = None,
        authors: Optional[List[Dict]] = None,
        organizations: Optional[List] = None,
        observatories: Optional[List] = None,
        sdgs: Optional[set] = None,
    ) -> OrkgResponse:
        """
        Edit the metadata of an already created paper. The passed values will replace the existing values.
        :param paper_id: the resource ID of the paper
        :param title: the updated title (optional)
        :param research_fields: the updated research fields of the paper (optional)
        :param identifiers: the updated unique identifiers of the paper (optional)
        :param publication_info: the updated publication info of the paper (optional)
        :param authors: the updated list of authors' info of the paper (optional)
        :param organizations: the updated list of IDs of the organizations the paper belongs to (optional)
        :param observatories: the updated list of IDs of the observatories the paper belongs to (optional)
        :param sdgs: the updated set of IDs of UN sustainable development goals the paper will be assigned to (optional)
        :return: OrkgResponse indicating success or failure of the request (no content)
        """
        paper = {
            "title": title,
            "research_fields": research_fields,
            "identifiers": identifiers,
            "publication_info": publication_info,
            "authors": authors,
            "organizations": organizations,
            "observatories": observatories,
            "sdgs": sdgs,
        }
        if all(value is None for value in paper.values()):
            raise ValueError("at least one field to update should be passed!")
        headers = {
            **(self.auth if self.auth is not None else {}),
            "Content-Type": "application/vnd.orkg.paper.v2+json;charset=UTF-8",
            "Accept": "application/vnd.orkg.paper.v2+json",
        }
        self.client.backend._append_slash = False
        response = self.client.backend.papers(paper_id).PUT(json=paper, headers=headers)
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def publish(
        self, paper_id: str, subject: str, description: str, authors: List[Dict]
    ) -> OrkgResponse:
        """
        Publish an existing paper by assigning a DOI and adding publication info.
        :param paper_id: the resource ID of the paper
        :param subject: the subject of the paper
        :param description: the description of the paper
        :param authors: the list of authors' info
        :return: OrkgResponse indicating success or failure of the request (no content)
        """
        paper = {"subject": subject, "description": description, "authors": authors}
        headers = {
            **(self.auth if self.auth is not None else {}),
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
        }
        self.client.backend._append_slash = False
        response = self.client.backend.papers(paper_id).publish.POST(
            json=paper, headers=headers
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def add(
        self, params: Optional[Dict] = None, merge_if_exists: bool = False
    ) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance. Automatically detects whether the provided data structure is compatible
        with the legacy or the new endpoint and calls the corresponding method.
        :param params: dict containing the metadata and content of the paper
        :param merge_if_exists: merge the papers if they exist in the graph and append contributions (optional)
        :return: an OrkgResponse containing either the new paper resource (v1) or the url to the new paper object (v2)
        """
        if "paper" in params.keys():
            required_params = ["title", "researchField"]
            missing_params = [
                p for p in required_params if p not in params["paper"].keys()
            ]
            if missing_params:
                raise TypeError(
                    f"Params is missing the following required key(s): {missing_params}"
                )
            return self.add_v1(params, merge_if_exists)
        else:
            required_params = [
                "authors",
                "contents",
                "extraction_method",
                "identifiers",
                "observatories",
                "organizations",
                "publication_info",
                "research_fields",
                "title",
            ]
            missing_params = [p for p in required_params if p not in params.keys()]
            if missing_params:
                raise TypeError(
                    f"Params is missing the following required key(s): {missing_params}"
                )
            return self.add_v2(**params)

    def add_v1(self, params: Dict, merge_if_exists: bool = False) -> OrkgResponse:
        """
        Create a new paper or add contributions to an existing paper in the ORKG instance using the legacy papers endpoint.
        :param params: paper Object
        :param merge_if_exists: merge the papers if they exist in the graph and append contributions
        :return: an OrkgResponse object containing the newly created paper resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.papers.POST(
            json=params, params={"mergeIfExists": merge_if_exists}, headers=self.auth
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    # TODO: remove self.auth check after implementing package-wide solution, see: https://gitlab.com/TIBHannover/orkg/orkg-pypi/-/issues/76
    def add_v2(
        self,
        title: str,
        research_fields: List,
        identifiers: Dict,
        publication_info: Dict,
        authors: List[Dict],
        contents: Dict,
        organizations: List,
        observatories: List,
        extraction_method: str,
        sdgs: Optional[set] = None,
        **kwargs,
    ) -> OrkgResponse:
        """
        Create a new paper in the ORKG instance using the new papers endpoint.
        :param title: the title of the paper
        :param research_fields: the list of research field IDs the paper will be assigned to
        :param identifiers: the unique identifiers of the paper (e.g. doi)
        :param publication_info: the publication info of the paper (e.g. year, url)
        :param authors: the authors of the paper
        :param contents: the contributions of the paper and resources, literals, predicates, and lists to be created
        :param organizations: the list of IDs of the organizations the paper belongs to
        :param observatories: the list of IDs of the observatories the paper belongs to
        :param extraction_method: the method used to extract the paper resource ("UNKNOWN", "MANUAL" or "AUTOMATIC")
        :param sdgs: the set of IDs of UN sustainable development goals the paper will be assigned to (optional)
        :return: an OrkgResponse containing the status code and url of the new paper object (no content)
        """
        assert len(kwargs) == 0, f"Unknown arguments: {list(kwargs.keys())}"
        paper = {
            "title": title,
            "research_fields": research_fields,
            "identifiers": identifiers,
            "publication_info": publication_info,
            "authors": authors,
            "contents": contents,
            "organizations": organizations,
            "observatories": observatories,
            "extraction_method": extraction_method,
            "sdgs": sdgs,
        }
        headers = {
            **(self.auth if self.auth is not None else {}),
            "Content-Type": "application/vnd.orkg.paper.v2+json;charset=UTF-8",
            "Accept": "application/vnd.orkg.paper.v2+json",
        }
        self.client.backend._append_slash = False
        response: Response = self.client.backend.papers.POST(
            json=paper, headers=headers
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def by_doi(self, doi: str) -> OrkgResponse:
        """
        Get the paper resource in the ORKG associated with the given DOI.
        :param doi: The DOI of the paper, could be a full url or just the DOI
        :return: A list of paper objects
        """
        # Disable appending a slash to the base URL
        self.client.backend._append_slash = False

        # Extract the DOI from the input if it's a full URL
        if "doi.org" in doi:
            doi = doi.split("doi.org/")[-1]

        # Send an HTTP GET request to fetch paper information
        response = self.client.backend.papers.GET(
            headers={"Accept": "application/vnd.orkg.paper.v2+json"},
            params={"doi": doi},
        )

        return self.client.wrap_response(response)

    def by_title(self, title: str) -> OrkgResponse:
        """
        Retrieve a paper object based on its title.
        :param title: The title of the research paper.
        :return: A list of paper objects
        """
        # Disable appending a slash to the base URL
        self.client.backend._append_slash = False

        # Send an HTTP GET request to fetch paper information
        response = self.client.backend.papers.GET(
            headers={"Accept": "application/vnd.orkg.paper.v2+json"},
            params={"title": title},
        )

        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def in_research_field(
        self,
        research_field_id: str,
        include_subfields: Optional[bool] = False,
        params: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Get all papers in a research field
        :param research_field_id: the id of the research field
        :param include_subfields: True/False whether to include papers from subfields, default is False (optional)
        :param page: the page number (optional)
        :param size: number of items per page (optional)
        :param sort: key to sort on (optional)
        :param desc: true/false to sort desc (optional)
        :return: OrkgResponse object
        """
        url = self.client.backend("research-fields")(research_field_id)
        if include_subfields:
            url = url.subfields.papers
        else:
            url = url.papers
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = url.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = url.GET()
        return self.client.wrap_response(response)

    @staticmethod
    def _get_paper_statements_and_metadata(
        paper: Dict, params: Dict
    ) -> Tuple[Dict, Dict, Dict]:
        """
        Format paper statement values and add default values for missing data.
        Separate into dictionaries for statements and metadata.

        :param paper: dict of all info extracted from csv file
        :param params: string representation of dict (e.g. "{'name': 1}") dict with default statements, should contain CSV_PLACEHOLDER (optional)
        :return:
            - dict of paper statements (without metadata)
            - dict of paper metadata
            - dict of standard statements or empty dict if no standard statements
        """
        title = paper["paper:title"]
        authors = (
            [
                {"label": author.strip()}
                for author in str(paper["paper:authors"]).split(";")
            ]
            if "paper:authors" in paper
            and paper["paper:authors"] == paper["paper:authors"]
            else []
        )
        publication_month = paper.get("paper:publication_month", 1)
        publication_year = paper.get("paper:publication_year", 2000)
        research_field = paper.get("paper:research_field", "R11")  # "Science"
        doi = paper.get("paper:doi", "")
        url = ""
        published_in = ""
        paper_metadata = {
            "title": title,
            "authors": authors,
            "publicationMonth": publication_month,
            "publicationYear": publication_year,
            "researchField": research_field,
            "doi": doi,
            "url": url,
            "publishedIn": published_in,
        }
        standard_statements = (
            literal_eval(params["standard_statements"])
            if "standard_statements" in params
            else {}
        )
        # remove metadata from paper dict, already added above
        metadata_headers = [
            "paper:title",
            "paper:authors",
            "paper:publication_month",
            "paper:publication_year",
            "paper:doi",
            "paper:research_field",
        ]
        [paper.pop(key) if key in paper else paper for key in metadata_headers]
        return paper, paper_metadata, standard_statements

    def _add_new_paper(self, contribution_ids: List, paper: Dict) -> List:
        """
        Add new paper to ORKG instance and add contribution ID to list.

        :param contribution_ids: list of contribution ID strings
        :param paper: dict of paper statements and metadata
        :return: updated list of contribution ID strings
        """
        response = self.add(paper)
        if "id" in response.content:
            paper_id = response.content["id"]
            paper_statements = self.client.statements.get_by_subject(
                subject_id=paper_id, size=10000
            ).content
            for statement in paper_statements:
                if statement["predicate"]["id"] == "P31":
                    contribution_ids.append(statement["object"]["id"])
                    print("Added paper:", str(paper_id))
        else:
            print("Error adding paper: ", str(response.content))
        return contribution_ids

    def _add_new_contribution(
        self,
        contribution_ids: List,
        contribution_statements: Dict[str, List],
        existing_paper_id: str,
    ) -> List:
        """
        Add contribution to existing paper in ORKG instance and add contribution ID to list.

        :param contribution_ids: list of contribution ID strings
        :param contribution_statements: dict of predicate IDs and their objects
        :param existing_paper_id: paper ID string
        :return: updated list of contribution ID strings
        """
        paper_statements = self.client.statements.get_by_subject(
            subject_id=existing_paper_id, size=10000
        ).content
        contribution_amount = 0
        for paper_statement in paper_statements:
            if paper_statement["predicate"]["id"] == "P31":  # "Contribution"
                contribution_amount += 1
        contribution_id = self.client.resources.add(
            label="Contribution " + str(contribution_amount + 1),
            classes=["Contribution"],
        ).content["id"]
        self.client.statements.add(
            subject_id=existing_paper_id,
            predicate_id="P31",
            object_id=contribution_id,
        )
        self._create_statements(contribution_id, contribution_statements)
        contribution_ids.append(contribution_id)
        print(
            "Added contribution:",
            str(contribution_id),
            "to paper:",
            str(existing_paper_id),
        )
        return contribution_ids

    def _insert_research_problem(
        self, contribution_statements: Dict[str, List], research_problems: List[str]
    ) -> Dict[str, List]:
        """
        Add research problem(s) by resource ID to contribution statements dictionary.

        :param contribution_statements: dict of predicate IDs and their objects
        :param research_problems: list of (one or many) research problem(s) as strings
        :return: updated dict of contribution statements
        """
        contribution_statements["P32"] = []
        for research_problem in research_problems:
            research_problem_id = self.client.resources.find_or_add(
                label=research_problem, classes=["Problem"]
            ).content["id"]
            # P32 has research problem
            contribution_statements["P32"].append({"@id": research_problem_id})
        return contribution_statements

    def _insert_standard_statements(
        self, contribution_statements: Dict[str, List], statements_to_insert: Dict
    ) -> Dict[str, Union[str, List]]:
        """
        Create new standard statements dict with predicate IDs as keys and predicate labels as values.

        :param contribution_statements: dict of predicate IDs and their objects
        :param statements_to_insert: dict with default statements, should contain CSV_PLACEHOLDER
        :return: dict of standard statements' predicate IDs to predicate labels
        """
        for predicate in statements_to_insert:
            if isinstance(statements_to_insert[predicate], list):  # if is array
                for i in range(len(statements_to_insert[predicate])):
                    if (
                        statements_to_insert[predicate][i]["values"]
                        == "CSV_PLACEHOLDER"
                    ):
                        statements_to_insert[predicate][i][
                            "values"
                        ] = contribution_statements
            if not re.search("^P+[a-zA-Z0-9]*$", predicate):
                predicate_id = self.client.predicates.find_or_add(
                    label=predicate
                ).content["id"]
                statements_to_insert[predicate_id] = statements_to_insert[predicate]
                del statements_to_insert[predicate]
        return statements_to_insert

    def _extract_statements(self, paper: Dict) -> Tuple[List[str], Dict]:
        """
        Create a dictionary of predicate-object pairs formatted/typed for the ORKG.
        Predicates: find an existing ID matching the label, or create a new one.
        Objects: if resource, find an existing ID matching the label, or create a new one. Otherwise, add as literal.
        Also creates a list of research problem label(s).

        :param paper: dict of paper statements as extracted from CSV
        :return:
            - list of research problem label(s)
            - dict of predicate IDs and their objects
        """
        contribution_statements = {}
        research_problems = []
        for predicate in paper:
            value = paper[predicate]
            # add research problem (one or more)
            if predicate.startswith("contribution:research_problem"):
                research_problem = paper.get("predicate", "")
                if research_problem != "":
                    research_problems.append(research_problem)
                continue
            # filter out nan values
            if value != value:
                continue
            # to make columns unique, pandas appends a dot and number to duplicate columns, remove this here
            predicate = re.sub(r"\.[1-9]+$", "", predicate)
            value_is_resource = False
            # if predicate starts with resource:, insert it as resource instead of literal
            if predicate.startswith("resource:"):
                value_is_resource = True
                predicate = predicate[len("resource:") :]
            predicate_id = self.client.predicates.find_or_add(label=predicate).content[
                "id"
            ]
            if not value_is_resource:
                if predicate_id in contribution_statements:
                    contribution_statements[predicate_id].append({"text": value})
                else:
                    contribution_statements[predicate_id] = [{"text": value}]
            else:
                resource_id = self.client.resources.find_or_add(label=value).content[
                    "id"
                ]
                if predicate_id in contribution_statements:
                    contribution_statements[predicate_id].append({"@id": resource_id})
                else:
                    contribution_statements[predicate_id] = [{"@id": resource_id}]
        return research_problems, contribution_statements

    def _create_statements(self, subject_id: str, statements: Dict):
        """
        Add statements to ORKG instance.

        :param subject_id: string of subject resource ID
        :param statements: dict of predicate IDs and their objects
        """
        for predicate_id in statements:
            values = statements[predicate_id]
            for value in values:
                if "text" in value:
                    literal_id = self.client.literals.add(label=value["text"]).content[
                        "id"
                    ]
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=literal_id,
                    )
                elif "@id" in value:
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=value["@id"],
                    )
                elif "label" in value:
                    resource_id = self.client.resources.add(
                        label=value["label"]
                    ).content["id"]
                    self.client.statements.add(
                        subject_id=subject_id,
                        predicate_id=predicate_id,
                        object_id=resource_id,
                    )
                    self._create_statements(resource_id, value["values"])
