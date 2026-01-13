from typing import List, Optional, Union

from orkg.client.harvesters import directory as directory_harvester
from orkg.client.harvesters import doi as doi_harvester
from orkg.common import OID
from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient


class HarvestersClient(NamespacedClient):
    def doi_harvest(
        self,
        doi: str,
        orkg_rf: Union[str, OID],
        directory: Optional[str] = None,
        slow_mode: Optional[bool] = False,
    ) -> OrkgResponse:
        """
        Harvests DOI data for a paper and add it to the ORKG.
        It works under the assumption that the paper contains some JSON-LD representation of its content
        If directory is provided, it is expected to have a `doi.json` file and other json files that are the contributions.
        If the `doi.json` doesn't exist and the `doi` parameter is present then the metadata is fetched from the DOI and the contributions from disk.
        :param doi: The DOI of the paper to harvest
        :param orkg_rf: The resource ID of the ORKG research field to add the harvested data to, or the string representation to be looked up (can raise errors)
        :param slow_mode: Chunks the paper into contributions to avoid technical timeouts! (optional)
        :param directory: The directory to read the specs from (optional)
        """
        return doi_harvester.harvest(
            orkg_client=self.client,
            doi=doi,
            orkg_rf=orkg_rf,
            directory=directory,
            slow_mode=slow_mode,
        )

    def directory_harvest(
        self,
        directory: str,
        research_field: Union[str, OID],
        title: str,
        doi: Optional[str] = None,
        authors: Optional[List[Union[str, OID]]] = None,
        publication_year: Optional[int] = None,
        publication_month: Optional[int] = None,
        published_in: Optional[str] = None,
        url: Optional[str] = None,
        extraction_method: Optional[str] = None,
        slow_mode: Optional[bool] = False,
        **kwargs,
    ) -> OrkgResponse:
        """
        Harvests a directory of JSON-LD files created by the templates and add it to the ORKG.
        :param directory: The directory to read the specs from
        :param research_field: The resource ID of the ORKG research field to add the harvested data to, or the string representation to be looked up (can raise errors)
        :param title: The title of the paper
        :param doi: The DOI of the paper (optional)
        :param authors: The authors of the paper (optional)
        :param publication_year: The publication year of the paper (optional)
        :param publication_month: The publication month of the paper (optional)
        :param published_in: The publication venue of the paper (optional)
        :param url: The URL of the paper (optional)
        :param extraction_method: The extraction method of the paper - should be one of: UNKNOWN, AUTOMATIC, MANUAL (optional)
        :param slow_mode: Chunks the paper into contributions to avoid technical timeouts! (optional)
        :param kwargs: Additional arguments to be passed to the paper object
        """

        return directory_harvester.harvest(
            orkg_client=self.client,
            directory=directory,
            research_field=research_field,
            title=title,
            doi=doi,
            authors=authors,
            publication_year=publication_year,
            publication_month=publication_month,
            published_in=published_in,
            url=url,
            extraction_method=extraction_method,
            slow_mode=slow_mode,
            **kwargs,
        )
