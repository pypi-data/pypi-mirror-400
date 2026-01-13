import json
import os
from typing import Any, List, Optional, Union

from orkg.client.harvesters.utils import process_contribution
from orkg.common import OID
from orkg.out import OrkgResponse


def harvest(
    orkg_client: Any,
    directory: str,
    research_field: Union[str, OID],
    title: str,
    doi: Optional[str] = None,
    authors: Optional[List[str]] = None,
    publication_year: Optional[int] = None,
    publication_month: Optional[int] = None,
    published_in: Optional[str] = None,
    url: Optional[str] = None,
    extraction_method: Optional[str] = None,
    slow_mode: Optional[bool] = False,
    **kwargs,
) -> OrkgResponse:
    # Check if the directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist.")

    # Check if the directory contains any json files
    if not any(file.endswith(".json") for file in os.listdir(directory)):
        raise ValueError(f"The directory {directory} does not contain any json files.")

    # Check if research field is valid
    if isinstance(research_field, str):
        rf_response = orkg_client.resources.get(q=research_field, exact=True, size=1)
        if not rf_response.succeeded or len(rf_response.content) == 0:
            raise ValueError(
                f"Unable to find the ORKG research field with the given string value {research_field}"
            )
        research_field = OID(rf_response.content[0]["id"])

    # Prepare the paper object
    paper_json = {"title": title, "researchField": f"{research_field.id}"}
    if doi is not None:
        paper_json["doi"] = doi
    if authors is not None:
        paper_json["authors"] = [
            {"label": author} if isinstance(author, str) else {"id": str(author)}
            for author in authors
        ]
    if publication_year is not None:
        paper_json["publicationYear"] = str(publication_year)
    if publication_month is not None:
        paper_json["publicationMonth"] = str(publication_month)
    if published_in is not None:
        paper_json["publishedIn"] = published_in
    if url is not None:
        paper_json["url"] = url
    if extraction_method is not None:
        paper_json["extractionMethod"] = extraction_method
    if "contributions" not in paper_json:
        paper_json["contributions"] = []
    for key, value in kwargs.items():
        paper_json[key] = value

    # Read all json files in the directory
    contribution_content = []
    for file in os.listdir(directory):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(directory, file)) as f:
            contribution_content.append(json.load(f))

    # Process the contribution content
    for contribution_json in contribution_content:
        orkg_contribution_json = {}
        global_ids = {}
        context = contribution_json.get("@context", {})
        process_contribution(
            contribution_json, orkg_contribution_json, global_ids, context
        )
        # replace the key "label" with "name"
        orkg_contribution_json["name"] = orkg_contribution_json.pop("label")
        paper_json["contributions"].append(orkg_contribution_json)

    # Remove @temp from all the contribution objects (NamedObject doesn't have a @temp field anymore)
    for contribution in paper_json["contributions"]:
        if "@temp" in contribution:
            del contribution["@temp"]

    # Now that we have everything, let's finalize the paper object and add it to the graph
    paper_json = {"paper": paper_json}
    if not slow_mode:
        return orkg_client.papers.add(paper_json)
    else:
        contributions = paper_json["paper"]["contributions"]
        paper_json["paper"]["contributions"] = [contributions[0]]
        paper_response = orkg_client.papers.add(paper_json)
        for contribution in contributions[1:]:
            contribution_response = orkg_client.objects.add({"resource": contribution})
            orkg_client.statements.add(
                subject_id=paper_response.content["id"],
                predicate_id="P31",
                object_id=contribution_response.content["id"],
            )
        return paper_response
