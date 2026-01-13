import re
from enum import Enum
from typing import Optional


class OID(object):
    """
    Represents an ORKG ID
    """

    id: str
    type: Optional[str]

    def __init__(self, id: str, type: Optional[str] = None):
        """
        :param id: the id
        :param type: the type of the id (optional)
        """
        self.id = id
        self.type = type

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return self.id

    def __eq__(self, other: "OID") -> bool:
        if not isinstance(other, OID):
            return False
        return self.id == other.id and self.type == other.type

    def __hash__(self) -> int:
        return hash(self.id)

    def __bool__(self) -> bool:
        return bool(self.id)

    def is_literal_id(self) -> bool:
        return re.match(r"^L\d+$", self.id) is not None

    def is_resource_id(self) -> bool:
        return re.match(r"^R\d+$", self.id) is not None

    def is_predicate_id(self) -> bool:
        return re.match(r"^P\d+$", self.id) is not None

    def is_class_id(self) -> bool:
        return re.match(r"^C\d+$", self.id) is not None

    def is_custom_id(self) -> bool:
        return (
            not self.is_literal_id()
            and not self.is_resource_id()
            and not self.is_predicate_id()
            and not self.is_class_id()
        )

    def to_orkg_json(self) -> dict:
        obj = {"@id": self.id}
        if self.type:
            obj["@type"] = self.type
        return obj


class Hosts(Enum):
    PRODUCTION = "https://orkg.org"
    SANDBOX = "https://sandbox.orkg.org"
    INCUBATING = "https://incubating.orkg.org"


class ComparisonType(Enum):
    MERGE = "MERGE"
    PATH = "PATH"


class ExportFormat(Enum):
    CSV = "CSV"
    HTML = "HTML"
    DATAFRAME = "DATAFRAME"
    XML = "XML"
    UNKNOWN = "UNKNOWN"


class ThingType(Enum):
    COMPARISON = "COMPARISON"
    DIAGRAM = "DIAGRAM"
    VISUALIZATION = "VISUALIZATION"
    DRAFT_COMPARISON = "DRAFT_COMPARISON"
    LIST = "LIST"
    REVIEW = "REVIEW"
    QUALITY_REVIEW = "QUALITY_REVIEW"
    PAPER_VERSION = "PAPER_VERSION"
    ANY = "ANY"
    UNKNOWN = "UNKNOWN"
