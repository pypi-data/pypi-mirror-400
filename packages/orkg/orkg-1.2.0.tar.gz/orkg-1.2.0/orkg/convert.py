from typing import Dict, List

import pandas as pd


class JsonLDConverter:
    """
    Custom convertor from ORKG JSON to JSON-LD
    """

    _blank_node_counter = 1

    def __init__(self, host: str):
        self.ORKG_PREFIX = host
        if self.ORKG_PREFIX[-1] != "/":
            self.ORKG_PREFIX += "/"
        self.CLASS_PREFIX = f"{self.ORKG_PREFIX}class/"
        self.RESOURCE_PREFIX = f"{self.ORKG_PREFIX}resource/"
        self.PREDICATE_PREFIX = f"{self.ORKG_PREFIX}property/"

    def __handle_csvw_dataset(self, lol: List[List], context: Dict) -> Dict:
        # following CSVW @ https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/
        if len(lol) == 0:
            return {}
        # create table node - the node that will be returned
        table_node = {"@type": [f"{self.CLASS_PREFIX}Table"], "label": "Table"}
        # create columns and assign them
        columns = lol[0]
        context["columns"] = f"{self.PREDICATE_PREFIX}CSVW_Columns"
        context["name"] = f"{self.PREDICATE_PREFIX}CSVW_Name"
        context["number"] = f"{self.PREDICATE_PREFIX}CSVW_Number"
        column_nodes = [
            {
                "@type": [f"{self.CLASS_PREFIX}Column"],
                "titles": [c],
                "number": i,
                "@id": self.get_blank_node_id(),
            }
            for i, c in enumerate(columns, start=1)
        ]
        table_node["columns"] = column_nodes
        # iterate over rows and create them
        row_nodes = []
        for i, r in enumerate(lol[1:], start=1):
            row = {
                "@type": [f"{self.CLASS_PREFIX}Row"],
                "titles": [f"Row {i}"],
                "cells": [],
                "number": i,
            }
            # run through cells
            for idx, c in enumerate(r):
                row["cells"].append(
                    {
                        "@type": [f"{self.CLASS_PREFIX}Cell"],
                        "value": str(c) if not pd.isna(c) else None,
                        "column": column_nodes[idx]["@id"],
                    }
                )
            # append row to rows
            row_nodes.append(row)
        context["rows"] = f"{self.PREDICATE_PREFIX}CSVW_Rows"
        context["cells"] = f"{self.PREDICATE_PREFIX}CSVW_Cells"
        context["value"] = f"{self.PREDICATE_PREFIX}CSVW_Value"
        context["titles"] = f"{self.PREDICATE_PREFIX}CSVW_Titles"
        context["column"] = f"{self.PREDICATE_PREFIX}CSVW_Column"
        table_node["rows"] = row_nodes
        return table_node

    def get_blank_node_id(self) -> str:
        """
        Creates an incremental blank node identifier for the json-ld structure
        :return: string in the form of _:n{number}
        """
        bn_id = f"_:n{self._blank_node_counter}"
        self._blank_node_counter = self._blank_node_counter + 1
        return bn_id

    def convert_2_jsonld(self, orkg_json: Dict) -> Dict:
        """
        Convert an ORKG JSON format to an equivalent JSON-LD format
        :param orkg_json: The root ORKG JSON object
        :return: a json object in the format of JSON-LD
        """
        context = {}
        jsonld = {}
        if "resource" in orkg_json:
            orkg_json = orkg_json["resource"]
        # create dummy blank node
        jsonld["@id"] = self.get_blank_node_id()

        # handle label
        jsonld["label"] = orkg_json["name"]
        context["label"] = "http://www.w3.org/2000/01/rdf-schema#label"

        # handle classes
        jsonld["@type"] = [self.CLASS_PREFIX + c for c in orkg_json["classes"]]

        # handle values
        self.handle_values(orkg_json["values"], jsonld, context)

        # prepare final jsonld
        jsonld["@context"] = context
        return jsonld

    def handle_values(self, orkg_json: Dict, jsonld: Dict, context: Dict) -> None:
        """
        Recursively handle the values part of the ORKG JSON format
        :param orkg_json: the ORKG object to work on
        :param jsonld: the resulting JSON-LD part
        :param context: the accompanying context for JSON-LD
        :return: Nothing, since it operates on the parameter dictionaries
        """
        # add predicates into context
        for prop, url in [(p, self.PREDICATE_PREFIX + p) for p in orkg_json.keys()]:
            context[prop] = url

        # handle each predicate
        for key, entities in orkg_json.items():
            jsonld[key] = []
            for entity in entities:
                jsonld_entity = {}
                # handle dataframe values
                if "@df" in entity:
                    jsonld_entity = self.__handle_csvw_dataset(entity["@df"], context)
                # handle @id
                if "@id" in entity:
                    if "@type" in entity:  # TODO: replace with match in python 3.10
                        entity_type = entity["@type"]
                        if entity_type == "resource":
                            jsonld_entity["@id"] = self.RESOURCE_PREFIX + entity["@id"]
                        elif entity_type == "class":
                            jsonld_entity["@id"] = self.CLASS_PREFIX + entity["@id"]
                        elif entity_type == "predicate":
                            jsonld_entity["@id"] = self.PREDICATE_PREFIX + entity["@id"]
                        else:
                            # FIXME: the literal value should be looked up and added here properly
                            jsonld_entity["@literal"] = entity["@id"]
                    else:
                        jsonld_entity["@id"] = self.RESOURCE_PREFIX + entity["@id"]

                # handle text
                if "text" in entity:
                    literal_value = entity["text"]
                    if "datatype" in entity:
                        literal_value = f"{literal_value}^^{jsonld_entity['datatype']}"
                    jsonld[key].append(literal_value)

                # handle label
                if "label" in entity:
                    jsonld_entity["@id"] = self.get_blank_node_id()
                    jsonld_entity["label"] = entity["label"]
                    if "classes" in entity:
                        jsonld_entity["@type"] = [
                            self.CLASS_PREFIX + c for c in entity["classes"]
                        ]

                    # handle values
                    if "values" in entity:
                        self.handle_values(entity["values"], jsonld_entity, context)
                # append newly created json-ld entity property
                if len(jsonld_entity) > 0:
                    jsonld[key].append(jsonld_entity)
