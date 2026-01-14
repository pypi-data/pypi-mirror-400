"""Module to show a a networkX directed graph with nobvisual"""
from ctypes import c_int64

import networkx as nx

from networkx.readwrite import json_graph

from nobvisual.utils import mv_to_dict, path_as_str
from maraudersmap.nx_utils import get_root_from_tree


def ntw_nobvisual(
    ntx: nx.DiGraph,
):
    """
    Convert networkX to nobvisual

    Args:
        ntx (obj): NetworkX graph
        legend (dict): Name of the filed / Value of complexity as key, color as value

    Returns:
        Show nobvisual graph
    """
    for node in ntx.nodes():
        color = ntx.nodes[node].get("color", "#ffffff")
        ntx.nodes[node]["color"] = color

    root_node = get_root_from_tree(ntx)
    nstruct = ntx_to_nob(ntx, root_node)
    return nstruct


def ntx_to_nob(ntx: nx.DiGraph, root_node: str) -> list:
    """
    Convert networkX graph to list of nob data structure

    Args:
        ntx (obj): NetworkX graph
        root_node (str): Path to the main folder as str

    Returns:
        nstruct (list): List of nob object
    """
    json_data = json_graph.tree_data(ntx, root=root_node)
    json_data = clean_data(json_data)
    nob = mv_to_dict(json_data)
    nstruct = [_rec_nstruct(nob)]

    return nstruct


def clean_data(json_structure: dict) -> dict:
    """
    Only take the name, color, size, ccn and score value in each node of the graph through the json

    Args:
        json_structure (dict): Json representation of the graph

    Returns:
        json_clean (dict): Json with only the desired values
    """
    json_clean = {
        "name": json_structure.get("name", None),
        "color": json_structure.get("color", None),
        "ccn": json_structure.get("ccn", None),
        "size": json_structure.get("size", None),
        "score": json_structure.get("score", None),
        "grep": json_structure.get("grep", None),
        "coverage": json_structure.get("coverage", None),
    }

    if "children" in json_structure.keys():
        json_clean["children"] = []

        for child in json_structure["children"]:
            json_clean["children"].append(clean_data(child))
    else:
        pass

    return json_clean


def _rec_nstruct(in_: dict, item_id: int = c_int64(-1), path: str = None):
    """
    Recusive building of nstruct

    Args:
        in_ (dict): dict of the nob structure
        item_id (int): id of the item
        path (str): path to the file

    Returns:
        out (dict): dict for nob circular packing representation
    """
    if path is None:
        path = list()
    text = path_as_str(path)
    #text_ls = text.split()
    name = text#text_ls[-1].strip() if len(text_ls) else text

    item_id.value += 1
    out = {
        "id": item_id.value,
        "datum": None,
        "name": name,
        "text": text,
    }

    if "children" in in_.keys():
        out["datum"] = in_["size"]
        out["children"] = []
        tot_nloc = 0
        for id_child in in_["children"].keys():
            out["children"].append(
                _rec_nstruct(in_["children"][id_child], item_id=item_id, path=path)
            )
            tot_nloc += in_["children"][id_child]["size"]
        out["datum"] = tot_nloc
    else: #leaves
        out["datum"] = in_["size"]
        keys = ["name", "ccn", "size", "score", "coverage", "grep"]
        text = ""
        for key in keys:
            if key in in_:
                text += f"{key}: {in_[key]}\n"
                out[key]=in_[key]
            
        out["text"] = text
    out["name"] = in_["name"]
        

    return out
