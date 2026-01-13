import datetime
import keyword
import re
from collections.abc import MutableMapping
from typing import Any, Dict, List, Union

Number = Union[int, float, complex, List[int], List[float], List[complex]]
Boolean = Union[bool, List[bool]]
String = Union[str, List[str]]
Integer = Union[int, List[int]]
Date = Union[datetime.date, List[datetime.date]]


def clean_up_dict(dictionary: dict) -> dict:
    """
    replaces the key 'name' with 'label' inside the 'resource' object.
    then strips the root key 'resource' and returns the inner dictionary.
    """
    dictionary = dictionary["resource"]
    dictionary["label"] = dictionary["name"]
    del dictionary["name"]
    return dictionary


def pre_process_string(string: str) -> str:
    lower_string = string.lower().replace(" ", "_")
    res = re.sub(r"\W+", "", lower_string)
    return res


def check_against_keywords(string: str) -> str:
    """
    Checks a string against python keywords.
    If a keyword is found, it is postfixed with a '_template'.
    """
    if string in keyword.kwlist:
        return string + "_template"
    return string


def map_type_to_pythonic_type(value_type: str) -> str:
    if value_type == "Number" or value_type == "Decimal":
        return "Number"
    elif value_type == "Boolean":
        return "Boolean"
    elif value_type == "Integer":
        return "Integer"
    elif value_type == "Date":
        return "Date"
    else:
        return "String"


def remove_empty_values(dictionary: dict):
    if "values" not in dictionary["resource"]:
        return
    for _, value in dictionary["resource"]["values"].items():
        for v in value:
            if not bool(v):
                value.remove(v)


def _check_duplicates(items: List[Dict[str, Any]]) -> None:
    """
    Remove duplicate dictionaries and dictionaries with None text or label
    from a list.

    Args:
        items (List[Dict[str, Any]]): List of dictionaries to check.
    """
    seen = []
    to_remove = []
    for item in items:
        if item in seen:
            to_remove.append(item)
        elif "text" in item and item["text"] == "None":
            to_remove.append(item)
        elif "label" in item and item["label"] == "None":
            to_remove.append(item)
        else:
            seen.append(item)
    # Remove duplicate or None text/label items
    for item in to_remove:
        items.remove(item)


def recursive_dict_check(input_dict: Any) -> None:
    """
    Recursively traverse the dictionary to remove duplicate dictionaries
    and dictionaries with None text or label in all lists.

    Args:
        input_dict (Any): Input JSON value, dict, list or scalar.
    """
    for key, value in input_dict.items():
        if key == "@df":
            continue
        if isinstance(value, list):
            # check for duplicate dicts in lists
            _check_duplicates(value)
            # also check each dict item in the list
            for item in value:
                if isinstance(item, MutableMapping):
                    recursive_dict_check(item)
        elif isinstance(value, MutableMapping):
            # if value is a dict, check the dict
            recursive_dict_check(value)


def remove_empty_lists_from_values(input_dict: Any) -> None:
    """
    Recursively traverse the dictionary to remove empty lists from the 'values' key.

    Args:
        input_dict (Any): Any Input JSON value, dict, list or scalar.
    """
    to_remove = []
    for key, value in input_dict.items():
        if key == "values":
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list) and not sub_value:
                    to_remove.append(sub_key)
        elif isinstance(value, MutableMapping):
            remove_empty_lists_from_values(value)
    # remove empty lists
    for key in to_remove:
        del input_dict["values"][key]


def post_process_dict(dictionary: dict):
    remove_empty_values(dictionary)
    recursive_dict_check(dictionary)
    remove_empty_lists_from_values(dictionary)


def stringify_value(value: Any) -> str:
    if isinstance(value, datetime.date):
        return value.isoformat()
    else:
        return str(value)
