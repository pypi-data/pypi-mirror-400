"""Module to show a a networkX directed graph with pyvis"""



import networkx as nx
from pyvis.network import Network
from loguru import logger
#from maraudersmap.show_pyplot import fastplot



def showgraph_pyvis(nx_data, legend, prefix, writeondisc=True):
    """Show output file, default ouput is pyvis"""

    # with open(controlfile, "r") as fin:
    #     param = safe_load(fin)

    #footer_code = generate_html_footer(param["path"], param["remove_patterns"])
    ntw_pyvis(
        nx_data,
        legend,
        loosen=100,
        prefix=prefix,
        physics_panel=True,
        #footer_code=footer_code,
        writeondisc=writeondisc,
    )


def ntw_pyvis(
    ntx: nx.DiGraph,
    legend: dict,
    refsize=5,
    loosen=1,
    prefix: str = "nodes",
    physics_panel: bool = False,
    # footer_code: str = "",
    writeondisc=True,
):
    """
    Convert a networkx to a pyvis html File

    Args:
        ntx (obj): a Network X directed Graph
        legend (dict): Name of the filed / Value of complexity as key, color as value
        refsize (int): Node reference size
        loosen (int): [-] mass divided:
            if increased, makes nodes more losely coupled during interactions
        prefix (str): named used to create the file
        physics_panel (bool): if true add physic panel to the HTML
        footer_code (str): footer for the graph as str of html code to be put at the end of the file

    Returns:
        Dump the legend.html and the pyvis.html graph
    """
    # fastplot(ntx)
    nt = Network(width="1000px", height="1000px", directed=True)

    min_mass=1e9
    max_mass=0
    min_size=1e9
    max_size=0

    for node in ntx.nodes:
        node_size = ntx.nodes[node].get("size", refsize)
        node_comment = ntx.nodes[node].get("comment","")
        #node_soften = ntx.nodes[node].get("soften", False)
        #node_root = ntx.nodes[node].get("root", False)
        #node_analyzed = ntx.nodes[node].get("analyzed", True)
        #node_empty_folder = ntx.nodes[node].get("empty_folder", False)
        color = ntx.nodes[node].get("color", "#FFFFFF")
    
        mass = max(1,(node_size / refsize) / loosen * refsize)
        size = refsize * (node_size / refsize) ** 0.5

        node_type = ntx.nodes[node].get("type", "no_type")
        

        min_mass=min(mass,min_mass)
        max_mass=max(mass,max_mass)
        min_size=min(size,min_size)
        max_size=max(size,max_size)
        
        if ":" in node:
            node_locate,node_lbl = node.split(":")
            label = f"{node_type}\nfile {node_locate}\n{node_lbl}"
        else:
            label = f"{node_type}\n{node}"
        label += "\n"+node_comment
        
        shape = "dot"
        if not list(ntx.predecessors(node)):  # is a root
            shape = "star"
        # if not node_analyzed:
        #     shape = "triangleDown"
        # if node_empty_folder:
        #     shape = "diamond"

        kwargs = {
            "label": label,
            "mass": mass,
            "size": size,
            "color": color,
            "shape": shape,
            "borderWidth": 3,
        }
        nt.add_node(
            node,
            **kwargs,
        )

    logger.info(f"Sizes {min_size}/{max_size}")
    logger.info(f"Masses {min_mass}/{max_mass}")
    

    for link in ntx.edges:
        try:
            type = ntx.edges[link]["type"]
        except KeyError:
            type=None
        if type in ["contain"]:
            size=1
            nt.add_edge(link[0], link[1], width=size)

        elif type in ["parent"]:
            size=10
            nt.add_edge(link[0], link[1], width=size)
        else:
            size=5
            nt.add_edge(link[0], link[1], width=size) # call
            

    if physics_panel:
        nt.show_buttons(filter_="physics")

    if writeondisc:
        nt.options.physics.use_barnes_hut(
            {"gravity": -10000,
             "central_gravity":0.3,
             "spring_length":95,
             "spring_strength":0.04,
             "damping":0.09,
             "overlap":0,
            }
        )
        nt.show(prefix + ".html", notebook=False,)  # On recent pyvis, this is necessary.
        header_code = generate_html_header(legend, prefix)
        edit_html(prefix, header_code)

        # if footer_code:
        #    edit_html(prefix, footer_code, header=False)
        logger.info(f"Output written to {prefix}.html")


def edit_html(prefix: str, code: str, header: bool = True) -> None:
    """
    Add the footer or header to the current graph.html

    Args:
        prefix (str): name of the .html file
        code (str): html code to be added to current file
        header (bool): if True write on top of file, otherwise the footer will be written
    """
    location = 2
    insertion = -2
    if header:
        location = 0
        insertion = location + 1

    with open(f"{prefix}.html", "r+") as fout:
        pyvis_code = fout.readlines()
        pyvis_code.insert(
            insertion,
            code,
        )
        fout.seek(location)
        fout.writelines(pyvis_code)


def build_style_struct(legend: dict) -> str:
    """
    Build the css style structure for the circles and respective colors

    Args:
        legend (dict): Name of the filed / Value of complexity as key, color as value

    Returns:
        style_struct (str): Css code for circles
    """
    style_struct = f"""
    <style>
        .left{{
            position: left;
            width: 1200px;
        }}
        .circle{{
            width: 20px;
            height: 20px;
            margin: -5px;
            font-size: 20px;
            border-radius: 50%;
            background : #ffffff;
            display: inline-block;
        }}
    """
    for param, value in legend.items():
        new_param = param
        if "." in param:
            new_param = param.replace(".", "_")
        #  letter a in front of every name to avoid css error
        style_struct += f"""
        .a{new_param}-circle {{
            background: {value};
        }}
    """
    
    style_struct += """ </style>"""

    return style_struct


def build_div_struct(legend: dict, prefix: str) -> str:
    """
    Build the css style structure for the circles and respective colors

    Args:
        legend (dict): Name of the filed / Value of complexity as key, color as value
        prefix (str): Graph name

    Returns:
        div_struct (str): html code to write the circles
    """
    div_struct = f"""
    <div class="left">
        <center>
    """
    # """
    #                 <p style="font-size: 80px;"> {prefix}</p>
    #         <p>
    # """
    counter = 0
    for param in legend.keys():
        new_param = param
        if "." in param:
            new_param = param.replace(".", "_")
        if counter == 6:
            counter = 0
            div_struct += f"""
            &nbsp <div class="circle a{new_param}-circle"></div><span>&nbsp {param}<br><br></span>
            """
        else:
            counter += 1
            div_struct += f"""
            &nbsp <div class="circle a{new_param}-circle"></div><span>&nbsp {param}</span>
            """
    div_struct += """
        </p>
    </center>
    </div>
    """
    return div_struct


def generate_html_header(legend: dict, prefix: str) -> str:
    """
    This will create the html code for the title and the legend of pyvis graph.

    Args:
        legend (dict): Name of the filed / Value of complexity as key, color as value
        prefix (str): Graph name

    Returns:
        header_code (str): header html code
    """
    prefix = "".join([f"{word.upper()} " for word in prefix.split("_")])

    def _clean_key(key:str)-> str:
        for char in " !$*=,":
            key = key.replace(char,"")
        return key

    releg = {_clean_key(key):value for key,value in legend.items()}
    
    style_struct = build_style_struct(releg)
    div_struct = build_div_struct(releg, prefix)
    header_code = style_struct + div_struct

    return header_code


def generate_html_footer(source_path: str, remove_patterns: list) -> str:
    """
    This will create the html code for the footer of pyvis graph.

    Args:
        source_path (str): path to the source file of you analyzed code
        remove_patterns (list): list of patterns removed from the graph

    Returns:
        footer_code (str): footer html code
    """
    footer_code = f"""
    <style>
        .left-margin {{
            position: left;
            margin-left: 600px;
            width: 600px;
        }}
    </style>
    <div class="left-margin">
        <p><br>
            <b>More Informations : </b><br><br>
            &nbsp &nbsp Source file located at: <em>{source_path}</em><br><br>
            &nbsp &nbsp
            Node following these patterns were removed : <br>
    """
    for pattern in remove_patterns:
        footer_code += f"""
        &nbsp &nbsp &nbsp - {pattern}; <br>
        """
    footer_code += """
    <br><br>
    <em><b><u> Note :</u></b> There are 3 major patterns to detect,
    if the pattern name does not contain any '*' it means that the node your trying to filter
    must have this specific name.<br>
    Otherwise, adding '*' in front of the pattern will look for nodes with names that finish with your pattern.<br>
    If the '*' is at the end, it means the node name has to start with this pattern.<br>
    If the pattern is surrounded by '*' it means that the node name has to contain this pattern to be filtered.</em>
    </p>
    """
    return footer_code
