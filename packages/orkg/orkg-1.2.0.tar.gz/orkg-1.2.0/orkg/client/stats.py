from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient


class StatsClient(NamespacedClient):
    def get(self) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.stats.GET()
        return self.client.wrap_response(response)
