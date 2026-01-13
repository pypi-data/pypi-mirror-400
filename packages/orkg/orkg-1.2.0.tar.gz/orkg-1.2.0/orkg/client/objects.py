from typing import Dict

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient


class ObjectsClient(NamespacedClient):
    def add(self, params: Dict) -> OrkgResponse:
        """
        Warning: Super-users only should use this endpoint
        Create a new object in the ORKG instance
        :param params: orkg Object
        :return: an OrkgResponse object containing the newly created object resource
        """
        self.client.backend._append_slash = True
        response = self.client.backend.objects.POST(json=params, headers=self.auth)
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)
