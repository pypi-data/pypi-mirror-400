from typing import Dict, List, Optional, Union

from orkg.common import ThingType
from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, simcomp_available


class JSONClient(NamespacedClient):
    @simcomp_available
    def save_json(
        self,
        thing_key: str,
        thing_type: ThingType = ThingType.UNKNOWN,
        data: Optional[Union[Dict, List]] = None,
        config: Optional[Dict] = None,
    ) -> OrkgResponse:
        """
        Save a json object to the simcomp relational database
        :param thing_key: the key of the thing
        :param thing_type: the type of the thing (UNKNOWN, COMPARISON, DIAGRAM, VISUALIZATION, DRAFT_COMPARISON, LIST, REVIEW, QUALITY_REVIEW, PAPER_VERSION, ANY)
        :param data: the json object to save
        :param config: the config of the thing, used for comparisons mostly
        :return: the response of the request
        """
        # Check if the thing already exists
        res = self.client.json.get_json(thing_key, thing_type)
        if res.succeeded:
            raise ValueError(
                f"thing with key {thing_key} and type {thing_type.value} already exists!"
            )
        # Save the thing
        if config is None:
            config = {}
        if data is None:
            data = {}
        return self.client.wrap_response(
            self.client.simcomp.thing.POST(
                json={
                    "thing_key": thing_key,
                    "data": data,
                    "thing_type": thing_type.value,
                    "config": config,
                }
            )
        )

    @simcomp_available
    def get_json(self, thing_key: str, thing_type: ThingType) -> OrkgResponse:
        """
        Get a json object from the simcomp relational database
        :param thing_key: the key of the thing
        :param thing_type: the type of the thing
        :return: the response of the request
        """
        return self.client.wrap_response(
            self.client.simcomp.thing.GET(
                params={"thing_key": thing_key, "thing_type": thing_type.value}
            )
        )
