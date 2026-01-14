
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.pyplot as plt

import networkx as nx

from maraudersmap.colors_utils import colorscale
from maraudersmap.layout_ripple import layout_ripple


def interactive_ripple(ntx, coords, conn, depth_array, sizes):
    # Create the figure and the line that we will manipulate
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.25)
    # ax.set_xticks([])
    # ax.set_yticks([])
    
    links = [ax.plot((coords[i,0],coords[j,0]),(coords[i,1],coords[j,1]),linestyle="-",color="black",alpha=0.5)
             for i,j in conn]

    (net_nodes, ) = ax.plot(coords[:,0],coords[:,1],"o")
    #ax.set_xlim([-1,1])
    #ax.set_ylim([-1,1])
    
    # Radio Buttions for colors and stuff

    # ax_color_by = fig.add_axes([0.01, 0.73, 0.15, 0.15])
    # colors_rules = RadioButtons(
    #     ax_color_by,
    #     ("Default", "Complexity", "Size", "Pragma_GPU"),
    #     label_props={"fontsize": [12, 12, 12, 12]},
    #     radio_props={"s": [30, 30, 30, 30]},
    #     active=0,
    # )

    # def colorizer(label):
    #     """_summary_

    #     Args:
    #         label (_type_): _description_
    #     """
    #     color_dict = {
    #         "Complexity": lambda: color_by(ntx, "CCN"),
    #         "Size": lambda: color_by(ntx, "ssize"),
    #         # "Pragma_GPU": lambda: color_by(ntx, "gpu"),
    #     }

    #     if label == "Default":
    #         colors = ["black"] * len(net_nodes)
    #     # elif label == "Pragma_GPU":

    #     elif label in color_dict:
    #         color_dict[label]()
    #         colors = color_dict[label]()

    #     for idx, line_ in enumerate(net_nodes):
    #         line_[0].set_color(colors[idx])

    #     plt.draw()

    # colors_rules.on_clicked(colorizer)

    # Sliders
    ax_lvl = fig.add_axes([0.15, 0.17, 0.7, 0.03])
    slider_lvl = Slider(
        ax=ax_lvl,
        label="Level  ",
        valmin=-6.,
        valmax=2.,
        valinit=-6,
        orientation="horizontal"
    )
    ax_conn = fig.add_axes([0.15, 0.14, 0.7, 0.03])
    slider_conn = Slider(
        ax=ax_conn,
        label="Connexion  ",
        valmin=-6.,
        valmax=0.,
        valinit=-6,
        orientation="horizontal"
    )
    ax_ovl = fig.add_axes([0.15, 0.11, 0.7, 0.03])
    slider_ovl = Slider(
        ax=ax_ovl,
        label="Overlay  ",
        valmin=-6.,
        valmax=2.,
        valinit=-6,
        orientation="horizontal"
    )
    ax_rep = fig.add_axes([0.15, 0.08, 0.7, 0.03])
    slider_rep = Slider(
        ax=ax_rep,
        label="Repulsion  ",
        valmin=-6.,
        valmax=0.,
        valinit=-6,
        orientation="horizontal"
    )
    ax_nit = fig.add_axes([0.15, 0.05, 0.7, 0.03])
    slider_nit = Slider(
        ax=ax_nit,
        label="Iterations  ",
        valmin=1.,
        valmax=4.,
        valinit=1.,
        orientation="horizontal"
    )
    ax_gvt = fig.add_axes([0.15, 0.02, 0.7, 0.03])
    slider_gvt = Slider(
        ax=ax_gvt,
        label="Frontier  ",
        valmin=-6.,
        valmax=2.,
        valinit=-6,
        orientation="horizontal"
    )
    # The function to be called anytime a slider's value changes
    def update(val):
        relax_connexions = 10.**(slider_conn.val)
        relax_repulsions = 10.**(slider_rep.val)
        relax_gravity_frontier = 10.**(slider_gvt.val)
        relax_gravity_level = 10.**(slider_lvl.val)
        relax_overlap = 10.**(slider_ovl.val)
        nit=int(10.**(slider_nit.val))
        coords2 = layout_ripple(
            coords, 
            conn,
            depth_array,
            relax_gravity_level,
            relax_gravity_frontier,
            relax_repulsions,
            relax_overlap,
            relax_connexions,
            nit=nit,
            wtf=False,
        )
        net_nodes.set_data(coords2[:,0],coords2[:,1])
        for link,(i,j) in zip(links,conn):
            link[0].set_data((coords2[i,0],coords2[j,0]),(coords2[i,1],coords2[j,1]))
        #fig.canvas.draw_idle()
    
    
    # register the update function with each slider
    slider_conn.on_changed(update)
    slider_rep.on_changed(update)
    slider_gvt.on_changed(update)
    slider_lvl.on_changed(update)
    slider_ovl.on_changed(update)
    slider_nit.on_changed(update)


    plt.show()

    relax_connexions = 10.**(slider_conn.val)
    relax_repulsions = 10.**(slider_rep.val)
    relax_gravity_frontier = 10.**(slider_gvt.val)
    relax_gravity_level = 10.**(slider_lvl.val)
    relax_overlap = 10.**(slider_ovl.val)
    nit=int(10.**(slider_nit.val))
    coords2 = layout_ripple(
        coords, 
        conn,
        depth_array,
        relax_gravity_level,
        relax_gravity_frontier,
        relax_repulsions,
        relax_overlap,
        relax_connexions,
        nit=nit,
    )
    return coords2
    

# def color_by(ntx: nx.DiGraph, color_key: str):
#         """_summary_"""

#         # Span for the CCN / sizes
#         minimum = 9e9
#         maximum = 9e-9
#         for node in ntx.nodes:
#             minimum = min(minimum, ntx.nodes[node][color_key])
#             maximum = max(maximum, ntx.nodes[node][color_key])

#         colors = []
#         for node in ntx.nodes:
#             colors.append(colorscale(ntx.nodes[node][color_key], minimum, maximum))

#         return colors