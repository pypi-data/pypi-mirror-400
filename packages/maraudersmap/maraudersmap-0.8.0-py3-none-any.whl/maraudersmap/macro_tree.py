""" Set of function used to generate a networkX graph for a file representation
of a repository such as size, complexity"""

import networkx as nx
from loguru import logger
from pathlib import Path

from maraudersmap.tree import get_tree
from maraudersmap.nx_utils import get_root_from_tree
from maraudersmap.show_pyplot import fastplot


def _rec_to_macro_tree(graph: nx.DiGraph, node: str) -> nx.DiGraph:
    """
    Set the new leaf of the macro tree.

    Args:
        graph (obj): networkX graph
        node (str): Name of the root node

    """
    succ = list(graph.successors(node))

    if graph.number_of_nodes() == 1:  # If macro_tree is run on a single file
        graph.nodes[node]["leaf"] = True

    if succ:
        for child in succ:
            child_succ = list(graph.successors(child))
            if child_succ:
                _rec_to_macro_tree(graph, child)
            else:
                graph.nodes[child]["soften"] = False
                graph.nodes[child]["leaf"] = True


def _rec_node_to_erase(
    graph: nx.DiGraph,
    node: str,
) -> list:
    """
    Update the data of the nodes graph according to the successors, i.e. update
    the ccn, size and check if it's a leaf, or an empty folder.

    Args:
        graph (obj): networkX graph
        node (str): node name

    Returns:
        node_to_erase (list): Names of node to erase from tree_graph
    """
    succ = list(graph.successors(node))
    node_to_erase = []
    if succ:
        for child in succ:
            rm_node = _rec_node_to_erase(graph, child)
            node_to_erase += rm_node
    else:
        node_to_erase.append(node)
    return node_to_erase


###################################


def get_macro_tree(
    path: str,
    code_name: str,
) -> nx.DiGraph:
    """
    Main function that builds the network X macro tree graph.

    Args:
        path (str): Path to the root folder of the code or file
        code_name (str): Name of the code

    Returns:
        graph (obj): NetworkX of the tree_graph
    """
    tree_graph = get_tree(path, code_name, filter_extensions=False)

    root = get_root_from_tree(tree_graph)
    # root="root"
    # fastplot(tree_graph)

    macro_graph = tree_graph.copy()
    logger.info("Tree graph built")
    logger.info("Generating macro_tree ...")

    if Path(path).is_file():
        logger.info(
            "Macro tree run on a single file, one and only one node will be displayed."
        )
    else:
        node_to_erase = _rec_node_to_erase(tree_graph, root)
        logger.debug(f"Node erased are {node_to_erase}")

        for node in node_to_erase:
            macro_graph.remove_node(node)

        _rec_to_macro_tree(macro_graph, root)

    return macro_graph
