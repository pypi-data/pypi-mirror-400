"""module to find stats about the graph

what are the most called nodes? the most caling nodes? both?"
"""
import numpy as np
import networkx as nx
from loguru import logger


def identity(x):
    return x


def ntw_stats_mvp(
    ntx: nx.DiGraph,
    file_prefix: str = "mmap_pyplot",
    debug=False,
):
    """
    Print a short list of most active nodes in the graph.

    Sorted by predecessors, then both, then successors.
    """

    pred = np.array([len(list(ntx.predecessors(node))) for node in ntx.nodes])
    succ = np.array([len(list(ntx.successors(node))) for node in ntx.nodes])

    indexes = []
    indexes = build_mvp(pred, seen_idx=indexes)
    indexes = build_mvp(pred + succ, seen_idx=indexes)
    indexes = build_mvp(succ, seen_idx=indexes)

    print_mvp(list(ntx.nodes), pred, succ, indexes)


def build_mvp(
    values: np.array,
    seen_idx: list = None,
    nsigma=3,
) -> list:
    """Add the indexes the outliers values, if these indexes were not seen before"""
    limit = values.mean() + nsigma * values.std()
    indexes = seen_idx
    for idx in reversed(np.argsort(values)):
        if values[idx] < limit:
            break
        if idx in seen_idx:
            continue
        indexes.append(idx)
    return indexes


def print_mvp(name: list, pred: np.array, succ: np.array, indexes: list):
    """Print a table of graph nodes , with predecessors and successors numbers"""
    print(f"  | succ | pred | name")
    for idx in indexes:
        print(f"  |{succ[idx]: 6d}|{pred[idx]: 6d}| {name[idx]}")
    print(f"  | succ | pred | name")
