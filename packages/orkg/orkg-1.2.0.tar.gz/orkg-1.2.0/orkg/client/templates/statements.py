from typing import List, Optional


class ObjectStatement(object):
    """
    A class representing a statement in the ORKG object format.
    The object statement could represent a resource, a literal, or a nested resource.
    """

    # Optionals
    label: Optional[str]
    classes: Optional[List[str]]
    text: Optional[str]
    datatype: Optional[str]
    values: Optional[List]
    name: Optional[str]
    # Must have
    predicate_id: str
    template_id: str

    def __init__(self, predicate_id: str, template_id: str):
        self.predicate_id = predicate_id
        self.template_id = template_id
        self.literals = []
        self.resources = []
        self.values = None
        self.name = None

    @staticmethod
    def create_main(name: str, classes: List[str] = None) -> "ObjectStatement":
        statement = ObjectStatement("", "")
        statement.set_main_statement(name, classes)
        return statement

    @property
    def is_main_statement(self) -> bool:
        return self.name is not None

    def set_main_statement(self, name: str, classes: List[str] = None):
        self.name = name
        self.classes = classes

    def set_literal(self, text: str, datatype: Optional[str] = None):
        self.literals.append((text, datatype))

    def set_nested_statement(self, statement: "ObjectStatement"):
        self.set_resource(statement.label, statement.classes)
        for value in statement.values:
            self.add_value(value)

    def set_resource(self, label: str, classes: List[str] = None):
        self.resources.append((label, classes))

    def add_value(self, value: "ObjectStatement"):
        if self.values is None:
            self.values = []
        self.values.append(value)

    def values_to_statements(self) -> str:
        if self.values is None:
            return "{}"
        return (
            "{"
            + ", ".join(
                [f'"{v.predicate_id}": [{{{v.to_statement()}}}]' for v in self.values]
            )
            + "}"
        )

    def to_statement(self) -> str:
        statement = ""
        for literal in self.literals:
            text, datatype = literal
            statement += f'{{"text": stringify_value({text})'
            if datatype is not None:
                statement += f', "datatype": "{datatype}"'
            statement += "}"
        for resource in self.resources:
            label, classes = resource
            statement += f'{{"label": {label}'
            if classes is not None:
                statement += f', "classes": {classes}'
            statement += "}"
            if self.values is not None:
                statement += f', "values": {self.values_to_statements()} '
        return statement

    def serialize(self) -> str:
        if self.is_main_statement:
            return f'{{"resource": {{"name": "{self.name}", "classes": {self.classes}, "values": {self.values_to_statements()}}}}}'
        else:
            return f"{self.to_statement()}"
