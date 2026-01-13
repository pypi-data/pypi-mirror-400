from typing import Dict, Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class LiteralsClient(NamespacedClient):
    def by_id(self, id: str) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.literals(id).GET()
        return self.client.wrap_response(response)

    @query_params("q", "exact")
    def get_all(self, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.literals.GET(dict_to_url_params(params))
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.literals.GET()
        return self.client.wrap_response(response)

    @query_params("id", "label", "datatype")
    def add(self, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least label must be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.literals.POST(json=params, headers=self.auth)
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("label", "datatype")
    def update(self, id: str, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("label must be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.literals(id).PUT(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    def exists(self, id: str) -> bool:
        return self.by_id(id).succeeded
