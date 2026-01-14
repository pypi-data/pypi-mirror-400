"""Network X utils to clean graphs"""

import fnmatch
import networkx as nx
from loguru import logger


def get_maingraph(ntx: nx.DiGraph) -> nx.DiGraph:
    """
    Extract one graph from a disconnected graph
    Args:
        ntx (obj): ntx (obj): networkX DiGraph

    Returns:
        ntx (obj): networkX DiGraph without single nodes

    :

    1->2->3          5->6->7
       v
       4

    gives

    1->2->3
       v
       4

    """
    u_ntx = nx.to_undirected(ntx)

    largest_cc = max(nx.connected_components(u_ntx), key=len)

    to_remove = []
    for node in ntx.nodes:
        if node not in largest_cc:
            to_remove.append(node)

    print(f"Main graph purge {len(to_remove)}")
    nt_out = ntx.copy()
    for node in to_remove:
        nt_out.remove_node(node)
    return nt_out


def get_subgraph(ntx: nx.DiGraph, root: str, radius: int = 2) -> nx.DiGraph:
    """
    Extract one graph from a disconnected graph
    Args:
        ntx (obj): ntx (obj): networkX DiGraph

    Returns:
        ntx (obj): networkX DiGraph without single nodes

    :

    a1->a2->a3          b5->b6->b7
       v
       a4

    with "b6" gives

    b5->b6->b7
    """
    logger.info(f"Getting subgraph from node {root}")
    subgraph = nx.ego_graph(ntx, root, radius=radius, undirected=True).copy()
    return subgraph


def remove_by_patterns(
    ntx: nx.DiGraph, remove_patterns: list = None, remove_descendants: bool = False
) -> nx.DiGraph:
    """
    Remove parts of the graph

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        remove_patterns (list): List of patterns to match in nodes name

    Returns:
        ntx (obj): networkX DiGraph without nodes matching the pattern

    :

    a1->a2->a3          b5->b6->b7
       v
       a4

    with ["a*", "b5"] gives

    b6->b7
    """
    logger.info(f"Removing by patterns.")
    nt_out = ntx.copy()

    to_remove = []
    for pattern in remove_patterns:
        matches = fnmatch.filter(ntx.nodes.keys(), pattern)
        descendants_list = []

        if remove_descendants:
            for node in matches:
                descendants_list.extend(nx.descendants(ntx, node))

        pattern_list = list(set(matches + descendants_list))
        logger.info(
            f"  {pattern}: {len(matches)} matchs and {len(descendants_list)} descendants"
        )
        to_remove.extend(pattern_list)

    to_remove = set(to_remove)
    logger.info(f"    {len(to_remove)} nodes removed by patterns")
    for node in set(to_remove):
        nt_out.remove_node(node)

    return nt_out


def soften_by_patterns(ntx: nx.DiGraph, soften_patterns: list = []) -> nx.DiGraph:
    """
    Add a soften attribut to parts of the graph

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        soften_patterns (list): List of patterns to match in nodes name

    Returns:
        ntx (obj): networkX DiGraph with soften nodes by pattern
    """
    logger.info(f"Softening by patterns {' ; '.join(soften_patterns)}")

    nt_out = ntx.copy()

    def to_soften(name):
        for pattern in soften_patterns:
            if fnmatch.filter([name], pattern):
                return True
        return False

    for node in ntx.nodes:
        if to_soften(node):
            nt_out.nodes[node]["soften"] = True

    return nt_out


def remove_hyperconnect(ntx: nx.DiGraph, treshold: int = 5) -> nx.DiGraph:
    """
    Remove nodes when there are  many predecessors and no successor

    Args:
        ntx (obj): ntx (obj): networkX DiGraph

    Returns:
        ntx (obj): networkX DiGraph without hyperconnected nodes

    :
       a4
       v
    a1->a1<-a3          b5->b6->b7

    b5->b6->b7    a2 a3 a4
    """
    logger.info(f"Removing hyperconnected nodes, starting from {treshold} predecessors")

    nt_out = ntx.copy()
    to_remove = []
    for node in ntx.nodes:
        if len(list(ntx.predecessors(node))) >= treshold:
            to_remove.append(node)

    logger.info(f"    {len(to_remove)} nodes removed by hyperconnection")
    for node in to_remove:
        nt_out.remove_node(node)

    return nt_out


def remove_singles(ntx: nx.DiGraph) -> nx.DiGraph:
    """
    Remove nodes without ancestors or predecessors

    Args:
        ntx (obj): ntx (obj): networkX DiGraph

    Returns:
        ntx (obj): networkX DiGraph without single nodes
    """

    logger.info(f"Removing single nodes or self connected nodes")

    to_remove = []
    for node in ntx.nodes:
        if not list(ntx.predecessors(node)) and not list(
            ntx.successors(node)
        ):  # unconnected node
            to_remove.append(node)
        if list(ntx.predecessors(node)) == [node] and list(ntx.successors(node)) == [
            node
        ]:  # self connected, isolated, node
            to_remove.append(node)

    logger.info(f"    {len(to_remove)} nodes removed by singularity or self connection")
    for node in to_remove:
        ntx.remove_node(node)
        # logger.info(f'    Single {node} removed')

    to_remove = []
    for edge in ntx.edges:
        if edge[0] == edge[1]:
            to_remove.append(edge)
    logger.info(f"    {len(to_remove)} edges removed by self connection")
    for edge in to_remove:
        ntx.remove_edge(edge[0], edge[1])

    return ntx


def merge_node(ntx: nx.DiGraph, node: str, mergeup=True) -> nx.DiGraph:
    """
    Remove nodes without ancestors or predecessors

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        node  (str): ntx (obj): networkX node ref

    Returns:
        ntx (obj): networkX DiGraph without single nodes
    """
    logger.info(f"Merge node")

    if mergeup:
        logger.info(f"Collapsing node {node} upward")
        nodes2 = ntx.predecessors(node)
    else:
        logger.info(f"Collapsing node {node} downward")
        nodes2 = ntx.successors(node)

    nt_out = ntx.copy()
    for node2 in nodes2:
        nt_out = nx.contracted_nodes(nt_out, node, node2, self_loops=False)

    return nt_out


def merge_links(ntx: nx.DiGraph, linktype: str) -> nx.DiGraph:
    """
    Remove nodes without ancestors or predecessors

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        node  (str): ntx (obj): networkX node ref

    Returns:
        ntx (obj): networkX DiGraph without single nodes
    """
    logger.info(f"Merge links {linktype}")

    to_remove = []

    for edge in ntx.edges:
        if ntx.edges[edge]["type"] == linktype:
            to_remove.append(edge)

    nt_out = ntx.copy()
    for u, v in to_remove:
        # logger.info(f"Collapsing {u,v} " )
        nt_out = nx.contracted_nodes(nt_out, u, v, self_loops=False)

    return nt_out


def cut_links(ntx: nx.DiGraph, linktype: str) -> nx.DiGraph:
    """
    Remove nodes without ancestors or predecessors

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        node  (str): ntx (obj): networkX node ref

    Returns:
        ntx (obj): networkX DiGraph without single nodes
    """
    logger.info(f"Cuts links {linktype}")

    to_remove = []

    for edge in ntx.edges:
        if ntx.edges[edge]["type"] == linktype:
            to_remove.append(edge)

    nt_out = ntx.copy()
    for u, v in to_remove:
        # logger.info(f"Collapsing {u,v} " )
        nt_out.remove_edge(u, v)

    logger.info(f"Removed {len(to_remove)} edges of type {linktype}")
    return nt_out


def get_root_from_tree(ntx: nx.DiGraph) -> str:
    """
    Return the root node. Fail if multiple roots on diffrent graphs or same graph

    Args:
        ntx (obj): networkX DiGraph

    Returns:
        root (str): Name of the root node

    :

    a1->a2->a3
       v
       a4

       returns a1

     a1->a2->a3     b1->b2->b3
       v               v
       a4              b4

       returns failure

    a1->a2<-a3
       v
       a4

       returns failure


    """
    (root,) = [node for node, degree in ntx.in_degree() if degree == 0]
    return root


def crop_leafs(ntx: nx.DiGraph, levels: int = 1) -> nx.DiGraph:
    """remove leafs from graph"""

    logger.info(f"Removing {levels} lowest levels")

    depth = compute_graph_leafness(ntx)

    removed_nodes = 0
    for node in depth:
        if not depth[node]:
            pass
        elif depth[node] <= levels:
            ntx.remove_node(node)
            removed_nodes += 1
    logger.info(f"    {removed_nodes} nodes removed by leaf cropping")
    return ntx


def compute_graph_depth(ntx: nx.DiGraph) -> dict:
    """Compute the level of each node with respect to the rootest ones"""
    logger.info("Computing depth (distance to root)")

    depth = {}
    for node in ntx.nodes:
        depth[node] = None

    def add_level_to_successors(ntx, depth, node, level):
        """RECURSIVE add a level to nodes from their predecessor"""
        for snode in ntx.successors(node):
            if depth[snode] is None:
                depth[snode] = level + 1
                add_level_to_successors(ntx, depth, snode, level + 1)

    nb_roots = 0
    for node in ntx.nodes:
        if depth[node] is None:
            if list(ntx.predecessors(node)) in ([], [node]):  # source nodes
                depth[node] = 1
                nb_roots += 1
                add_level_to_successors(ntx, depth, node, 1)

    logger.info(f"Found {nb_roots} roots in this graph")

    for node in ntx.nodes:
        if depth[node] == None:
            logger.warning(f"node {node} shows no depth -Circular dependencies?-")
            depth[node] = 1
    return depth


def compute_graph_leafness(ntx: nx.DiGraph) -> dict:
    """Compute the level of each node with respect to the leafest ones"""
    logger.info("Computing leafness (distance to leaves)")

    depth = {}
    for node in ntx.nodes:
        depth[node] = None

    def add_level_to_predecessors(ntx, depth, node, level):
        for snode in ntx.predecessors(node):
            if depth[snode] is None:
                depth[snode] = level + 1
                add_level_to_predecessors(ntx, depth, snode, level + 1)

    nb_leafs = 0
    for node in ntx.nodes:
        if depth[node] is None:
            if list(ntx.successors(node)) in ([], [node]):  # source nodes
                depth[node] = 1
                nb_leafs += 1
                add_level_to_predecessors(ntx, depth, node, 1)

    logger.info(f"Found {nb_leafs} leafs in this graph")
    return depth


def compute_graph_relative_level(ntx: nx.DiGraph) -> dict:
    """
    Compute the relative level of the graph.
    Leaves are at 1 and higher functions are at 0 (main functions)

    Args:
        ntx (nx.DiGraph): networkX DiGraph

    Returns:
        dict: node name with relative level computed
    """
    leafness = compute_graph_leafness(ntx)
    depth = compute_graph_depth(ntx)
    rlevel = {}
    for node_name in leafness:
        rlevel[node_name] = (depth[node_name] - 1) / (
            depth[node_name] + leafness[node_name] - 2
        )

    return rlevel


def compute_graph_line_contamination(ntx: nx.DiGraph) -> dict:
    contamination = {}

    # Identify cycles
    sccs = list(nx.strongly_connected_components(ntx))
    node_to_scc = {}
    for idx, scc in enumerate(sccs):
        for node in scc:
            node_to_scc[node] = idx

    # Build condensed graph
    condensed = nx.DiGraph()
    for idx in range(len(sccs)):
        condensed.add_node(idx)

    for node_from, node_to in ntx.edges():
        scc_u = node_to_scc[node_from]
        scc_v = node_to_scc[node_to]
        if scc_u != scc_v:
            condensed.add_edge(scc_u, scc_v)

    # Compute value on condensed graph
    scc_contamination = {}

    def compute_scc_total(scc_id):
        if scc_id in scc_contamination:
            return scc_contamination[scc_id]

        # Initial contamination -> Sum of NLOC of cycle
        total = sum(ntx.nodes[node].get("NLOC", 0) for node in sccs[scc_id])

        for child_scc in condensed.successors(scc_id):
            total += compute_scc_total(child_scc)

        scc_contamination[scc_id] = total
        return total

    for scc_id in nx.topological_sort(condensed):
        compute_scc_total(scc_id)

    # Reassign values from cycle
    for node in ntx.nodes():
        scc_id = node_to_scc[node]
        contamination[node] = scc_contamination[scc_id]

    return contamination
