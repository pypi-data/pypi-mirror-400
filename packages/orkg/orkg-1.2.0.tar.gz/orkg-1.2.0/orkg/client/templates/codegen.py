"""
Some imports here though are not used by the codegen.py file itself, but are used by the generated code.
So they should be kept. and in case of any linter support in the future, they should be ignored.
"""

import datetime
import types
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from cardinality import at_least, at_most
from inflector import English, Inflector

from orkg.client.templates.components import DataFrame, NestedTemplate, Template
from orkg.client.templates.out import ObjectStatement, TemplateInstance
from orkg.client.templates.utils import (
    Boolean,
    Date,
    Integer,
    Number,
    String,
    check_against_keywords,
    clean_up_dict,
    post_process_dict,
    pre_process_string,
    stringify_value,
)
from orkg.common import OID
from orkg.utils import NamespacedClient


class OTFFunctionWriter(object):
    inflector = Inflector(English)

    @staticmethod
    def convert_df_to_list_of_lists(df: pd.DataFrame, label: Optional[str] = None) -> Dict[str, Union[str, List[List]]]:
        result = [[c for c in df.columns]]
        for index, row in df.iterrows():
            result.append([row[c] for c in df.columns])
        to_return = {'@df': result}
        if label is not None:
            to_return['label'] = label
        return to_return

    @staticmethod
    def implement_function(
            orkg_context: NamespacedClient,
            template_id: str
    ):
        template = Template.find_or_create_template(orkg_context.client, template_id)
        params, params_docstring = template.get_params_as_function_params()
        object_json, properties = template.create_api_object()
        lookup_map = {component.get_clean_name(): component.predicate_id for component in template.components}
        values_fillers_variable = "partial_json"
        values_fillers = OTFFunctionWriter.create_values_fillers(properties, lookup_map, values_fillers_variable)
        cardinality_checks = OTFFunctionWriter.create_cardinality_checks(template)
        function_name = check_against_keywords(pre_process_string(template.template_name))
        new_method = f'''
def {function_name}(self, {params}) -> TemplateInstance:
    """ Creates a template of type {template_id} ({template.template_name})

    {params_docstring}
    :return: a string representing the resource ID of the newly created resource
    """
    lookup_map = {lookup_map}
{cardinality_checks}
    obj = ObjectStatement.create_main({'""' if template.is_formatted else 'label'}, ['{template.template_class}'])
    {values_fillers_variable} = {object_json}
{values_fillers}
    obj = {values_fillers_variable}
    for param_name, nested_template in {{k: v for k, v in locals().items() if any(isinstance(v, t) for t in (TemplateInstance, pd.DataFrame, Tuple, OID, List))}}.items():
        predicate_id = lookup_map[param_name]
        if 'values' not in obj['resource']:
            obj['resource']['values'] = {{}}
        if predicate_id not in obj['resource']['values']:
            obj['resource']['values'][predicate_id] = []
        if isinstance(nested_template, pd.DataFrame):
            obj['resource']['values'][predicate_id].append(OTFFunctionWriter.convert_df_to_list_of_lists(nested_template))
        elif isinstance(nested_template, Tuple):
            obj['resource']['values'][predicate_id].append(OTFFunctionWriter.convert_df_to_list_of_lists(*nested_template))
        elif isinstance(nested_template, OID):
            obj['resource']['values'][predicate_id].append(nested_template.to_orkg_json())
        elif isinstance(nested_template, List):
            for template in nested_template:
                if isinstance(template, TemplateInstance):
                    obj['resource']['values'][predicate_id].append(clean_up_dict(template.template_dict))
        else:
            obj['resource']['values'][predicate_id].append(clean_up_dict(nested_template.template_dict))
    post_process_dict(obj)
    return TemplateInstance(obj, self.client)

if '{function_name}' in orkg_context.client.templates.materialized_templates:
    delattr(orkg_context.client.templates, '{function_name}')
orkg_context.client.templates.{function_name} = types.MethodType( {function_name}, orkg_context )
orkg_context.client.templates.materialized_templates.add('{function_name}')
                    '''
        exec(new_method)

    @staticmethod
    def create_cardinality_checks(template: Template) -> str:
        code = ""
        for component in template.components:
            param_name = component.get_clean_name()
            if component.min_cardinality or component.max_cardinality:
                error_message = f"The parameter {param_name} must have"
                if component.min_cardinality:
                    error_message += f" at least {component.min_cardinality} {OTFFunctionWriter.inflector.conditional_plural(component.min_cardinality, 'value')}" if component.min_cardinality else ""
                if len(error_message) > 0 and component.max_cardinality:
                    error_message += f" and at most {component.max_cardinality} {OTFFunctionWriter.inflector.conditional_plural(component.max_cardinality, 'value')}" if component.max_cardinality else ""
                code += f"    if isinstance({param_name}, List):\n"
                if component.min_cardinality:
                    code += f"        if not at_least({component.min_cardinality}, {param_name})"
                if component.max_cardinality:
                    if component.min_cardinality:
                        code += f" or not at_most({component.max_cardinality}, {param_name})"
                    else:
                        code += f"        if not at_most({component.max_cardinality}, {param_name})"
                code += ":\n"
                code += f"            raise ValueError('Oops! {error_message}')\n"
        return code

    @staticmethod
    def create_values_fillers(properties: List[ObjectStatement], properties_lookup_map: Dict, values_fillers_variable: str) -> str:
        code = ""
        properties_dict = {p.predicate_id: p for p in properties}
        for param_name, predicate_id in properties_lookup_map.items():
            if predicate_id not in properties_dict:
                continue
            object_description = properties_dict[predicate_id].serialize()
            if len(object_description) > 0:
                code += f"\n    # Updating {param_name}\n"
                code += f"    if '{predicate_id}' not in {values_fillers_variable}:\n"
                code += f"        {values_fillers_variable}['resource']['values']['{predicate_id}'] = []\n"
                code += f"    if isinstance({param_name}, OID):\n"
                code += f"        {values_fillers_variable}['resource']['values']['{predicate_id}'].append({{'@id': str({param_name})}})\n"
                code += f"    elif isinstance({param_name}, List):\n"
                code += f"        for i in range(len({param_name})):\n"
                code += f"            if isinstance({param_name}[i], OID):\n"
                code += f"                object_description_at_i = {{'@id': str({param_name}[i])}}\n"
                code += f"            if 'text' in object_description_at_i:\n"
                code += f"                object_description_at_i['text'] = {param_name}[i]\n"
                code += f"            elif 'label' in object_description_at_i:\n"
                code += f"                object_description_at_i['label'] = {param_name}[i]\n"
                code += f"            {values_fillers_variable}['resource']['values']['{predicate_id}'].append(object_description_at_i)\n"
                code += f"    else:\n"
                code += f"        {values_fillers_variable}['resource']['values']['{predicate_id}'].append({object_description})\n"
        return code
