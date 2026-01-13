import json
from typing import Dict, List, Optional, Set

from tqdm import tqdm

from orkg.client.templates.codegen import OTFFunctionWriter
from orkg.client.templates.components import Template
from orkg.utils import NamespacedClient


class TemplatesClient(NamespacedClient):
    materialized_templates: Set[str] = set()

    def materialize_template(self, template_id: str):
        """
        Materialize a singular ORKG template as python function
        :param template_id: the template id
        :return: True if everything is OK
        """
        materialization_result = self._fetch_and_build_template_function(template_id)
        Template.wip_templates.clear()
        return materialization_result

    def materialize_templates(
        self, templates: Optional[List[str]] = None, verbose: bool = True
    ):
        """
        Materialize a list of templates (or all templates if not provided)
        :param templates: optional list of templates
        :param verbose: sets if the process shows a progress bar or suppresses it
        """
        if templates is None:
            templates = [
                template["id"]
                for template in self.client.classes.get_resource_by_class(
                    class_id="NodeShape", size=1000
                ).content
            ]
        iterator = (
            tqdm(templates, desc="Materializing templates") if verbose else templates
        )
        for template_id in iterator:
            self.materialize_template(template_id)

    def _fetch_and_build_template_function(self, template_id: str):
        """
        Internal function to create python digital twins of ORKG templates
        :param template_id: template ID to build
        :return: True if everything is OK
        """
        OTFFunctionWriter.implement_function(self, template_id)
        return True

    def list_templates(self):
        """
        List the set of materialized template functions
        :return: list of strings
        """
        return list(self.materialized_templates)

    def get_template_specifications(self, template_id: str) -> str:
        """
        Return JSON representation of a template's specification (schema)
        :param template_id: the template to lookup
        :return: string representation of a JSON object
        """
        template = Template(self.client, template_id)
        result = {
            comp.get_clean_name(): f"A value of type ({comp.value_class_label})"
            for comp in template.components
        }
        return json.dumps(result, indent=4, sort_keys=True, default=str)

    def create_template_instance(self, template_id: str, instance: Dict) -> str:
        """
        Creates an instance of a given template by filling in
        the specifications of the template with the provided values

        :param template_id: the string representing the template ID
        :param instance: the json object that contains the components of the template instance
        """
        template = Template(self.client, template_id)
        obj = template.create_api_object()
        for key, value in instance.items():
            obj = obj.replace(key, f'"{value}"')
        json_object = json.loads(obj)
        return self.client.objects.add(params=json_object).content["id"]
