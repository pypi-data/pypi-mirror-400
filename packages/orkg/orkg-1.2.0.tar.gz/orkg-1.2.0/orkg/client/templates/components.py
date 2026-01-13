from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from orkg.client.templates.out import TemplateInstance
from orkg.client.templates.statements import ObjectStatement
from orkg.client.templates.utils import (
    check_against_keywords,
    map_type_to_pythonic_type,
    pre_process_string,
)
from orkg.common import OID
from orkg.utils import NamespacedClient

NATIVE_TYPES = ["Number", "String", "Boolean", "Integer", "Date", "URI", "Decimal"]
DATAFRAME_CLASSES = ["QBDataset", "Table"]

NestedTemplate = Union[TemplateInstance, OID, List[TemplateInstance], List[OID]]
DataFrame = Union[
    pd.DataFrame,
    Tuple[pd.DataFrame, str],
    OID,
    List[pd.DataFrame],
    List[Tuple[pd.DataFrame, str]],
    List[OID],
]


class TemplateComponent:
    """
    A template component, which represents a property of a template.
    The shape of each property is defined by the component.
    """

    predicate_id: str
    predicate_label: str
    value_class_id: Optional[str]
    value_class_label: Optional[str]
    is_of_custom_type: bool
    min_cardinality: Optional[int]
    max_cardinality: Optional[int]
    is_nested_template: bool
    nested_template_target: Optional[str]

    # private properties
    _orkg_client: NamespacedClient

    def __init__(self, orkg_client, component_id: str):
        self._orkg_client = orkg_client
        component_statements = orkg_client.statements.get_by_subject(
            subject_id=component_id, size=99999
        ).content
        # Set predicate info
        predicate = list(
            filter(lambda x: x["predicate"]["id"] == "sh:path", component_statements)
        )[0]["object"]
        self.predicate_id = predicate["id"]
        self.predicate_label = predicate["label"]
        # Set class value, id, and label
        value_class = list(
            filter(
                lambda x: x["predicate"]["id"] in ["sh:class", "sh:datatype"],
                component_statements,
            )
        )
        if len(value_class) == 0:
            self.value_class_id = "String"
            self.value_class_label = "Text"
            self.is_of_custom_type = False
        else:
            value_class = value_class[0]["object"]
            self.value_class_id = value_class["id"]
            self.value_class_label = value_class["label"]
            self.is_of_custom_type = (
                True if self.value_class_id not in NATIVE_TYPES else False
            )
        # Set cardinality of the property
        max_cardinality = list(
            filter(
                lambda x: x["predicate"]["id"] == "sh:maxCount", component_statements
            )
        )
        self.max_cardinality = (
            None
            if len(max_cardinality) == 0
            else int(max_cardinality[0]["object"]["label"])
        )
        min_cardinality = list(
            filter(
                lambda x: x["predicate"]["id"] == "sh:minCount", component_statements
            )
        )
        self.min_cardinality = (
            None
            if len(min_cardinality) == 0
            else int(min_cardinality[0]["object"]["label"])
        )
        # Set if the component is nested template
        if not self.is_of_custom_type:
            self.is_nested_template = False
        else:
            template_classes = orkg_client.statements.get_by_object_and_predicate(
                object_id=self.value_class_id, predicate_id="sh:targetClass", size=99999
            ).content
            if len(template_classes) == 0:
                self.is_nested_template = False
            else:
                self.is_nested_template = True
                self.nested_template_target = template_classes[0]["subject"]["id"]
                # Recursively materialize nested templates of the root
                if self.nested_template_target not in Template.wip_templates:
                    Template.wip_templates.add(self.nested_template_target)
                    self._orkg_client.templates.materialize_template(
                        self.nested_template_target
                    )

    def get_clean_name(self) -> str:
        return pre_process_string(check_against_keywords(self.predicate_label))

    def get_return_type(self, optional: bool = False) -> str:
        if not optional and self.min_cardinality == 0:
            return f"Optional[{self.get_return_type(True)}]"
        # Check if the return type should be a pandas.DataFrame
        if self.value_class_id in DATAFRAME_CLASSES:
            return "DataFrame"
        # Check if it is a nested template
        if self.is_nested_template:
            return "NestedTemplate"
        # o/w it is a pure python type
        return f"Union[{map_type_to_pythonic_type(self.value_class_id)}, OID]"

    def get_property_as_function_parameter(self) -> str:
        clean_label = self.get_clean_name()
        return_type = self.get_return_type()
        default_value = " = None" if self.min_cardinality == 0 else ""
        return f"{clean_label}: {return_type}{default_value}"

    def get_param_documentation(self) -> str:
        if self.is_nested_template:
            target_template = Template.find_or_create_template(
                self._orkg_client, self.nested_template_target
            )
            param_desc = f":param {self.get_clean_name()}: a nested template, use orkg.templates.{target_template.get_template_name_as_function_name()} or OID object or a list of the same"
        else:
            # component is not nested template, return normal documentation
            param_desc = f":param {self.get_clean_name()}: a parameter of type {self.value_class_label} or List[{self.value_class_label}] or OID object"
        if self.min_cardinality == 0:
            param_desc += " (optional)"
        return param_desc

    def create_object_statement(self) -> ObjectStatement:
        to_str = self.get_return_type() == "datetime.date"
        value = self.get_clean_name()
        statement = ObjectStatement(
            self.predicate_id, "UNKNOWN"
        )  # FIXME: template_id is unknown in this scope
        if not self.is_nested_template:
            if self.is_of_custom_type:
                statement.set_resource(
                    label=f"str({value})" if to_str else value,
                    classes=[self.value_class_id],
                )
            else:
                statement.set_literal(
                    text=f"str({value})" if to_str else value,
                    datatype=None,  # FIXME: datatype is not set for literals
                )
        return statement

    def __str__(self):
        return f'{"N" if self.is_nested_template else ""}Property(id="{self.predicate_id}", label="{self.predicate_label}", class="{self.value_class_id}", cardinality=({self.min_cardinality}, {self.max_cardinality}))'


class Template(object):
    # Static variables to keep track of all templates
    templates: Dict = {}
    wip_templates: Set = set()

    # Instance variables
    template_class: str
    is_formatted: bool
    template_id: str
    template_name: str
    components: List[TemplateComponent]
    is_strict: bool

    def __init__(self, orkg_client, template_id: str):
        # Add the template to the static variable
        Template.wip_templates.add(template_id)
        # Fetch template statements
        self.components = []
        template_statements = orkg_client.statements.get_by_subject(
            subject_id=template_id, size=99999
        ).content
        # Iterate over template statements and create template components
        components = filter(
            lambda x: x["predicate"]["id"] == "sh:property", template_statements
        )
        for component in components:
            self.components.append(
                TemplateComponent(orkg_client, component["object"]["id"])
            )
        # Set template class
        self.template_class = list(
            filter(
                lambda x: x["predicate"]["id"] == "sh:targetClass", template_statements
            )
        )[0]["object"]["id"]
        # Set template info
        self.template_id = template_id
        self.template_name = orkg_client.resources.by_id(id=template_id).content[
            "label"
        ]
        self.is_formatted = (
            len(
                list(
                    filter(
                        lambda x: x["predicate"]["id"] == "TemplateLabelFormat",
                        template_statements,
                    )
                )
            )
            > 0
        )
        strict_statement = list(
            filter(lambda x: x["predicate"]["id"] == "sh:closed", template_statements)
        )
        self.is_strict = (
            len(strict_statement) > 0
            and strict_statement[0]["object"]["label"].lower() == "true"
        )
        # Register template to the global templates dict
        Template.templates[template_id] = self
        # Sort components where the components with min cardinality 0 are at the end
        self.components.sort(key=lambda x: x.min_cardinality, reverse=True)

    @staticmethod
    def find_or_create_template(orkg_client, template_id: str) -> "Template":
        """
        Check if template is in registry, if yes return it.
        Otherwise, instantiate a new template.
        """
        if template_id in Template.templates:
            return Template.templates[template_id]
        else:
            return Template(orkg_client, template_id)

    def get_params_as_function_params(self) -> Tuple[str, str]:
        """
        Returns a tuple of the function parameters for the template.
        The first element is the function parameters as a string,
        the second element is the function docstring as a string.
        """
        params = ", ".join(
            [c.get_property_as_function_parameter() for c in self.components]
        )
        if not self.is_formatted:
            params = f"label: str, {params}"
            if params.strip()[-1] == ",":
                params = params.strip()[:-1]
        params_docstring = "\n\t".join(
            [comp.get_param_documentation() for comp in self.components]
        )
        if not self.is_formatted:
            params_docstring = f":param label: the label of the resource of type string\n\t{params_docstring}"
        return params, params_docstring

    def get_template_name_as_function_name(self) -> str:
        return check_against_keywords(pre_process_string(self.template_name))

    def create_api_object_values_and_classes(self) -> Tuple[List[ObjectStatement], str]:
        """
        Returns the API object values for the template.
        """
        properties = [
            c.create_object_statement()
            for c in self.components
            if c.value_class_id not in DATAFRAME_CLASSES
        ]
        return properties, f'"classes": ["{self.template_class}"]'

    def create_api_object(self) -> Tuple[str, List[ObjectStatement]]:
        """
        Returns a partial ORKG API object for the template as string., needs to be completed with the resource values.
        The second value returned is a list of the properties that are used by the code generator to fill the values
        """
        properties, classes = self.create_api_object_values_and_classes()
        object_json = f"""{{
                "resource": {{
                    "name": {'""' if self.is_formatted else 'label'},
                    {classes},
                    "values": {{}}
                }}
            }}"""
        return object_json, properties

    def __str__(self):
        return f'Template(id="{self.template_id}", class="{self.template_class}", components= "{len(self.components)} comps."))'
