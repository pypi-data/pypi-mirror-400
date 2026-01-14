import networkx as nx
from maraudersmap.score import get_leaves, get_routine_content
from maraudersmap.nx_utils import get_root_from_tree


def analyze_grep_pragma(pattern: str, struct: dict, routine: list) -> dict:
    """
    Look for the presence of a pragma grep, if it's there then the grep coverage will be 1.
    
    Args:
        pattern (str): Pattern to find.
        struct (dict): Struct of the routine (from struct_repo or struct_files).
        routine (list): Code of the routine.

    Returns:
        Update the current graph leaves with the grep key
    """
    struct["grep"] = 0
    for line in routine:
        if pattern in line.strip():
            struct["grep"] = 1
            break

    return struct


# def _rec_inherit_grep_cov(graph: nx.DiGraph, root: str) -> None:
#     """
#     Recursive addition of grep coverage pourcentage per node starting from the root of the graph

#     Args:
#         graph (obj): networkX DiGraph
#         root (str): name of the root node

#     Returns:
#         Update the current graph by adding the grep coverage
#     """
#     succ = list(graph.successors(root))
#     if succ:
#         grep_cov = 0
#         for child in succ:
#             _rec_inherit_grep_cov(graph, child)
#             grep_cov += graph.nodes[child]["grep"]

#         grep_cov /= len(succ)
#         graph.nodes[root]["grep"] = grep_cov


# def build_covgraph(pattern, graph: nx.DiGraph, leaves: list) -> nx.DiGraph:
#     """ """
#     for leaf in leaves:
#         graph.nodes[leaf]["grep"] = 0
#         if graph.nodes[leaf].get("analyzed", True) and not graph.nodes[leaf].get(
#             "empty_folder", False
#         ):
#             # analyze pragma
#             routine_content = get_routine_content(
#                 graph.nodes[leaf]["path"],
#                 graph.nodes[leaf]["line_start"],
#                 graph.nodes[leaf]["line_end"],
#             )

#             graph = analyze_grep_pragma(pattern, graph, routine_content, leaf)

#     root_node = get_root_from_tree(graph)
#     _rec_inherit_grep_cov(graph, root_node)

#     return graph


# def get_grep_coverage(pattern, graph: nx.DiGraph) -> nx.DiGraph:
#     """
#     Compute the grep coverage graph by looking for grep pragma inside the routines
#     based on the tree function analysis of maraudersmap

#     Args:
#         graph (obj): networkX DiGraph

#     Returns:
#         grep_cov_graph (obj) networkX DiGraph with grep coverage computed
#     """
#     leaves = get_leaves(graph)
#     grep_cov_graph = build_covgraph(pattern, graph, leaves)
#     return grep_cov_graph


def set_grep_codebase(
    pattern: str, struct: dict, repo_path: str, struct_file: dict
) -> None:
    """
    [RECURSIVE] Compute the grep coverage on all the codebase.

    Args:
        pattern (str): Pattern to grep.
        struct (dict): Structure of the element (from struct_repo).
        repo_path (str): Local path to the repo.
        struct_file (dict): struct_files data.
    """
    childrens = struct["children"]
    if childrens:
        # inherit grep from childrens
        grep_cov = 0
        for child in childrens:
            set_grep_codebase(pattern, child, repo_path, struct_file)
            # grep_cov += child["grep"]
        # grep_cov /= len(childrens) # keep for percentage
        struct["grep"] = grep_cov
    else:
        # struct_repo was generated with procedures (`-p`) : leaves are elements inside files.
        if struct["type"] != "folder" and struct["type"] != "file":
            path = repo_path + "/" + struct["path"]
            set_grep_routine(pattern, struct, path)
        # struct_repo was generated without procedures : leaves are files.
        # -> use struct_files data.
        elif struct["type"] == "file":
            path = repo_path + "/" + struct["path"]
            struct["grep"] = get_grep_file(pattern, struct_file[struct["path"]], path)
        # empty folder
        else:
            struct["grep"] = 0


def set_grep_routine(pattern: str, struct_routine: dict, path: str) -> None:
    """
    Compute the grep coverage by looking for grep pragma inside the routines

    Args:
        pattern (str): Pattern to find.
        struct_routine (dict): Structure of the routine
                               (from struct_repo or struct_files)
        path (str): Path of the file
    """
    routine_content = get_routine_content(
        path,
        struct_routine["lines"][0],
        struct_routine["lines"][1],
    )
    struct_routine = analyze_grep_pragma(pattern, struct_routine, routine_content)


def get_grep_file(pattern: str, struct_file: dict, path: str) -> int:
    """
    Get the grep coverage for a single file using struct_files data.
    It's only used if struct_repo doesn't contain the procedures.

    Args:
        pattern (str): Pattern to find.
        struct_file (dict): struct_files data.
        repo_path (str): Local path to the repo.

    Returns:
        int: 1 if pattern in the file's code. 0 if not.
    """
    if struct_file != {}:
        for process in struct_file.values():
            set_grep_routine(pattern, process, path)
            if process["grep"] == 1:
                return 1
    return 0
