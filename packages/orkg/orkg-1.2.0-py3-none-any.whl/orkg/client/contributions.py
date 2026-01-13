from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from orkg.common import ComparisonType, ExportFormat, ThingType
from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, simcomp_available


class ContributionsClient(NamespacedClient):
    @simcomp_available
    def similar(self, contribution_id: str, candidate_count: int = 10) -> OrkgResponse:
        """
        Get contributions which are similar to a specified contribution.
        Returns a list of [contribution ID, contribution label, paper ID, paper title, and similarity score].

        :param contribution_id: contribution ID
        :param candidate_count: number of similar contributions to return (default: 10)
        :return: OrkgResponse object of similar contributions
        """
        self.client.simcomp._append_slash = True
        response = self.client.simcomp.contribution.similar.GET(
            params={"contribution_id": contribution_id, "n_results": candidate_count}
        )
        return self.client.wrap_response(response=response)

    @simcomp_available
    def compare(
        self,
        contributions: List[str],
        comparison_type: ComparisonType = ComparisonType.PATH,
        export_format: Optional[ExportFormat] = None,
    ) -> OrkgResponse:
        """
        Get comparison by list of contribution IDs.

        :param contributions: list of contribution IDs
        :param comparison_type: type of comparison to perform (default: ComparisonType.PATH)
        :param export_format: format of comparison export (default: None)
        :return: OrkgResponse object of the comparison
        """
        self.client.simcomp._append_slash = False
        response = self.client.simcomp.contribution.compare.GET(
            params={
                "contributions": contributions,
                "type": comparison_type.value,
                "format": None if export_format is None else export_format.value,
            }
        )
        return self.client.wrap_response(response=response)

    @simcomp_available
    def compare_dataframe(
        self,
        contributions: Optional[List[str]] = None,
        comparison_id: Optional[str] = None,
        like_ui=True,
        include_meta=False,
        comparison_type: ComparisonType = ComparisonType.PATH,
        thing_type: Optional[ThingType] = ThingType.COMPARISON,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Fetches an ORKG comparison into a pandas.DataFrame.
        Optional: create a second DataFrame of contribution metadata.
        Included metadata (when present): author, doi, publication month, publication year, url, research field, venue

        :param contributions: list of contribution IDs from a comparison
        :param comparison_id: ID of a comparison
        :param like_ui: true/false whether to match comparison df to its UI representation
        :param include_meta: true/false whether to return metadata df
        :param comparison_type: the method used to compare the contributions - PATH or MERGE (default: PATH)
        :param thing_type: type of thing to export (default: COMPARISON)
        :return:
            - comparison DataFrame
            - metadata DataFrame (optional)
        """
        # Check if valid request
        if contributions is None and comparison_id is None:
            raise ValueError("either provide the contributions, or the comparison ID")
        if contributions is not None and comparison_id is not None:
            raise RuntimeWarning(
                "both contributions and comparison ID provided, using comparison ID"
            )

        if comparison_id is not None:
            df: pd.DataFrame = self._export_comparison(
                comparison_id, like_ui, thing_type
            )
        else:
            df: pd.DataFrame = self._compare_contributions_and_export(
                comparison_type, contributions
            )

        if include_meta:
            # Collect required components to generate metadata dataframe
            if comparison_id is not None:
                raw_response = self.client.json.get_json(
                    thing_key=comparison_id, thing_type=thing_type
                ).content
            else:
                raw_response = self.compare(
                    contributions=contributions, comparison_method=comparison_type
                ).content
            # Use helper method to create metadata df
            return df, self._create_metadata_df(
                [c for c in df.columns],
                {
                    contribution[
                        "id"
                    ]: f"{contribution['paper_label']}/{contribution['label']}"
                    for contribution in raw_response["payload"]["thing"]["data"][
                        "contributions"
                    ]
                },
                raw_response["payload"]["thing"]["data"]["contributions"],
            )
        return df

    def _compare_contributions_and_export(
        self, comparison_type: ComparisonType, contributions: List[str]
    ) -> pd.DataFrame:
        """
        Compare contributions and return a DataFrame.
        :param comparison_type: the method used to compare the contributions - PATH or MERGE (default: PATH)
        :param contributions: list of contribution IDs from a comparison
        :return: a pandas DataFrame
        """
        # Use the compare endpoint
        response = self.compare(
            contributions=contributions,
            comparison_type=comparison_type,
            export_format=ExportFormat.DATAFRAME,
        )
        if not response.succeeded:
            raise RuntimeError(
                f"Failed to fetch live data for contributions {contributions}"
            )
        df = self._convert_simcomp_df_to_pandas_df(response.content)
        return df

    def _export_comparison(
        self, comparison_id: str, like_ui: bool, thing_type: ThingType
    ) -> pd.DataFrame:
        """
        Export a comparison and return a DataFrame.
        :param comparison_id: ID of a comparison
        :param like_ui: true/false whether to match comparison df to its UI representation
        :param thing_type: type of thing to export (default: COMPARISON)
        :return: a pandas DataFrame
        """
        # Use the export endpoint
        response = self.client.simcomp.thing.export.GET(
            params={
                "thing_key": comparison_id,
                "thing_type": thing_type.value,
                "format": ExportFormat.DATAFRAME.value,
                "like_ui": like_ui,
            }
        )
        if not response.ok:
            raise RuntimeError(f"Failed to get thing {comparison_id}")
        df = self._convert_simcomp_df_to_pandas_df(response.json())
        return df

    @staticmethod
    def _convert_simcomp_df_to_pandas_df(simcomp_json: Dict) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(simcomp_json)
        # iterate over each cell in the dataframe
        for column in df.columns:
            for row in range(len(df)):
                # if a value contains <SEP> split it and make the cell a list
                if "<SEP>" in df[column][row]:
                    df[column][row] = df[column][row].split("<SEP>")
        return df

    def _create_metadata_df(
        self,
        columns: List[str],
        contribution_ids_and_titles: Dict[str, str],
        contributions_list: List[Dict],
    ) -> pd.DataFrame:
        """
        Create a metadata DataFrame containing the following properties (when available):
            author, doi, publication month, publication year, url, research field, venue
        Column headings are identical to the comparison DataFrame.

        :param columns: list of headings for df columns
        :param contribution_ids_and_titles: dictionary of contribution IDs to headings: Paper Title/Contribution N (Contribution ID)
        :param contributions_list: list of contribution dictionaries containing contribution label, ID, paper ID, title, and year
        :return: metadata DataFrame
        """
        paper_set = set(
            [f"{contribution['paper_id']}" for contribution in contributions_list]
        )
        comparison_meta_data = {}
        # create dict of meta properties and values
        for paper in paper_set:
            contribution_ids, paper_meta_data = self._get_paper_metadata(
                contributions_list, paper
            )
            # add paper meta info for each contribution to comparison meta info
            for contribution_id in contribution_ids:
                column_name = contribution_ids_and_titles[contribution_id]
                paper_dict = paper_meta_data.copy()
                comparison_meta_data[column_name] = paper_dict
                comparison_meta_data[column_name]["contribution id"] = contribution_id
        # Make dataframe with same column order as comparison df and replace missing fields with empty string
        df_meta = pd.DataFrame.from_dict(comparison_meta_data)[columns].fillna("")
        return df_meta

    def _get_paper_metadata(
        self, contributions_list: List[Dict], paper: str
    ) -> Tuple[List, Dict]:
        """
        Get metadata info for a paper.

        :param contributions_list: list of contribution dictionaries containing contribution label, ID, paper ID, title, and year
        :param paper: ID of the paper
        :return:
            - list of IDs of contributions belonging to this paper
            - dictionary of (available) paper metadata properties to values
        """
        # author, doi, publication month, publication year, url, research field, venue
        meta_property_ids = ["P27", "P26", "P28", "P29", "url", "P30", "HAS_VENUE"]
        paper_meta_dict_of_lists = defaultdict(list)
        paper_statements = self.client.statements.get_by_subject_unpaginated(
            subject_id=paper
        )
        for statement in paper_statements.content:
            if statement["predicate"]["id"] in meta_property_ids:
                pred = statement["predicate"]["label"]
                obj = statement["object"]["label"]
                paper_meta_dict_of_lists[pred].append(obj)
        # make dict values strings if only one and list of strings if two or more
        paper_meta_data = {
            k: v.pop() if len(v) == 1 else v
            for k, v in paper_meta_dict_of_lists.items()
        }
        paper_meta_data["title"] = paper_statements.content[0]["subject"]["label"]
        paper_meta_data["paper id"] = paper
        # get IDs of all contributions from this paper which are included in the comparison
        contribution_ids = [
            str(contribution["id"])
            for contribution in contributions_list
            if contribution["paper_id"] == paper
        ]
        return contribution_ids, paper_meta_data
