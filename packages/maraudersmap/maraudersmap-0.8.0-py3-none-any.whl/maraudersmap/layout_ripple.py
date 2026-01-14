"""Custom RIPPLE layout for callgraphs, fair approximation of a force atlas layout"""

import numpy as np
import networkx as nx
from loguru import logger

from maraudersmap.layout_forces import connexion_forces, repulsion_forces_macros, repulsion_forces_neighbors,gravity_level_forces, gravity_frontier
EPS=1e-12

def layout_ripple(
        coords:np.array, 
        conn:np.array,
        depth_array:np.array,
        relax_gravity_level:float,
        relax_gravity_frontier:float,
        relax_repulsions:float,
        relax_overlap:float,
        relax_connexions:float,
        nit:int=1000,
        connexion_length:float= 0.0,
        neighbors_fac: float = 0.0,
        quad_fac: float = 0.0,
        with3d:bool=False,
        wtf: bool = False
    ):


    logger.info(f"Nit  : {nit}")
    logger.info(f"Conn : {relax_connexions}")
    logger.info(f"Rep. : {relax_repulsions}")
    logger.info(f"Gvt. : {relax_gravity_frontier}")
    logger.info(f"Lvl. : {relax_gravity_level}")
    logger.info(f"Ovl. : {relax_overlap}")

    if wtf:
        coords_ =  coords
    else:
        coords_ = coords.copy()

    nnodes = coords.shape[0]
    

    if with3d:
        nnodes=coords.shape[0]
        coords3d= np.zeros((nnodes,3))
        coords3d[:,0:2]=coords_
        coords_ = coords3d

    # Compute typical sizes
    rim = 1            # drawing radius
    
    #logger.info(f"gravity {relax_gravity_frontier}, conn {relax_connexions}, rep {relax_repulsions}")
    neighbors = max(int(nnodes*neighbors_fac), 3)
    max_in_quad = max(int(nnodes*quad_fac), 3)
    delay=0
    for iter in range(nit):
        coords_ += gravity_level_forces(coords_,depth_array, rim) * relax_gravity_level
        coords_ += gravity_frontier(coords_, rim, expnt=2) *relax_gravity_frontier  
        coords_ += repulsion_forces_macros(coords_,max_in_quad=max_in_quad, in_cell_repulsion=False) * relax_repulsions
        coords_ += repulsion_forces_neighbors(coords_,neighbors= neighbors)* relax_overlap
        coords_ += connexion_forces(coords_, conn, length=connexion_length, expnt=2)*relax_connexions
        if delay > nit*1./10:
            logger.info(f"Layout {int(iter/nit*100)}%")
            delay = 0
        delay += 1
    logger.info(f"Layout Done")

    if with3d and iter > 0.7*nit:
            coords_ += gravity_frontier(coords_, rim*0.1, axis=2) *relax_gravity_frontier 

    if  with3d:
        coords_=coords_[:,0:2]
    return coords_


