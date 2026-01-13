import json
from typing import Dict

from orkg.client.templates.statements import ObjectStatement
from orkg.convert import JsonLDConverter
from orkg.out import OrkgResponse


class TemplateInstance(object):
    """
    A class that takes a dictionary in the constructor with methods
    to serialize the dictionary to a file, pretty print it, and send it to the KG.
    """

    def __init__(self, template_dict, orkg_client) -> None:
        self.template_dict = template_dict
        self.client = orkg_client
        self.preprocess_dict()

    def preprocess_dict(self):
        if isinstance(self.template_dict, str):
            self.template_dict = (
                self.template_dict.strip("'<>() ")
                .replace("'", '"')
                .replace("{{", "{")
                .replace("}}", "}")
                .replace('""', '"')
            )
            self.template_dict = json.loads(self.template_dict)

    def serialize_to_file(self, file_path: str, format: str = "orkg") -> None:
        """
        Serializes the template to a file.
        :param format: the format of the serialization (default: "orkg", possible: "json-ld")
        :param file_path: the file path to save the template to
        """
        with open(file_path, "w") as f:
            if format.lower().strip() == "json-ld":
                json.dump(
                    JsonLDConverter(self.client.host).convert_2_jsonld(
                        self.template_dict
                    ),
                    f,
                    indent=4,
                )
            else:
                json.dump(self.template_dict, f, indent=4)

    def pretty_print(self, format: str = "orkg") -> None:
        """
        Pretty prints the template to the console.
        :param format: the format of the printed text (default: "orkg", possible: "json-ld")
        """
        if format.lower().strip() == "json-ld":
            print(
                json.dumps(
                    JsonLDConverter(self.client.host).convert_2_jsonld(
                        self.template_dict
                    ),
                    indent=4,
                )
            )
        else:
            print(json.dumps(self.template_dict, indent=4))

    def save(self) -> OrkgResponse:
        """
        Saves the template to the server.
        :return: The OrkgResponse from the server
        """
        return self.client.objects.add(params=self.template_dict)

    @staticmethod
    def parse_dict(dictionary: Dict, obj: ObjectStatement) -> None:
        if "resource" in dictionary:
            # This is a complete resource and not a nested one
            dictionary = dictionary["resource"]
            obj.set_resource(dictionary["name"], dictionary["classes"])
            if "values" in dictionary:
                dictionary = dictionary["values"]
        for key, values in dictionary.items():
            for value in values:
                sub_obj = ObjectStatement(key, obj.template_id)
                obj.add_value(sub_obj)
                if "text" in value:
                    datatype = value.get("datatype", None)
                    sub_obj.set_literal(f"\"{value['text']}\"", datatype)
                elif "label" in value:
                    classes = value.get("classes", None)
                    sub_obj.set_resource(f"\"{value['label']}\"", classes)
                    if "values" in value:
                        TemplateInstance.parse_dict(value["values"], sub_obj)
