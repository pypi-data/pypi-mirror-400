from typing import Dict, Optional

from orkg.out import OrkgResponse, OrkgUnpaginatedResponse
from orkg.utils import NamespacedClient, dict_to_url_params, query_params


class StatementsClient(NamespacedClient):
    def by_id(self, id: str) -> OrkgResponse:
        self.client.backend._append_slash = True
        response = self.client.backend.statements(id).GET()
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get(self, params: Optional[Dict] = None) -> OrkgResponse:
        self.handle_sort_params(params)
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_unpaginated(
        self, start_page: int = 0, end_page: int = -1, params: Optional[Dict] = None
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get, args={}, params=params, start_page=start_page, end_page=end_page
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_subject(
        self, subject_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        self.handle_sort_params(params)
        params.update({"subject_id": subject_id})
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_unpaginated(
        self,
        subject_id: str,
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_subject,
            args={"subject_id": subject_id},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_predicate(
        self, predicate_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        self.handle_sort_params(params)
        params.update({"predicate_id": predicate_id})
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_predicate_unpaginated(
        self,
        predicate_id: str,
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_predicate,
            args={"predicate_id": predicate_id},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_object(
        self, object_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        self.handle_sort_params(params)
        params.update({"object_id": object_id})
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_object_unpaginated(
        self,
        object_id: str,
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_object,
            args={"object_id": object_id},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_object_and_predicate(
        self, object_id: str, predicate_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        self.handle_sort_params(params)
        params.update({"object_id": object_id, "predicate_id": predicate_id})
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_object_and_predicate_unpaginated(
        self,
        object_id: str,
        predicate_id: str,
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_object_and_predicate,
            args={"object_id": object_id, "predicate_id": predicate_id},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_and_predicate(
        self, subject_id: str, predicate_id: str, params: Optional[Dict] = None
    ) -> OrkgResponse:
        self.handle_sort_params(params)
        params.update({"subject_id": subject_id, "predicate_id": predicate_id})
        response = self.client.backend.statements.GET(params=params)
        return self.client.wrap_response(response)

    @query_params("page", "size", "sort", "desc")
    def get_by_subject_and_predicate_unpaginated(
        self,
        subject_id: str,
        predicate_id: str,
        start_page: int = 0,
        end_page: int = -1,
        params: Optional[Dict] = None,
    ) -> OrkgUnpaginatedResponse:
        return self._call_pageable(
            self.get_by_subject_and_predicate,
            args={"subject_id": subject_id, "predicate_id": predicate_id},
            params=params,
            start_page=start_page,
            end_page=end_page,
        )

    @query_params("subject_id", "predicate_id", "object_id")
    def add(self, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) != 3:
            raise ValueError("all parameters must be provided")
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements.POST(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("subject_id", "predicate_id", "object_id")
    def update(self, id: str, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) == 0:
            raise ValueError("at least one parameter must be provided")
        else:
            if not self.exists(id):
                raise ValueError("the provided id is not in the graph")
            self.client.backend._append_slash = True
            response = self.client.backend.statements(id).PUT(
                json=params, headers=self.auth
            )
            if response.ok:
                return self.client.expand_response(response)
        return self.client.wrap_response(response)

    @query_params("min_level", "max_level", "blacklist", "whitelist", "include_first")
    def bundle(self, thing_id: str, params: Optional[Dict] = None) -> OrkgResponse:
        if len(params) > 0:
            self.client.backend._append_slash = False
            response = self.client.backend.statements(thing_id).bundle.GET(
                dict_to_url_params(params)
            )
        else:
            self.client.backend._append_slash = True
            response = self.client.backend.statements(thing_id).bundle.GET()
        return self.client.wrap_response(response)

    def delete(self, id: str) -> OrkgResponse:
        if not self.exists(id):
            raise ValueError("the provided id is not in the graph")
        self.client.backend._append_slash = True
        response = self.client.backend.statements(id).DELETE()
        return self.client.wrap_response(response)

    def exists(self, id: str) -> bool:
        return self.by_id(id).succeeded
