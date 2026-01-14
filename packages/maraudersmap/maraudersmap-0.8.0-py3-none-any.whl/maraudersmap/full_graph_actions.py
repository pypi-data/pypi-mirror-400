import os, webbrowser
import fnmatch
import networkx as nx
import fnmatch
from copy import deepcopy
import numpy as np
from matplotlib import colors as mplcolors
from loguru import logger
from typing import List, Tuple
from tucan.string_utils import get_common_root_index

from maraudersmap.nx_utils import (
    remove_by_patterns,
    remove_hyperconnect,
    remove_singles,
    get_subgraph,
    merge_links,
    cut_links,
    compute_graph_depth,
    compute_graph_relative_level,
    compute_graph_line_contamination
)

from maraudersmap.show_pyvis import showgraph_pyvis
from maraudersmap.show_plotly import dash_app_autoload,dash_app_noload
from maraudersmap.show_pyplot import ntw_pyplot2d
from maraudersmap.show_graphviz import ntw_graphiz
from maraudersmap.stats_mvp import ntw_stats_mvp

from maraudersmap.colors_utils import find_color,colorscale_hex,colorscale_legend


def show_graph(
        cgs_nx:nx.DiGraph,
        backend:str="pyvis",
        color:str="type",
        patterns:str=None,
        remove_patterns:list=None,
        hyperconnect:int=10, 
        subgraph_roots:list=None,
        load:bool=False,
        prefix: str="unnamed",
        grep_patterns=None,
        rootpath:str=None
    ):
    file_prefix = f"mmap_"+prefix
    
    # ovverride in case of MVP vision
    if backend == "mvp":
        cgs_nx = reduce_graph_names(cgs_nx)
        ntw_stats_mvp(cgs_nx,file_prefix=file_prefix)
        return
       
    cgs_nx = clean_graph(
        cgs_nx,
        remove_patterns=remove_patterns,
        hyperconnect=hyperconnect,
        subgraph_roots=subgraph_roots,
    )

    if color == "grep":
        cgs_nx = grep_in_graph(cgs_nx,rootpath,grep_patterns)

    cgs_nx = reduce_graph_names(cgs_nx)

    cgs_nx, legend = color_nodes(cgs_nx, color, color_pattern=patterns, grep_patterns=grep_patterns)


    if backend == "pyvis":
        showgraph_pyvis(cgs_nx, legend, file_prefix)
        if load:
            file_url = 'file://' + os.path.realpath(file_prefix+".html")
            webbrowser.open(file_url)
    elif backend == "plotly":
        if load:
            dash_app_autoload(cgs_nx)
        else:
            app = dash_app_noload(cgs_nx)
            app.run_server(debug=True, use_reloader=True)
            logger.info("App created, Please log yourself to the url:\nhttp://127.0.0.1:8050")
    elif backend == "pyplot":
        ntw_pyplot2d(cgs_nx,file_prefix=file_prefix)
    elif backend == "pydot":
        ntw_graphiz(cgs_nx, view=load,file_prefix=file_prefix)
    else:
        logger.error(f"Backend {backend} not understood")


def grep_in_graph(nxdata: nx.DiGraph, rootpath:str,grep_patterns:dict)-> nx.DiGraph:
    #regex_yellow = re.compile(r"!$OPENACC")
    #regex_blue = re.compile(r"nlen")

    patblue = grep_patterns["blue"]
    patyellow= grep_patterns["yellow"]
    
    
    for node in nxdata.nodes:
        
        nxdata.nodes[node]["grep_yellow"]=False
        nxdata.nodes[node]["grep_blue"]=False
        
        lines = nxdata.nodes[node].get("lines", None)
        if lines is None:
            nxdata.nodes[node]["grep_yellow"]=None
            nxdata.nodes[node]["grep_blue"]=None
            continue
        
        start_line,end_line = lines
        _fname = rootpath+"/"+node.split(":")[0]

        with open(_fname, 'r') as file:
            for current_line_number, line in enumerate(file, start=1):
                if current_line_number > end_line:
                    break
                if start_line <= current_line_number:
                    if line_matches_any(line,patyellow):
                    #if regex_yellow.search(line):
                        nxdata.nodes[node]["grep_yellow"]=True
                    if line_matches_any(line,patblue):
                        nxdata.nodes[node]["grep_blue"]=True

    return nxdata


def reduce_graph_names(nxdata: nx.DiGraph)-> nx.DiGraph:
    root_idx = get_common_root_index(list(nxdata.nodes))
    if root_idx == -1:
        return nxdata
    
    relabel_dict = {node: node[root_idx:] for node in nxdata.nodes}
    nxdata = nx.relabel_nodes(nxdata, relabel_dict)
    return nxdata

def complete_callgraph_data(nxdata: nx.DiGraph, merge_containers:bool=False,nocalls:bool=False):
    if merge_containers:
        nxdata = merge_links(nxdata, "contain")        
    if nocalls:
        nxdata = cut_links(nxdata, "call")

    vals = {node:nxdata.nodes[node].get("NLOC", 1)*0.5 for node in nxdata.nodes}
    nx.set_node_attributes(nxdata,vals,"size")
    return nxdata

def complete_importgraph_data(nxdata: nx.DiGraph, merge_containers:bool=False,nocalls:bool=False):
    vals = {node:nxdata.nodes[node]["NLOC"]*0.5 for node in nxdata.nodes}
    nx.set_node_attributes(nxdata,vals,"size")
    return nxdata

def complete_valgrind_data(nxdata: nx.DiGraph):
    vals = {node: f'{nxdata.nodes[node]["fraction"]}%' for node in nxdata.nodes}
    nx.set_node_attributes(nxdata,vals,"comment")
    vals = {node:nxdata.nodes[node]["fraction"]*0.5 for node in nxdata.nodes}
    nx.set_node_attributes(nxdata,vals,"size")

    return nxdata


def clean_graph(
    nxdata: nx.DiGraph,
    remove_patterns: list = None,
    hyperconnect: int = None,
    subgraph_roots:list =None,
) -> nx.DiGraph:
    """
    Performs the diverse cleanings of the graph

    Args:
        ntx (obj): ntx (obj): networkX DiGraph
        remove_patterns (list): List of patterns to match in nodes name
        soften_patterns (list): List of patterns to match in nodes name
        hyperconnect (int): number of edges allowed for nodes

    Returns:
        ntx (obj): networkX DiGraph cleaned

    """

    def log_graph_size():
        logger.info(f"{nxdata.number_of_nodes()} nodes / {nxdata.number_of_edges()} edges")

    logger.info("Start filtering graph")

    log_graph_size()
    if subgraph_roots is not None:
        logger.info(f"Limiting to subgraph roots {subgraph_roots}")
        new_data = nx.DiGraph()
        for pattern in subgraph_roots:
            results =  fnmatch.filter(nxdata.nodes.keys(), pattern)
            if len(results)>1:
                logger.warning(f"subgraph_roots pattern {pattern} yielded several results")
                for res in results:
                    logger.warning(f" -{res}")
                logger.warning(f"Aborting...")
                return None
                
            elif len(results)==0:
                logger.warning(f"subgraph_roots pattern {pattern} yielded no results,{' '.join(results)} skipping...")
            else:
                new_data =nx.compose(new_data, get_subgraph(nxdata,results[0]))
        nxdata=new_data
        log_graph_size()
    
    # if prune_lower_levels is not None:
    #     nxdata = crop_leafs(nxdata, levels=prune_lower_levels)
    #     log_graph_size()
    
    if hyperconnect is not None:
        logger.info(f"Remove hyperconnected roots starting at  {hyperconnect}")
        
        nxdata = remove_hyperconnect(nxdata, hyperconnect)
        log_graph_size()
    
    if remove_patterns is not None :
        logger.info(f"Remove patterns: {remove_patterns}")
        nxdata = remove_by_patterns(nxdata, remove_patterns)
        log_graph_size()
    
    logger.info(f"Remove singles")
    nxdata = remove_singles(nxdata)
    log_graph_size()

    logger.info(
        "After cleaning :"
        + str(nxdata.number_of_nodes())
        + " nodes/"
        + str(nxdata.number_of_edges())
        + " edges"
    )
    if nxdata.number_of_nodes() == 0:
        msgerr = "Filtering removed all nodes, aborting"
        logger.critical(msgerr)
        raise RuntimeError(msgerr)
    
    return nxdata


def color_nodes_by_quantity(
    graph: nx.DiGraph,
    min_lvl: int,
    max_lvl: int,
    color_by: str,
    color_map: str = "rainbow_PuRd",
    log_scale: bool = True,
) -> dict:
    """
    Add hexadecimal color to networkX graph according to a selected data

    Args:
        graph (obj): NetworkX graph
        min_lvl (int): Lower bound
        max_lvl (int): Upper bound
        color_by (str): Name of the data to look for in graph
        color_map (str): Name of the Paul Tol's color map desired
        log_scale (bool): switch to log_scale

    Returns:
        colored_graph (obj) : Update the color key in the graph nodes dict
        legend (dict): Name and color for legend
    """
    colored_graph = deepcopy(graph)
    for node in colored_graph.nodes:
        lvl = colored_graph.nodes[node].get(color_by, None)
        color = colorscale_hex(
            lvl, min_lvl, max_lvl, color_map=color_map, log_scale=log_scale
        )
        colored_graph.nodes[node]["color"] = color

    legend = {}
    color_lvl = np.linspace(min_lvl, max_lvl, 5)

    for lvl in color_lvl:
        if min_lvl != 0 and max_lvl != 1:
            lvl = round(lvl)
        color_rgb = colorscale_hex(
            lvl, min_lvl, max_lvl, color_map=color_map, log_scale=log_scale
        )
        legend[str(lvl)] = color

    return colored_graph, legend




def color_nodes(cgs_nx:nx.DiGraph, color_scheme:str, color_pattern:dict=None, grep_patterns:dict=None):

    if color_scheme == "type":
        cgs_nx, legend = color_nodes_by_type(cgs_nx)
    elif color_scheme == "lang":
        cgs_nx, legend = color_nodes_by_lang(cgs_nx)
    elif color_scheme == "cplx":
        cgs_nx, legend = color_nodes_by_cplx(cgs_nx)
    elif color_scheme == "lvl":
        cgs_nx, legend = color_nodes_by_lvl(cgs_nx)
    elif color_scheme == "rlvl":
        cgs_nx, legend = color_nodes_by_rlvl(cgs_nx)
    elif color_scheme == "conta":
        cgs_nx, legend = color_nodes_by_contamination(cgs_nx)
    elif color_scheme == "ptn":
        if color_pattern==None:
            raise RuntimeWarning("Color pattern not provided, exiting...")
        cgs_nx, legend = color_nodes_by_pattern(cgs_nx, color_pattern)
    elif color_scheme == "grep":
        if grep_patterns==None:
            raise RuntimeWarning("Grep pattern not provided, exiting...")
        cgs_nx, legend = color_nodes_by_grep(cgs_nx, grep_patterns)
    else:
        raise ValueError("Color scheme not understood...")
    
    return cgs_nx,legend

def color_nodes_by_type(graph: nx.DiGraph):
    colored_graph = deepcopy(graph)

    COLORS_TYPE={
        "blue": ["function", "def", "int", "double", "char","float"],
        "teal": ["subroutine", "void"],
        "forestgreen": ["method"],
        "limegreen": ["procedure", "interface"],
        "darkgrey": ["module", "namespace"],
        "khaki": ["object", "class"],
        "orange": ["type", "struct","enum","class"],
        "red": ["template"],
        "pink": ["pointer"],
        "lightgrey": ["file"],
        "grey": ["program"],
        
    }

    unrolled_colors = {}
    legend = {}
    for color,items in COLORS_TYPE.items():
        legend[items[0]]=color
        for item in items:
            unrolled_colors[item]=color

    for node in colored_graph.nodes():
        if "type" not in colored_graph.nodes[node]:
            logger.warning(f"No type for {node}")
            type_=None
        else:
            type_ = colored_graph.nodes[node]["type"]
        if type_ not in unrolled_colors:
            logger.warning(f"Type '{type_}' not colored...")
        colored_graph.nodes[node]["color"] = unrolled_colors.get(type_, "black")   
    return colored_graph,legend


def color_nodes_by_lang(graph: nx.DiGraph):
    colored_graph = deepcopy(graph)

    COLORS_LANG ={
        "python": "yellow",
        "fortran": "green",
        "cpp": "blue",
        "header": "teal",
        "other": "grey"
    }
    for node in colored_graph.nodes():
        if "lang" not in colored_graph.nodes[node]:
            logger.warning(f"No lang for {node}")
            lang_=None
        else:
            lang_= colored_graph.nodes[node]["lang"]
        colored_graph.nodes[node]["color"] = mplcolors.to_hex(COLORS_LANG.get(lang_, "black"))
    return colored_graph,COLORS_LANG

def color_nodes_by_contamination(graph: nx.DiGraph)->Tuple[nx.DiGraph,dict]:
    colored_graph = deepcopy(graph)
    depth = compute_graph_line_contamination(colored_graph)

    total = sum(graph.nodes[node].get("NLOC", 0) for node in graph.nodes)

    cmap = "iridescent"
    min_lvl = 0
    max_lvl = total
    legend = colorscale_legend(min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap,levels=10)
    for node in colored_graph.nodes():
        color = colorscale_hex(depth[node],min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap) 
        colored_graph.nodes[node]["color"] = color
    return colored_graph,legend

def color_nodes_by_rlvl(graph: nx.DiGraph)->Tuple[nx.DiGraph,dict]:
    colored_graph = deepcopy(graph)
    depth = compute_graph_relative_level(colored_graph)
    cmap = "iridescent"
    min_lvl = 0
    max_lvl = 1
    legend = colorscale_legend(min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap)
    for node in colored_graph.nodes():
        color = colorscale_hex(depth[node],min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap) 
        colored_graph.nodes[node]["color"] = color
    return colored_graph,legend

def color_nodes_by_lvl(graph: nx.DiGraph):
    colored_graph = deepcopy(graph)

    depth = compute_graph_depth(colored_graph)
    cmap = "rainbow_discrete"
    min_lvl = 1
    max_lvl = 12
    legend = colorscale_legend(min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap)
    for node in colored_graph.nodes():
        color = colorscale_hex(depth[node],min_lvl=min_lvl,max_lvl=max_lvl, log_scale=False,color_map=cmap) 
        colored_graph.nodes[node]["color"] = color
    return colored_graph,legend

def color_nodes_by_cplx(graph: nx.DiGraph):
    colored_graph = deepcopy(graph)

    cmap = "iridescent"
    min_lvl = 1.
    max_lvl = 100.
    legend = colorscale_legend(min_lvl=min_lvl,max_lvl=max_lvl, log_scale=True,color_map=cmap, levels=12)
    for node in colored_graph.nodes():
        color = colorscale_hex(colored_graph.nodes[node]["CCN"],min_lvl=min_lvl,max_lvl=max_lvl, log_scale=True,color_map=cmap) 
        colored_graph.nodes[node]["color"] = color
    return colored_graph,legend

def color_nodes_by_pattern(graph: nx.DiGraph, color_rules: dict):
    """
    Add  color to networkX graph according to selected patterns

    Args:
        graph (obj): NetworkX graph
        color_rules (dict): Patterns as key, color as value

    Returns:
        colored_graph (obj) : Update the color key in the graph nodes dict
        legend (dict): Name and color for legend
    """
    if color_rules is None:
        raise RuntimeError("Colors rules are missing...")

    colored_graph = deepcopy(graph)
    for node in colored_graph.nodes():
        #color = colored_graph.nodes[node].get("color", None)
        #if not color:                               # do not get why 
        color = find_color(node, color_rules)
        colored_graph.nodes[node]["color"] = color

    legend = build_hex_color_rules(color_rules)

    return colored_graph, legend




def color_nodes_by_grep(graph: nx.DiGraph, grep_patterns: dict):
    """
    Add  color to networkX graph according to selected patterns

    Args:
        graph (obj): NetworkX graph
        color_rules (dict): Patterns as key, color as value

    Returns:
        colored_graph (obj) : Update the color key in the graph nodes dict
        legend (dict): Name and color for legend
    """
    
    colored_graph = deepcopy(graph)
    for node in colored_graph.nodes():
        yellow =  colored_graph.nodes[node].get("grep_yellow", None)
        blue = colored_graph.nodes[node].get("grep_blue", None)
        
        color = "lightgrey"
        if yellow is None:
            color = "black"
        else:     
            if yellow:
                color = "gold" 
            if blue:
                color = "blue"
            if yellow and blue:
                color = "green"
        colored_graph.nodes[node]["color"] = color

    ylkey = "|".join(grep_patterns["yellow"])
    blkey = "|".join(grep_patterns["blue"])
    legend = {
        "missed": "black",
        "no match": "grey",
        ylkey : "gold",
        blkey : "blue",
        "both" : "green",
    }
    legend2={}
    for key, color in legend.items():
        legend2[key.replace(" ","_")] = mplcolors.to_hex(color)

    return colored_graph, legend2


def line_matches_any(line, patterns):
    """
    Check if a line matches any of the given wildcard patterns.

    Args:
        line (str): The line to check.
        patterns (list): List of wildcard patterns.

    Returns:
        bool: True if the line matches any pattern, False otherwise.
    """
    return any(fnmatch.fnmatch(line, pattern) for pattern in patterns)


def build_hex_color_rules(color_rules: dict) -> dict:
    """
    Convert a user-defined color scheme (`color_rules`) to a standardized
    hexadecimal color legend.

    Raises an error if any invalid color is found.

    Args:
        color_rules (dict): Patterns as key, color as value

    Returns:
        dict: Hexadecimal color legend : patterns as key, color as value.
    """
    legend = {}
    for key, color in color_rules.items():
        legend[key] = mplcolors.to_hex(color)
    return legend
