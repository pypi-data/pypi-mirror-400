"""Different layout algorithms to show the callgraphs of several softwares"""

import math
import numpy as np
import networkx as nx
from loguru import logger

BIG=1e10
    
# def depth_layout(pos:dict, depth:dict)-> dict:
#     """Layout to shift radially nodes according to its depth.
#     The higher depth, the outer circle
    
#     External circle is of radius 1
#     """
#     logger.info(f"Depth layout pass.")
    
#     repos={}
#     max_depth=0
#     for value in depth.values():
#         max_depth=max(max_depth,value)
    
#     for node in pos:
#         theta=math.atan2(*pos[node])
#         rad = depth[node]/max_depth
#         repos[node]=(rad*math.cos(theta),rad*math.sin(theta))
#     return pos

# def tested_spring_layout(ntx:nx.DiGraph,pos:dict, nit=30)-> dict:
#     """Application of spring layout, using """

#     for node in ntx.nodes:
#         ntx.nodes[node]["spring_coeff"] = 1./(len(list(ntx.successors(node)))+1)

#     logger.info(f"Spring layout pass for {nit} iterations.")
#     #n = ntx.number_of_nodes()
#     pos = nx.spring_layout(
#         ntx,
#         weight="spring_coeff", 
#         pos=pos,
#         iterations=nit)
#     logger.info("... done")

#     return pos



# def wheel_layout(pos:dict, list_patterns: list)-> dict:
#     """
#     remap an initial layout by the keys of dictionary rules.

#     Parameters:
#     -----------
#     pos : dict A dictionary of positions keyed by node
    
#     Returns:
#     --------
#     pos : dict A dictionary of positions keyed by node
    
    
#     """
#     logger.info("Wheel layout pass.")
#     nkeys = len(list_patterns)
#     if nkeys < 2:
#         logger.warning("Less than two color rules categories, skipping...")
#         return pos
    
#     _pifourth = math.pi/2.

#     for i,key in enumerate(list_patterns):
#         for node in pos:
#             if key in node:
#                 rad=math.hypot(*pos[node])
#                 theta=i/(nkeys-1)*3*_pifourth + _pifourth
#                 pos[node]=(rad*math.cos(theta),rad*math.sin(theta))
#     return pos


# def a4_layout(pos: dict, width:float=21/29.7 , height:float=1., margin=0.05)->dict:
#     """rescale layout to a A4 format"""
#     logger.info(f"Rescale layout to retangular format.")
    
#     # rescale positions, and set them in numpy
#     bbox = [BIG,BIG,-BIG,-BIG]
#     for x,y in pos.values():
#         bbox[0]=min(x,bbox[0])
#         bbox[1]=min(y,bbox[1])
#         bbox[2]=max(x,bbox[2])
#         bbox[3]=max(y,bbox[3])
#     logger.info("bbox", bbox)
#     lenscale =min(bbox[2]-bbox[0],bbox[3]-bbox[1])
#     for node in pos:
#         x = margin + (1.-2*margin) * pos[node][0]/lenscale*width
#         y = margin + (1.-2*margin) * pos[node][1]/lenscale*height
#         pos[node] = np.array([x,y])
#     return pos



# def fa2l_layout(ntx: nx.DiGraph, pos:dict, fa_iter:int=10)->dict:
#     """Force atlas layout using package fa2l, similar to the algorithm of pyvis.

#     DEPRECATED:  Time consuming, Kept here for debug and exploration, prefer ripple_layout

#     NOTE: a second pass is done wthout edges, to let nodes move around with less contraints
#     """
    
#     logger.info("Force-Atlas Barnes-Hut network layout.")
        
#     try:
#         from fa2l import force_atlas2_layout
#     except ImportError:
#         logger.warning("Package fa2l not available, skipping")
#         return pos
    
#     u_ntx = nx.to_undirected(ntx)

#     logger.info("Edges pass")
#     pos = force_atlas2_layout(
#         u_ntx,
#         iterations=10, # this one should 
#         pos_list= pos,
#         #node_masses=node_weights,
#         outbound_attraction_distribution=True,
#         lin_log_mode=False,
#         prevent_overlapping=False,
#         edge_weight_influence=10.0,

#         jitter_tolerance=1.0,
#         barnes_hut_optimize=True,
#         barnes_hut_theta=0.5,

#         scaling_ratio=0.004,
#         strong_gravity_mode=False,
#         multithread=False,
#         gravity=1.0
#     )

#     logger.info("Nodes pass")
#     pos = force_atlas2_layout(
#         u_ntx,
#         iterations=fa_iter,
#         pos_list= pos,
#         #node_masses=node_weights,
#         outbound_attraction_distribution=True,
#         lin_log_mode=False,
#         prevent_overlapping=False,
#         edge_weight_influence=0.01,

#         jitter_tolerance=1.0,
#         barnes_hut_optimize=True,
#         barnes_hut_theta=0.5,

#         scaling_ratio=0.004,
#         strong_gravity_mode=False,
#         multithread=False,
#         gravity=1.0
#     )
    
#     return pos
