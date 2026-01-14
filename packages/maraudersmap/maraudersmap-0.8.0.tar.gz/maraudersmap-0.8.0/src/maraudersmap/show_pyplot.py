"""module to plot a graph using pyplot"""
import matplotlib.pyplot as plt
import networkx as nx
import math
from loguru import logger

import numpy as np

from maraudersmap.nx_utils import compute_graph_depth
from maraudersmap.layout_ripple import layout_ripple
#from maraudersmap.layout_misc import a4_layout,wheel_layout,depth_layout
from maraudersmap.colors_utils import shade_color
from maraudersmap.show_pyplot_interactive import interactive_ripple
from maraudersmap.layout_debug import gen_grid_layout_data

EPS=1e-12
SMALLEST_ITEM=1./500
FONTSIZE=0.5

def ntw_pyplot2d(
    ntx: nx.DiGraph,
    file_prefix:str="mmap_pyplot",
    debug=False
):
    """
    Convert a networkx to a pyplot 2D with a goodlooking shape
    """

    depth = compute_graph_depth(ntx)    
    pos = nx.random_layout(ntx,seed=2)            # initial fixed random layout
    coords =np.array( [pos[node] for node in pos]) *2 -1
    depth_array =np.array( [depth[node] for node in pos])
    conn=[]
    node_list = list(ntx.nodes.keys())
    for edge in ntx.edges:
        if edge[0] != edge[1]:
            conn.append([node_list.index(edge[0]),node_list.index(edge[1])])
    conn =  np.array(conn)

    sizes = []
    for node_name in pos:
        sizes.append(np.sqrt(ntx.nodes[node_name]["ssize"]))

    if debug:
        coords,conn, depth_array = gen_grid_layout_data(ni=10, nj=10)




    coords2 = interactive_ripple(ntx,coords, conn,depth_array,sizes )
    
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.set_axis_off()
    ax.set_aspect('equal')
    pos =  {
            node: coords2[i,:] for i, node in enumerate(node_list)
    }
    
    ax = build_pyplot_graph(ntx,ax,pos,show_names=True)
    #ax = add_patterns_to_fig(ax,pos,rules)
    #Prefer a file dump to a plt.show(), which is much slower to plot and explore thant the PDF.
    plt.savefig(f"{file_prefix}.pdf")
    plt.show()


def build_pyplot_graph(ntx: nx.DiGraph, ax:plt.Axes, pos: dict, show_names=False)->plt.Axes:
    """Pyplot graph building."""

    logger.info("Build Matplotlib figure")

    def auto_rad(size:float, min_size: float=2)-> float:
        """Compute the size of a node."""
        rad = math.log10(
            max(size, min_size)
            /min_size
        )
        return SMALLEST_ITEM*(1+rad)
    
    # Start with edges to put them in the background
    for edge in ntx.edges:
        pos1 = np.array(pos[edge[0]])
        pos2 = np.array(pos[edge[1]])
        color=ntx.nodes[edge[0]].get("color", "cyan")
        dx = pos2-pos1

        # Shorten arrows to stay out of node circles
        rad1= 1.1*auto_rad(ntx.nodes[edge[0]].get("size", 0))
        rad2= 1.1*auto_rad(ntx.nodes[edge[1]].get("size", 0))
        dx_len=math.hypot(*dx)+EPS
        pos_shift = pos1 + dx/dx_len*rad1
        dx_rescaled = dx/dx_len *(dx_len-rad1-rad2)
        
        width = SMALLEST_ITEM
        headsize = max(0.05*(math.hypot(*dx_rescaled)+EPS), 2*width)

        ax.arrow(
            *pos_shift,
            *dx_rescaled,
            color=color,
            linewidth=width,
            head_width=0.66*headsize, 
            head_length=headsize,
            alpha=0.25,
            length_includes_head=True
        )

    for node in ntx.nodes:
        color=ntx.nodes[node].get("color", "black")
        rad = auto_rad(ntx.nodes[node].get("size", 0))
        name=ntx.nodes[node].get("name", node)
        circle = plt.Circle( 
            pos[node],
            rad,
            color=color,
            linewidth=0,
            #alpha=0.8
            )
        ax.add_artist(circle)   
        if show_names:
            label = name.replace("::","\n")
            label = label.replace(":","\n")
            ax.text(
                pos[node][0],
                pos[node][1]-1*rad, #Place text under the node
                label,
                color=shade_color(color,-0.5),
                fontsize=FONTSIZE,ha="center", va="top")
    return ax
    

def add_patterns_to_fig(ax:plt.Axes, pos: dict, rules:dict)->plt.Axes:
    """Initially used to add a square frontier for patterns
    
    NOTE: Messy, seldom used now.
    """
    margin=0.05
    for key,color in rules.items():
        posx=[]
        posy=[]
        for node in pos:
            if key in node:
                posx.append(pos[node][0])
                posy.append(pos[node][1])

        if posx:
            posx=np.array(posx)
            posy=np.array(posy)
            box = plt.Rectangle( 
                (posx.min()-margin,posy.min()-margin),
                width=posx.max()-posx.min()+2*margin,
                height=posy.max()-posy.min()+2*margin,
                fill=False,
                #color=color,
                edgecolor=color,
                linewidth=2,
                alpha=0.05
            )
            ax.add_artist(box) 
            
            x = posx.min()-margin
            y = posy.min()-margin
            t = ax.text(x,y, key,color=color,fontsize=FONTSIZE,ha="left",va="top")
    return ax


def fastplot(ntx, color='lightblue'):
    """Utility kept for debugging, useful while writing unitary tests"""
    nx.draw(
        ntx,
        with_labels=True,
        node_color=color,
        edge_color=color,
        node_size=500, 
        arrowstyle='->',
        arrowsize=10,
        pos=nx.spring_layout(ntx)
    )
    