import json
import os
import re
from typing import Any, Dict, List, Optional, Union

import requests

from orkg.client.harvesters.utils import process_contribution
from orkg.common import OID
from orkg.out import OrkgResponse


def _validate_doi(doi: str) -> bool:
    """Check if a string is a valid DOI or a complete DOI URL."""
    if doi is None:
        return False

    # DOI pattern.
    doi_pattern = re.compile(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)

    # DOI URL pattern.
    url_pattern = re.compile(r"^https?://doi\.org/10.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)

    return bool(doi_pattern.match(doi) or url_pattern.match(doi))


def harvest(
    orkg_client: Any,
    doi: Optional[str],
    orkg_rf: Union[str, OID],
    directory: Optional[str],
    slow_mode: Optional[bool] = False,
) -> OrkgResponse:
    if doi is None and directory is None:
        raise ValueError("Either doi or directory must be provided.")

    contributions_urls = []
    doi_content = None

    # Check if directory is provided and all is valid
    if directory is not None:
        if not os.path.isdir(directory):
            raise ValueError(f"The directory {directory} does not exist.")
        if doi is None and not os.path.isfile(os.path.join(directory, "doi.json")):
            raise ValueError(
                f"The directory {directory} does not contain the file doi.json."
            )
        if os.path.isfile(os.path.join(directory, "doi.json")):
            with open(os.path.join(directory, "doi.json")) as f:
                doi_content = json.load(f)
    if doi_content is None:
        doi_content, contributions_urls = _get_doi_response(doi)

    if isinstance(orkg_rf, str):
        rf_response = orkg_client.resources.get(q=orkg_rf, exact=True, size=1)
        if not rf_response.succeeded or len(rf_response.content) == 0:
            raise ValueError(
                f"Unable to find the ORKG research field with the given string value {orkg_rf}"
            )
        orkg_rf = OID(rf_response.content[0]["id"])

    paper_json = {
        # TODO: handle multiple titles
        "title": doi_content["title"][0]
        if isinstance(doi_content["title"], list)
        else doi_content.get("title", "No title"),
        "doi": doi_content.get("DOI", None),
        "authors": [
            {"label": f'{author["given"]} {author["family"]}'}
            for author in doi_content["author"]
        ],
        "publicationYear": int(doi_content["published"]["date-parts"][0][0])
        if "date-parts" in doi_content["published"]
        and len(doi_content["published"]["date-parts"][0]) > 1
        else None,
        "publicationMonth": int(doi_content["published"]["date-parts"][0][1])
        if "date-parts" in doi_content["published"]
        and len(doi_content["published"]["date-parts"][0]) > 2
        else None,
        "publishedIn": doi_content.get("publisher", None),
        "researchField": f"{orkg_rf}",
    }

    if "contributions" not in paper_json:
        paper_json["contributions"] = []

    # Get the contribution content and override if directory is provided
    contribution_content = [requests.get(url).json() for url in contributions_urls]
    contribution_content = _filter_to_orkg_harvestable_content(contribution_content)

    if directory is not None:
        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f != "doi.json"
        ]
        contribution_content: List[Dict] = []
        for file in files:
            with open(os.path.join(directory, file)) as f:
                contribution_content.append(json.load(f))

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


def _filter_to_orkg_harvestable_content(contribution_content: List[Dict]) -> List[Dict]:
    new_contribution_content = []
    for contribution in contribution_content:
        if (
            "@id" in contribution
            and "label" in contribution
            and "@type" in contribution
            and any("orkg.org/class" in t for t in contribution["@type"])
        ):
            new_contribution_content.append(contribution)
    return new_contribution_content


def _get_doi_response(doi: str):
    # Check if the doi is a valid DOI string
    if not _validate_doi(doi):
        raise ValueError(f"{doi} is not a valid DOI string")

    # Strip doi from https://doi.org/ if present
    doi = (
        doi.replace("https://doi.org/", "")
        if doi.startswith("https://doi.org/")
        else doi
    )

    # Get the DOI metadata
    url = f"https://doi.org/{doi}"
    doi_response = requests.get(url, headers={"Accept": "application/json"})
    if doi_response.status_code != 200:
        raise ValueError(
            f"Unable to retrieve the metadata of the DOI {doi} from crossref"
        )
    doi_response = doi_response.json()

    # Get the supplementary content via datacite
    # pass the doi part only
    url = f"https://api.datacite.org/dois?query=relatedIdentifiers.relatedIdentifier:{doi}"
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code != 200:
        raise ValueError(
            f"Unable to retrieve the supplementary content via reverse lookup of {doi}"
        )
    response = response.json()

    if "data" in response and len(response["data"]) == 0:
        raise ValueError(f"No supplementary material found via reverse lookup of {doi}")

    response["data"] = response["data"][
        0
    ]  # TODO: Handle multiple supplementary materials hits

    # Check that this file is meant as a supplementary material to our DOI
    if not any(
        [
            ri["relatedIdentifier"] == doi
            for ri in response["data"]["attributes"]["relatedIdentifiers"]
            if ri["relationType"] == "IsSupplementTo"
        ]
    ):
        raise ValueError(
            f"Supplementary material {response['data']['id']} is not a related to {doi}"
        )

    # get contribution info
    contributions_urls = [
        url["relatedIdentifier"]
        for url in filter(
            lambda x: x["relationType"] == "HasPart"
            and x["relatedIdentifierType"] == "URL"
            and x["resourceTypeGeneral"] == "Dataset",
            response["data"]["attributes"]["relatedIdentifiers"],
        )
    ]
    return doi_response, contributions_urls
