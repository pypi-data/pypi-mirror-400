import uuid
from typing import Dict, List, Union


def process_contribution(
    contribution_json: Union[Dict, List, str],
    resulting_object: Union[Dict, List],
    global_ids: Dict,
    context: Dict,
):
    if isinstance(contribution_json, List):
        for item in contribution_json:
            process_contribution(item, resulting_object, global_ids, context)
    elif isinstance(contribution_json, Dict):
        if isinstance(resulting_object, List):
            current_object = {}
            resulting_object.append(current_object)
            resulting_object = current_object
        for key, value in contribution_json.items():
            if key == "@id":
                if value.startswith("_:"):
                    global_ids[value] = "_" + str(uuid.uuid4())
                    resulting_object["@temp"] = global_ids[value]
                else:
                    resulting_object["@id"] = value.rsplit("/", 1)[-1]
            elif key == "@type":
                resulting_object["classes"] = [
                    clazz.rsplit("/", 1)[-1] for clazz in contribution_json[key]
                ]
            elif key == "label":
                resulting_object["label"] = str(contribution_json[key])
            elif key == "@context":
                continue
            else:
                orkg_predicate_id = context[key].rsplit("/", 1)[-1]
                # other keys
                if "values" not in resulting_object:
                    resulting_object["values"] = {}
                if isinstance(value, List) and all(
                    isinstance(item, str)
                    or isinstance(item, int)
                    or isinstance(item, float)
                    or isinstance(item, bool)
                    for item in value
                ):
                    resulting_object["values"][orkg_predicate_id] = [
                        {"text": str(item)} for item in value
                    ]
                elif isinstance(value, List) or isinstance(value, Dict):
                    predicate_values = []
                    resulting_object["values"][orkg_predicate_id] = predicate_values
                    process_contribution(value, predicate_values, global_ids, context)
                else:
                    # Check if the value starts with "_:"
                    # FIXME: Workaround because the descriptions aren't up to date!!
                    if key not in context:
                        orkg_predicate_id = f"CSVW_{key.title()}"
                    resulting_object["values"][orkg_predicate_id] = []
                    if isinstance(value, str) and value.startswith("_:"):
                        resulting_object["values"][orkg_predicate_id].append(
                            {"@id": global_ids[value]}
                        )
                    else:
                        resulting_object["values"][orkg_predicate_id].append(
                            {"text": str(value)}
                        )
        if "classes" in resulting_object and "label" not in resulting_object:
            resulting_object["label"] = ""
