import warnings
from typing import Any, AnyStr, Callable, Dict, List, Optional, Type, Union

import pandas as pd
from loguru import logger

from orkg.graph import subgraph
from orkg.logging_messages import MessageBuilder


def _filter_dict(
    d: Dict[str, Any],
    keys_to_exclude: Union[str, List[str]],
    required_key: Optional[str] = None,
) -> Union[Dict[str, Any], None]:
    """
    Returns a new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`.

    If `required_key` is provided and it exists in `d`, the function will return a new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`. If `required_key` is not provided or it does not exist in `d`, the function will return None.

    Args:
    - d: A dictionary whose keys are strings and whose values can be of any type.
    - keys_to_exclude: A string or list of strings representing the keys to be excluded from the output dictionary.
    - required_key: An optional string representing a key that must exist in `d` for the function to return a dictionary. If `required_key` is not provided or it does not exist in `d`, the function will return None.

    Returns:
    - A new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`, or None if `required_key` is not provided or it does not exist in `d`.
    """
    if isinstance(keys_to_exclude, str):
        keys_to_exclude = [keys_to_exclude]
    if required_key is not None and required_key not in d:
        return None
    return {k: v for k, v in d.items() if k not in keys_to_exclude}


class OrkgResponse(object):
    # Class-level variable to store the ORKG client
    orkg_client = None

    # Class-level dictionary to store type conversion functions
    type_registry = {}

    @property
    def succeeded(self) -> bool:
        return str(self.status_code)[0] == "2"

    def __init__(
        self,
        client,
        response,
        status_code: Optional[str],
        content: Optional[Union[List, Dict, AnyStr]],
        url: str,
    ):
        self.orkg_client = client
        if response is None and status_code is None and content is None and url is None:
            logger.debug(MessageBuilder.backend_response_none())
            raise ValueError(
                "either response should be provided or content with status code"
            )
        if (response is not None and str(response.status_code)[0] != "2") or (
            status_code is not None and content is not None and status_code[0] != "2"
        ):
            self.status_code = (
                response.status_code if response is not None else status_code
            )
            self.content = response.content if response is not None else content
            self.page_info = None
            logger.debug(
                MessageBuilder.backend_response(
                    self.content, self.status_code, response
                )
            )
            return
        if response is not None:
            self.status_code = response.status_code
            self.content = (
                response.json()
                if len(response.content) > 0
                and response.content.decode("utf-8")[0] in ["[", "{"]
                else response.content.decode("utf-8")
            )
            self.page_info = None
            if isinstance(self.content, dict):
                self.page_info = _filter_dict(self.content, "content")
                self.content = (
                    self.content["content"]
                    if "content" in self.content
                    else self.content
                )
            self.url = response.url
            logger.debug(
                MessageBuilder.backend_response(
                    self.content, self.status_code, self.url
                )
            )
        if status_code is not None and content is not None:
            self.status_code = status_code
            self.content = content
            self.page_info = None
            if isinstance(self.content, dict) and "content" in content:
                self.page_info = _filter_dict(self.content, "content")
                self.content = self.content["content"]
            self.url = url
            logger.debug(
                MessageBuilder.backend_response(
                    self.content, self.status_code, self.url
                )
            )

    def __repr__(self) -> str:
        return "%s %s" % ("(Success)" if self.succeeded else "(Fail)", self.content)

    def __str__(self) -> Union[List, Dict]:
        return self.content

    def as_type(self, object_type: Type, *args, **kwargs) -> Any:
        """
        Convert the content of the response to the specified type using the registered conversion function.
        Args:
            object_type (Type): a type (e.g., float, pandas.DataFrame).
            *args: Variable length argument list to pass to the conversion function.
            **kwargs: Keyword arguments to pass to the conversion function.

        Returns:
            T: The content of the response converted to the specified type.
        """
        if object_type not in self.type_registry:
            raise ValueError(f"Type '{object_type}' is not registered for conversion.")

        conversion_function = self.type_registry[object_type]
        return conversion_function(self, *args, **kwargs)

    @classmethod
    def register_type(cls, object_type: Type, conversion_function: Callable) -> None:
        """
        Register a type conversion function in the type registry.
        Args:
            object_type (Type): a type (e.g., float, pandas.DataFrame).
            conversion_function (Callable): Function that performs the conversion.
        """
        cls.type_registry[object_type] = conversion_function

    def as_float(self) -> float:
        """
        Convert the content of the response to a float.
        returns: a float
        """
        if self.content is None:
            raise ValueError("Response content is None")
        if isinstance(self.content, list):
            raise ValueError("Can't convert list to int")
        return self.as_type(float)

    def as_int(self) -> int:
        """
        Convert the content of the response to an int.
        returns: an int
        """
        if self.content is None:
            raise ValueError("Response content is None")
        if isinstance(self.content, list):
            raise ValueError("Can't convert list to int")
        return self.as_type(int)

    def as_dataframe(self) -> pd.DataFrame:
        """
        Convert the content of the response to a pandas DataFrame.
        returns: a pandas DataFrame
        """
        if self.content is None:
            raise ValueError("Response content is None")
        if isinstance(self.content, list):
            raise ValueError("Can't convert list to a dataframe")
        if self.content["_class"] != "resource":
            raise ValueError("Response content is not a resource")
        if "Table" not in self.content["classes"]:
            raise ValueError("resource is not a table object")
        nx_object = subgraph(client=self.orkg_client, thing_id=self.content["id"])
        columns = [
            nx_object.edges(s, data=True)
            for s in [
                o
                for s, o, p in nx_object.edges(self.content["id"], data=True)
                if p["id"] == "CSVW_Columns"
            ]
        ]
        columns_of_df = []
        for column in columns:
            name = ""
            order = -1
            for _, o, p in column:
                if p["id"] == "CSVW_Number":
                    order = nx_object.nodes[o]["label"]
                if p["id"] == "CSVW_Name":
                    name = nx_object.nodes[o]["label"]
            columns_of_df.append((int(order), name))
        rows = [
            nx_object.edges(s, data=True)
            for s in [
                o
                for s, o, p in nx_object.edges(self.content["id"], data=True)
                if p["id"] == "CSVW_Rows"
            ]
        ]
        result = [[] for _ in range(len(rows))]
        index_of_df = []
        for row in rows:
            order = -1
            title = ""
            values = []
            for s, o, p in row:
                if p["id"] == "CSVW_Number":
                    order = nx_object.nodes[o]["label"]
                if p["id"] == "CSVW_Titles":
                    title = nx_object.nodes[o]["label"]
                if p["id"] == "CSVW_Cells":
                    cells = nx_object.edges(o, data=True)
                    for _, o, p in cells:
                        if p["id"] == "CSVW_Value":
                            values.append(nx_object.nodes[o]["label"])
                        else:
                            values.append("")
            index_of_df.append((int(order), title))
            result[int(order) - 1] = values
        columns = [c[1] for c in sorted(columns_of_df, key=lambda x: x[0])]
        index = [i[1] for i in sorted(index_of_df, key=lambda x: x[0])]
        return pd.DataFrame(result, columns=columns, index=index)


# Register conversion functions, order doesn't matter
OrkgResponse.register_type(float, lambda response: float(response.content["label"]))
OrkgResponse.register_type(int, lambda response: int(response.content["label"]))
OrkgResponse.register_type(pd.DataFrame, OrkgResponse.as_dataframe)


class OrkgUnpaginatedResponse(object):
    @property
    def all_succeeded(self) -> bool:
        return all([response.succeeded for response in self.responses])

    def __init__(self, responses: List[OrkgResponse]):
        self.responses = responses
        self.content: List[Dict] = []

        for response in self.responses:
            self.content.extend(response.content)
