"""Module to show a a networkX directed graph with pyvis"""

import graphviz
import networkx as nx
from maraudersmap.colors_utils import darken_color
from loguru import logger

def ntw_graphiz(
    ntx: nx.DiGraph,
    refsize: int = 3,
    graph_engine: str = "dot",
    view: bool = True,
    file_prefix:str = "unnamed"
):
    """
    Convert a networkx to a pyvis html File

    ntx: a Network X directed Graph
    size: reference size in pixel, use this to scale up everything
    loosen: [-] mass divided:
        if increased, makes nodes more losely coupled during interactions
    title: used to create the file
    physics_panel: if true add physic panel to the HTML
    """

    def _encode_names(name):
        """graphviz is using  ':'  in a peculiar way..."""
        
        label = name.replace(":",r"\n")  
        return label  

    gfz = graphviz.Digraph("dummy", engine=graph_engine)

    for node in ntx.nodes:
        comment = ntx.nodes[node].get("comment", None)
        label = _encode_names(node)
        color = ntx.nodes[node].get("color", "khaki")
        node_size = ntx.nodes[node].get("size", refsize)
        size = 0.05 * refsize * (node_size / refsize) ** 0.5
        pencolor = darken_color(color)
        
        msg = label
        if comment is not None:
            msg +=r"\n"+comment
        gfz.node(
            label,
            label=msg,
            style="filled",
            fillcolor=color,
            color=pencolor,
            shape="record",
            penwidth=str(size),
        )

    for link in ntx.edges:
        style = "solid"
        edge_size = ntx.edges[link].get("size", refsize)
        color =  ntx.nodes[link[0]].get("color", None)
        size = 0.5 * refsize * (edge_size / refsize) ** 0.5
        gfz.edge(
            _encode_names(link[0]),
            _encode_names(link[1]),
            style=style, color=color, penwidth=str(size))

    gfz.render(file_prefix, format="svg", cleanup=True, view=view)
    file_ = f"{file_prefix}.svg"
    print("Rendered with graphvis in your browser")
    print(f"Output written to {file_}")
    return file_
