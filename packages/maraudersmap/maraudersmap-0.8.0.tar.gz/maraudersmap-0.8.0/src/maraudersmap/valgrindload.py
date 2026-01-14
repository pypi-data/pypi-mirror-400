from loguru import logger
from typing import List, Tuple
import networkx as nx
from tucan.string_utils import get_common_root_index


def read_valgrind_file(filename) -> nx.DiGraph:
    """Load a valgrind data into a networkX digraph

    use: callgrind_annotate --tree=both --auto=yes  --inclusive=yes --context=2
     - tree both to get also the edges
     - with context (to get where were the sources)
     - reduce context for a lighter version
     - inclusive
    """
    with open(filename, "r") as fin:
        data = fin.readlines()
    return parse_valgrind_data(data)


def parse_valgrind_data(
    valgrind_lines: List[str], only_sources: str = bool, skip_negligible: bool = True
) -> nx.DiGraph:
    root_sources = find_root_sources(valgrind_lines)

    body = load_tree_lines(valgrind_lines)
    body = reorder_body(body)
    ntx = build_graph(body, root_sources, only_sources, skip_negligible)

    return ntx


def valgrind_simplify_names(ntx: nx.DiGraph) -> nx.DiGraph:
    """Simplify nodes"""
    to_remove = []
    remap = {}
    for node in ntx.nodes:
        if node.startswith("???"):
            to_remove.append(node)
            continue
        remap[node] = simplernode(node)

    for node in to_remove:
        ntx.remove_node(node)
    ntx = nx.relabel_nodes(ntx, remap)
    return ntx


def simplernode(str_: str) -> str:
    strips = ["'2", "_"]
    for ptn in strips:
        str_ = str_.rstrip(ptn)
    str_ = str_.replace("MOD_", "")  # modules
    str_ = str_.replace("mp_", "")  # modules
    str_ = str_.replace("__", "")  # modules
    return str_


def get_potential_nodes(ntx: nx.DiGraph) -> List[str]:
    """Identify potential nodes to color in the callgraph"""
    list_nodes = []
    for node in ntx.nodes:
        if node.startswith("???"):
            continue
        nodename = node.rstrip("'2").rstrip("_")
        list_nodes.append(nodename)
    return list_nodes


def find_root_sources(valgrind_lines: List[str]) -> List[str]:
    annotate_files = []
    for line in valgrind_lines:
        if line.startswith("-- Auto-annotated source"):
            annotate_files.append(line.split(":")[-1].strip())

    if not (annotate_files):
        msgerr = "No parsable Valgrind lines in this file."
        logger.critical(msgerr)
        raise RuntimeError(msgerr)

    root_sources = annotate_files[0][: get_common_root_index(annotate_files)]
    logger.info(f"Root sources found : {root_sources}")

    return root_sources


def load_tree_lines(valgrind_lines: List[str]) -> str:
    """extract the body of line limited to tree"""
    reading = False
    body = []
    for line in valgrind_lines:
        if line.startswith("--"):
            continue
        if line.startswith("Ir"):
            if "file:function" in line:
                reading = True
            else:
                reading = False
            continue
        if reading:
            body.append(line)
    return body


def reorder_body(body: List[str]) -> List[str]:
    """put caller lines after focus lines"""
    new_body = []
    caller_list = []
    for line in body:
        if line.strip() == "":
            continue

        kind = line.replace("(", "").replace(")", "").split()[2]
        if kind == "<":
            caller_list.append(line)
        elif kind == "*":
            new_body.append(line)
            new_body.extend(caller_list)
            caller_list = []
        elif kind == ">":
            new_body.append(line)
        else:
            msg_err = """
    None of *,>,< were found in your valgrind data.
    Are you sure you used --tree=both  option for callgrind_annotate?
"""
            raise RuntimeError(msg_err)

    # print("\n".join(new_body))

    return new_body


def build_graph(
    body: List[str], root_sources: str, only_sources:bool, skip_negligible: bool
) -> nx.DiGraph:
    """Convert valgrind data on tree into nx Directed graph"""
    ntx = nx.DiGraph()
    anchor = None

    # Detect nodes and called edges
    for line in body:
        # logger.warning(f"{anchor}")
        # logger.info(f"{line}")

        try:
            (
                counts,
                fraction,
                kind,
                file,
                function,
                repeat,
                source,
            ) = parse_valgrind_line(line)
        except ValueError:
            continue

        nodename = node_name(file, function, root_sources)
        
        if nodename.startswith("???"):
            continue
        if only_sources and nodename.startswith("!!!"):
            continue

        if kind == "*":
            anchor = nodename
            keep_this_node = True
           
           
            
            # if root_sources != "":
            #     if not nodename.startswith(root_sources):
            #         logger.warning(f"Skipping non-source node  : {nodename}")
            #         keep_this_node = False
           
            if skip_negligible and fraction == 0:  # skip low impact files
                keep_this_node = False
                logger.warning(f"Skipping negligible node : {nodename}")

        if keep_this_node:
            if kind == "*":
                ntx.add_node(nodename, counts=counts, fraction=fraction, type="node")
            elif kind == ">":
                if skip_negligible and fraction == 0:
                    continue

                if nodename not in ntx.nodes:
                    ntx.add_node(
                        nodename, counts=counts, fraction=fraction, type="called"
                    )

                if nodename == anchor:
                    ntx.nodes[anchor]["counts"] -= counts
                    ntx.nodes[anchor]["fraction"] -= fraction
                # if "MAIN" in nodename:
                #     logger.critical(f"{anchor} -> {nodename}")
                #     exit()
                ntx.add_edge(anchor, nodename)

            elif kind == "<":
                if skip_negligible and fraction == 0:
                    continue
                if nodename not in ntx.nodes:
                    ntx.add_node(
                        nodename, counts=counts, fraction=fraction, type="calling"
                    )

                ntx.add_edge(nodename, anchor)

    return ntx


def node_name(file: str, function: str, root_sources: str) -> str:
    """Handle node name construction"""
    if file.startswith(root_sources):
        strt = len(root_sources)
        file = file[strt:]
    else:
        file = "!!!"+file

    return f"{file}:{function}"


def parse_valgrind_line(line: str) -> Tuple[int, float, str, str, int, str]:
    """Read data from a valgrind line about the tree"""

    line = line.replace("(below main)", "below_main")

    for char in "()%[]":
        line = line.replace(char, " ")
    for char in ",":
        line = line.replace(char, "")

    items = line.split()
    # remove the repeat element if existing
    if line.split()[-2].rstrip("x").isdigit():
        repeat = items.pop(-2)
    else:
        repeat = "1x"

    if len(items) == 5:
        counts, fraction, kind, filefun, source = items
    else:
        logger.info(f"Cannot parse line :{line}, skipping...")
        raise ValueError

    counts = int(counts)
    fraction = float(fraction)
    file, function = filefun.split(":")
    repeat = int(repeat.rstrip("x"))
    return counts, fraction, kind, file, function, repeat, source
