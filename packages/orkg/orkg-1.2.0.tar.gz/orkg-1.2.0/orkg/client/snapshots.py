from typing import Optional

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient


class SnapshotsClient(NamespacedClient):
    def single_of_resource(self, resource_id: str, snapshot_id: str) -> OrkgResponse:
        """
        Get a specific snapshot of a resource.

        :param resource_id: The ID of the resource.
        :param snapshot_id: The ID of the snapshot.
        :return: An OrkgResponse containing the snapshot data.
        """
        self.client.backend._append_slash = False
        response = (
            self.client.backend.resources(resource_id)
            .snapshots(snapshot_id)
            .GET(
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json;charset=UTF-8",
                }
            )
        )
        return self.client.wrap_response(response)

    def all_of_resource(
        self, resource_id: str, template_id: Optional[str] = None
    ) -> OrkgResponse:
        """
        Get all snapshots of a specific resource.

        :param resource_id: The ID of the resource.
        :param template_id: The id of the template that was used to create the resource snapshot. (optional)
        :return: An OrkgResponse containing the list of snapshots (paged).
        """
        self.client.backend._append_slash = True
        backend_func = self.client.backend.resources(resource_id).snapshots.GET
        if template_id is not None:
            response = backend_func(params={"template_id": template_id})
        else:
            response = backend_func()
        return self.client.wrap_response(response)

    def create_one(
        self, resource_id: str, template_id: str, register_handle: bool = True
    ) -> OrkgResponse:
        """
        Create a new snapshot for a specific resource.

        :param resource_id: The ID of the resource.
        :param template_id: The id of the template that will be used for subgraph exploration when creating the snapshot.
        :param register_handle: Whether to register a persistent Handle identifier. (optional, default: true)
        :return: An OrkgResponse containing the created snapshot data.
        """
        self.client.backend._append_slash = False
        response = self.client.backend.resources(resource_id).snapshots.POST(
            json={"template_id": template_id, "register_handle": register_handle},
            headers={
                **self.auth,
                "Accept": "application/json",
                "Content-Type": "application/json;charset=UTF-8",
            },
        )
        if response.ok:
            return self.client.expand_response(response)
        return self.client.wrap_response(response)
