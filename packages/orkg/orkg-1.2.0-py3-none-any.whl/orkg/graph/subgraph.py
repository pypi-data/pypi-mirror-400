from typing import Any, List, Union

import networkx as nx
from requests.exceptions import RequestException


def subgraph(
    client: Any,
    thing_id: str,
    blacklist: Union[str, List[str]] = "",
    max_level: int = -1,
) -> nx.DiGraph:
    """
    Obtains a networkx directed graph representation of any ORKG component given by its thing_id.
    E.g. of ORKG components: Paper, Contribution, Comparison, Template

    It starts from the thing_id resource and traverses the graph until all literals are reached.

    :param client: orkg.ORKG client used to connect with ORKG backend.
    :param thing_id: Any subject, object or predicate ID in the ORKG.
    :param blacklist: Class(es) to be excluded from the subgraph. E.g. 'ResearchField'
        (see `orkgc:ResearchField <https://orkg.org/class/ResearchField>`_).
        Note that the first subgraph level will always be included.
    :param max_level: Deepest subgraph's level to traverse.
    """
    blacklist = [blacklist] if isinstance(blacklist, str) else blacklist

    try:
        response = client.statements.bundle(
            thing_id,
            params={
                "include_first": "true",
                "blacklist": ",".join(blacklist),
                "max_level": max_level,
            },
        )
    except RequestException:
        response = None

    if not response or not response.succeeded:
        raise ValueError(
            "Something went wrong while connecting to ORKG backend with host {}".format(
                client.host
            )
        )

    statements = response.content["statements"]

    if not statements:
        raise ValueError("Nothing found for the provided ID: {}".format(thing_id))

    return _construct_subgraph(statements)


def _construct_subgraph(statements: list) -> nx.DiGraph:
    """
    Constructs a subgraph represented by the given RDF ``statements``.

    :param statements: List of all RDF statements describing the subgraph.
    """
    _subgraph = nx.DiGraph()

    for statement in statements:
        # NetworkX does not create a node or an edge double, therefore, the following implementation works :)
        start_node = _create_node_from_thing(_subgraph, statement["subject"])
        target_node = _create_node_from_thing(_subgraph, statement["object"])
        _create_edge(_subgraph, start_node, target_node, statement["predicate"])

    return _subgraph


def _create_node_from_thing(_subgraph: nx.DiGraph, thing: dict) -> str:
    _subgraph.add_node(node_for_adding=thing["id"], **thing)
    return thing["id"]


def _create_edge(
    _subgraph: nx.DiGraph, start_node: str, target_node: str, predicate: dict
) -> None:
    _subgraph.add_edge(start_node, target_node, **predicate)
