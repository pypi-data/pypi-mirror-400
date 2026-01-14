import networkx as nx
import os
from loguru import logger
from pathlib import Path
import json, os
from yaml import safe_dump

from typing import List, Optional, Tuple
from tucan.package_analysis import (
    run_struct,
)
from tucan.travel_in_package import find_package_files_and_folders
from maraudersmap.valgrindload import valgrind_simplify_names


EPS = 1e-12


def get_callgraph(
    path: str,
    context: Optional[str] = None,
    mandatory_patterns: Optional[List[str]] = None,
    forbidden_patterns: Optional[List[str]] = None,
    valgrind_graph: Optional[nx.DiGraph] = None,
    cpp_directives: Optional[list] = None,
) -> Tuple[nx.DiGraph, dict]:
    """
    Get the  structure (what), and the context structure (with respect to what) to build the callgraph

    Args:
        path (str): Path to the repository
        context (Optional[str], optional): Path to the desired context. Defaults to None.
        mandatory_patterns (Optional[List[str]], optional): Words to keep in subpaths. Defaults to None.
        forbidden_patterns (Optional[List[str]], optional): Words to avoid in subpaths. Defaults to None.
        valgrind_graph (Optional[nx.DiGraph], optional): Valgrind graph trace. Defaults to None.
        cpp_directives (Optional[list], optional): List of CPP directives to resolve . Defaults to None.

    Returns:
        nx.DiGraph corresponding to the callgraph and dict of the repository structure analyzed by tucan.
    """

    if context is None:
        context = path

    if Path(path).is_file():
        tgt_code_db = run_struct(
            {os.path.basename(path): path}, cpp_directives=cpp_directives
        )
    else:
        tgt_paths_dict = find_package_files_and_folders(
            path,
            forbidden_patterns=forbidden_patterns,
            mandatory_patterns=mandatory_patterns,
        )
        tgt_code_db = run_struct(
            tgt_paths_dict, only_procedures=True, cpp_directives=cpp_directives
        )

    if context.strip("/") == path.strip(
        "/"
    ):  # often the case so it avoid recomputation
        context_code_db = tgt_code_db
    else:
        if Path(context).is_file():
            context_code_db = run_struct(
                {os.path.basename(context): context}, cpp_directives=cpp_directives
            )
        else:
            tgt_paths_dict = find_package_files_and_folders(context)
            context_code_db = run_struct(
                tgt_paths_dict, only_procedures=True, cpp_directives=cpp_directives
            )

    if valgrind_graph is not None:

        callgraph = build_callgraph_from_cg(
            tgt_code_db, context_code_db, valgrind_graph
        )
    else:
        callgraph = build_callgraph_static(
            tgt_code_db,
            context_code_db,
        )

    return callgraph, tgt_code_db


def build_callgraph_from_cg(
    tgt_code_db: dict, context_code_db: dict, valgrind_graph: nx.DiGraph
) -> nx.DiGraph:
    """
    Build the callgraph from a valgrind trace
    """

    valgrind_graph = valgrind_simplify_names(valgrind_graph)

    convert_vg_2_cg = {}

    for fname, fdata in context_code_db.items():
        for funcname in fdata:
            vg_style = "/" + fname + ":" + funcname.replace(".", "_")
            if vg_style in valgrind_graph.nodes:
                #            logger.success(vg_style)
                convert_vg_2_cg[vg_style] = fname + ":" + funcname
            else:
                pass
    #            logger.critical(vg_style)

    for node, val in convert_vg_2_cg.items():
        logger.critical(f"{node}<    >{val}")
    valgrind_graph = nx.relabel_nodes(valgrind_graph, convert_vg_2_cg)

    callgraph = nx.DiGraph()
    for node in valgrind_graph.nodes:
        fname, funcname = node.split(":")
        try:
            fdata = tgt_code_db[fname][funcname]
            _add_node(callgraph, fname, funcname, fdata)
            logger.success(f"Found {node}")
        except KeyError:
            fdata = {}
            logger.warning(f"Miss  {node}")
            _add_node(callgraph, fname, funcname, fdata)

    callgraph.edges = valgrind_graph.edges
    return callgraph


def build_callgraph_static(
    tgt_code_db: dict,
    context_code_db: dict,
) -> nx.DiGraph:
    """
    Build the callgraph from the staic analysis

    """
    logger.info("Computing callgraph, this can take a while...")

    ref_list = []
    for filename, fileddb in context_code_db.items():
        for funcname in fileddb:
            ref_list.append(filename + ":" + funcname)

    report = {
        "calls": {"guessed": [], "missed": []},
        "parents": {"guessed": [], "missed": []},
        "contains": {"guessed": [], "missed": []},
    }
    positive_i = 0
    negative_i = 0
    positive_p = 0
    negative_p = 0
    positive_c = 0
    negative_c = 0

    callgraph = nx.DiGraph()
    for file_orig, file_db in tgt_code_db.items():
        for func_orig, func_db in file_db.items():
            if f"{file_orig}:{func_orig}" not in callgraph.nodes:
                # callgraph.add_node(f"{file_orig}:{func_orig}", **func_db)
                _add_node(callgraph, file_orig, func_orig, func_db)

            for contained_name in func_db["contains"]:
                # logger.critical(contained_name)
                match_name, match_file = find_function_reference(
                    ref_list, contained_name, file_orig
                )

                if match_name is not None:
                    match_ddb = context_code_db[match_file][match_name]
                    _add_link(
                        callgraph,
                        match_ddb,
                        file_orig,
                        file_orig,
                        func_orig,
                        match_name,
                        type="contain",
                    )

                    report["contains"]["guessed"].append(f"{func_orig}->{match_name}")
                else:
                    report["contains"]["missed"].append(f"{func_orig}")

            for parent_name in func_db["parents"]:
                match_name, match_file = find_function_reference(
                    ref_list, parent_name, file_orig
                )
                if match_name is not None:
                    match_ddb = context_code_db[match_file][match_name]
                    _add_link(
                        callgraph,
                        match_ddb,
                        file_orig,
                        match_file,
                        func_orig,
                        match_name,
                        type="parent",
                    )
                    report["parents"]["guessed"].append(f"{parent_name}->{match_name}")
                else:
                    report["parents"]["missed"].append(f"{parent_name}")

            for called_name in func_db["callables"]:
                #  _,match_name2,match_file2 = _fetch_function_in_all_ddb(context_code_db, called_name, init_file_guess=file_orig)
                match_name, match_file = find_function_reference(
                    ref_list, called_name, file_orig
                )
                # if match_name != match_name2:
                #     logger.critical(f"mismatch \n{file_orig} : {called_name}\n{match_file} : {match_name} \n{match_file2} : {match_name2}")
                if match_name is not None:
                    match_ddb = context_code_db[match_file][match_name]
                    _add_link(
                        callgraph,
                        match_ddb,
                        file_orig,
                        match_file,
                        func_orig,
                        match_name,
                        type="call",
                    )
                    report["calls"]["guessed"].append(f"{called_name}->{match_name}")
                else:
                    report["calls"]["missed"].append(f"{called_name}->{match_name}")

    positive_i = len(report["contains"]["guessed"])
    negative_i = len(report["contains"]["missed"])
    positive_p = len(report["parents"]["guessed"])
    negative_p = len(report["parents"]["missed"])
    positive_c = len(report["calls"]["guessed"])
    negative_c = len(report["calls"]["missed"])

    logger.success(f" Found contains {log_line(positive_i, negative_i)}")
    logger.success(f" Found parents  {log_line(positive_p, negative_p)}")
    logger.success(f" Found callables{log_line(positive_c, negative_c)}")
    with open("Callgraph_report.yml", "w") as fout:
        safe_dump(report, fout)
    logger.info("Callgraph generated")
    return callgraph


def log_line(positive, negative):
    return (
        f"{positive} / {positive+negative} {int(positive/(positive+negative+EPS)*100)}%"
    )


def keys_with_max_values(d):
    """
    Returns the set of keys with the maximum values from the dictionary.
    If the maximum value is zero, returns an empty set.

    Parameters:
    d (dict): The dictionary with integer values.

    Returns:
    set: The set of keys with the maximum values, or an empty set if the maximum value is zero.

    Example:
    >>> keys_with_max_values({'a': 3, 'b': 5, 'c': 5, 'd': 2})
    {'b', 'c'}
    >>> keys_with_max_values({'a': 0, 'b': 0, 'c': 0})
    set()
    """
    if not d:
        return list()
    max_value = max(d.values())
    if max_value == 0:
        return list()
    return [k for k, v in d.items() if v == max_value]


def back_match(list1: list, list2: list) -> int:
    """
    Count the number of matching elements from the end of two lists.

    Args:
        list1 (list): The first list to compare.
        list2 (list): The second list to compare.

    Returns:
        int: The number of matching elements from the end of both lists.
    """
    count = 0

    # Compare elements from the end of the lists
    for elem1, elem2 in zip(reversed(list1), reversed(list2)):
        if elem1 == elem2:
            count += 1
        else:
            break

    return count


def end_match(references: List[str], suffix: str, rootless: bool = False) -> List[str]:
    """
    Finds and returns a list of strings from `references` that end with `str_`, with optional filtering based on `rootless` and `prefix`.

    Parameters:
    references (List[str]): A list of reference strings to be searched.
    str_ (str): The string to match at the end of each reference.
    rootless (bool): If True, strips the leading portion of `str_` before matching, starting from the first period character. Default is False.
    prefix (str): If provided, filters `references` to include only those that start with this prefix.

    Returns:
    List[str]: A list of strings from `references` that end with `str_` (or its rootless version if `rootless` is True).
    """

    # references = [ref for ref in references if ref.startswith(prefix)]

    items = suffix.split(".")
    if rootless:
        if len(items) == 1:
            return []
        items.pop(0)

    matches = {}
    for ref in references:
        if ref.endswith(items[-1]):
            if rootless and "." not in ref.split(":")[1]:
                continue
            matches[ref] = back_match(ref.split(":")[1].split("."), items)
    out = keys_with_max_values(matches)
    return out


def find_function_reference(
    ref_list: list, func_name: str, orig_file: str
) -> (str, str):

    matchs = end_match(ref_list, suffix=func_name)
    if not matchs:
        matchs = end_match(ref_list, suffix=func_name, rootless=True)

    if matchs:
        # logger.success(f"Reference found {matchs} <= {func_name} ")
        i_match = 0
        for i_m, match in enumerate(matchs):
            if match.startswith(orig_file):
                i_match = i_m
                break
            if len(match) < len(matchs[i_match]):
                i_match = i_m

        fileref, funcref = matchs[i_match].split(":")
        return funcref, fileref
    # logger.warning(f"Ref. to {func_name} not found")
    return None, None


def _add_node(callgraph: nx.DiGraph, file_: str, func_: str, db_by_func: dict):
    callgraph.add_node(
        f"{file_}:{func_}", **db_by_func, filename=file_, lang=_cast_lang(file_)
    )


def _add_link(
    callgraph: nx.DiGraph,  # the callgraph
    db_by_func: dict,  # the func tree ddb for one file
    file_orig: str,  # the origin func filename
    file_target: str,  # the target func filename
    func_orig: str,  # the origin func name
    func_target: str,  # the target func
    type: str = None,
):
    """Add a link in the graph"""

    # for func_target_full, func_db in db_by_file.items():
    #     # test if a fiunc_name matches the call. if yes add the node and the edge
    #     #if _longest_match(func_target_full, func_target):  # pas necessaire
    if f"{file_target}:{func_target}" not in callgraph.nodes:
        # callgraph.add_node(
        #     f"{file_target}:{func_target}", **db_by_func, filename=file_orig, lang=_cast_lang(file_orig)
        # )
        _add_node(callgraph, file_target, func_target, db_by_func)

    callgraph.add_edge(
        f"{file_orig}:{func_orig}",
        f"{file_target}:{func_target}",
        type=type,
    )
    return


def _cast_lang(filename: str):

    _, ext = os.path.splitext(filename)
    if ext in (".f", ".F", ".f77", ".f90", ".F77", ".F90"):
        lang = "fortran"
    elif ext in (".c", ".cpp", ".cc"):
        lang = "cpp"
    elif ext in (".py"):
        lang = "python"
    elif ext in (".h", ".hpp"):
        lang = "header"
    else:
        logger.critical(f"extension not understood {ext}")
        lang = "other"

    return lang


# def _try_add_callable_all(
#         callgraph:nx.DiGraph,
#         full_context_code_db:dict,# the func tree ddb for all files
#         file_orig:str,
#         func_orig:str,
#         func_target:str
#     )-> bool:
#     """Try to add a callable if it is in the context of the same file"""
#     added = False
#     for file_target, db_by_file in full_context_code_db.items():

#         # for ctxt_func_name, func_db in ctxt_file_db.items():
#         #     if  _longest_match(ctxt_func_name, call):
#         #         if (f"{ctxt_filename}:{ctxt_func_name}"not in callgraph.nodes):
#         #             callgraph.add_node(
#         #                 f"{ctxt_filename}:{ctxt_func_name}",**func_db,
#         #             )
#         #         callgraph.add_edge(
#         #             f"{filename}:{func_name}",
#         #             f"{ctxt_filename}:{ctxt_func_name}",
#         #         )
#         #         break
#         added = _add_link(
#             callgraph ,
#             db_by_file,
#             file_orig,
#             file_target,
#             func_orig,
#             func_target
#         )
#         if added:
#             break

#     return added


# def _fetch_function_in_all_ddb(allfiles_ddb:dict, func_name:str, init_file_guess:str=None) -> (dict, str, str):

#     all_filenames= list(allfiles_ddb.keys())

#     if init_file_guess is not None:
#         all_filenames = [init_file_guess] + all_filenames
#     for _file in  all_filenames: # search parent anywhere in the code
#         db_by_file = allfiles_ddb[_file]
#         match_ddb, match_name = _fetch_function_in_file_ddb(db_by_file, func_name)
#         if match_name is not None:
#             match_file=_file

#             return match_ddb, match_name, match_file

#     #logger.warning(f"Ref. to {func_name} not found")
#     return None,None,None

# def _fetch_function_in_file_ddb(file_ddb:dict, func_name:str) -> (dict, str):
#     for _func,_db_func in file_ddb.items():
#         if _longest_match(_func,func_name) :
#             match_name=_func
#             match_ddb=_db_func


#             #logger.success(f"Parent {match_name}  found")
#             return match_ddb, match_name

#     #logger.warning(f"Parent {func_name} not found")
#     return None,None

# def _longest_match(ctxt_func_name:str,call_func:str)->bool:
#     """Search for the longest match in the functions"""

#     try:
#         if ctxt_func_name.split(".")[-4:] == call_func.split(".") :
#             return True
#     except IndexError:
#         pass

#     try:
#         if ctxt_func_name.split(".")[-3:] == call_func.split(".") :
#             return True
#     except IndexError:
#         pass

#     try:
#         if ctxt_func_name.split(".")[-2:] == call_func.split(".") :
#             return True
#     except IndexError:
#         pass

#     if ctxt_func_name.split(".")[-1] == call_func :
#         return True


#     return False
