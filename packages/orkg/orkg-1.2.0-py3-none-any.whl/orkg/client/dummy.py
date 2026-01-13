from typing import Dict, List, Union

from orkg.out import OrkgResponse
from orkg.utils import NamespacedClient


class DummyClient(NamespacedClient):
    def create_xxx_response(
        self, code: str, content: Union[Dict, List]
    ) -> OrkgResponse:
        return OrkgResponse(
            client=self,
            status_code=code,
            content=content,
            response=None,
            url="",
        )

    def create_200_response(self, content: Union[Dict, List]) -> OrkgResponse:
        return self.create_xxx_response("200", content)

    def create_404_response(self, content: Union[Dict, List]) -> OrkgResponse:
        return self.create_xxx_response("404", content)
