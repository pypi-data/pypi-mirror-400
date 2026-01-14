"""The forces used in ntwork layouts"""

import numpy as np
from loguru import logger
from scipy.spatial import cKDTree
from maraudersmap.quadtree import QuadTree

EPS=1e-12



#      R E P U L S I O N   Forces
def repulsion_forces_macros(coords:np.array,weights:np.array=None ,max_in_quad:int=10, in_cell_repulsion:bool=True)->np.array:
    """Force to push away a node from its neigbors, vanishes at PUSHLEN distance"""   
    npts = coords.shape[0]
    if weights is None:
        weights=np.ones((npts))

    motion = np.zeros_like(coords)
    qt = QuadTree(
        coords,
        xmin=coords[:,0].min(),
        xmax=coords[:,0].max(),
        ymin=coords[:,1].min(),
        ymax=coords[:,1].max(),
        max_in_quad=max_in_quad,
        median_splitting=True
    )

    cluster_list_ids = qt.ids_clustered()
    #logger.info(f"Quad Clusters: {len(cluster_list_ids)}")
    cluster_list_center  = []
    cluster_list_weight  = []
    for ids_cluster in cluster_list_ids:
        cluster_list_center.append(np.average(coords[ids_cluster,:],axis=0))
        cluster_list_weight.append(weights[ids_cluster].sum())    
        if in_cell_repulsion:
            motion[ids_cluster,:] += _apply_repulsion(coords[ids_cluster,:],weights[ids_cluster])
    
    macro_motions =  _apply_repulsion(np.array(cluster_list_center), weights=np.array(cluster_list_weight))

    # for i,ids_cluster in enumerate(cluster_list_ids):
    #     motion[ids_cluster,:] += macro_motions[i,:]

    # not very interesting unless a lot of clusters
    cluster_indices = np.concatenate(cluster_list_ids)
    macro_repeats = np.concatenate([np.repeat(i, len(ids)) for i, ids in enumerate(cluster_list_ids)])
    # Use the advanced indexing to update the motion array
    motion[cluster_indices] += macro_motions[macro_repeats]

    return motion



def _apply_repulsion(coords:np.array, weights:np.array=None):
    npts = coords.shape[0]
    if npts == 1:
        return np.zeros_like(coords)
    if weights is None:
        weights=np.ones(npts)
    
    pairs = np.array(sorted({tuple(sorted((i, j))) for i in range(npts) for j in range(npts) if i != j}))
    edge_vectors = coords[pairs[:,0],:]-coords[pairs[:,1],:]
    distances=np.linalg.norm(edge_vectors,axis=1)
    ones_vect = edge_vectors/(distances[:,np.newaxis]+EPS)
    springs = np.clip(1/(distances+EPS)**0.5,None,1)
    
    ratio_weights = weights[pairs[:,0]]/weights[pairs[:,1]]
    
    motion = np.zeros_like(coords)
    
    # Loop version, to check...
    # for k,(i,j) in enumerate(pairs):
    #     motion[i,:] +=  +ones_vect[k,:]*springs[k]/ratio_weights[k]
    #     motion[j,:] +=  -ones_vect[k,:]*springs[k]/ratio_weights[k]
   
    # Compute the update values for motion array
    update_values = (ones_vect * springs[:, np.newaxis]) / ratio_weights[:, np.newaxis]
    # Apply updates to the motion array
    np.add.at(motion, pairs[:, 0], +update_values)
    np.add.at(motion, pairs[:, 1], -update_values)
    return motion


def repulsion_forces_neighbors(coords:np.array, weights:np.array=None ,neighbors:int=10)->np.array:
    """Force to push away a node from its neigbors"""
    tree = cKDTree(coords)
    _,neighb  = tree.query(coords, k=neighbors)
    motion = np.zeros_like(coords)
    
    for nei in range(1,neighbors):
        edge_vectors = (coords[neighb[:,nei]]-coords[:,:])
        distances=np.linalg.norm(edge_vectors, axis=1)
        springs= np.clip(1/(distances+EPS)**0.5,None,1)
        motion -= edge_vectors/(distances[:,np.newaxis]+EPS)*springs[:,np.newaxis]

    return motion


# C_O_N_N_E_X_I_O_N forces


def spring_model(distances:np.array,length, expnt:int=1)->np.array:
    """
    ::
            A                                .
            |                         .
            |                   .
            |                 .
            |               .
            +-------------.-------------> Distance
            |         .   length
            |      . 
            |    . 
            |   . 
     -length|...
            |
            | 
    
    Spring layout model

    length is the desired distance

    - if correct length (d=length), displacement zero
    - in case of extreme repulsion (d < length), displacement cannot be more than half length
    - in case of attraction , prop to inverse distance
    - in case of extreme attraction (d < length), displacement cannot be more than half distance
    - in case of attraction , prop to distance

    """
    if length > EPS:
        adim=distances/length
        spring = np.where(adim<1,-(1/adim-1),(adim-1)**expnt)
        spring = np.clip(spring,-0.49*length,0.49*distances)
    else:
        spring =  np.clip(distances**expnt,None,0.49*distances)
    
    return spring


def connexion_forces(coords:np.array, conn: np.array , length:float=0, expnt:int=1)->np.array:
    """Force to stabilize two neigbors to the distance PUSHLEN"""
    
    edge_vectors = (coords[conn[:,0]]-coords[conn[:,1]])                 
    distances=np.linalg.norm(edge_vectors,axis=1)
    springs= spring_model(distances,length,expnt=expnt)
    ones_vect=edge_vectors/(distances[:,np.newaxis]+EPS)
    conn_motion = ones_vect* springs[:,np.newaxis]
    motion = np.zeros(coords.shape)
    
    # for i,j in enumerate(conn[:,0]):
    #     motion[j,:] -= conn_motion[i,:]
    # #motion[conn[:, 0], :] -= conn_motion
    # for i,j in enumerate(conn[:,1]):
    #     motion[j,:] += conn_motion[i,:]
    # #motion[conn[:, 1], :] += conn_motion

    # Vectorized update of motion array
    np.add.at(motion, conn[:, 0], -conn_motion)
    np.add.at(motion, conn[:, 1], conn_motion)
    return motion


#   vvvvvvvvv  G R A V I T Y  vvvvvvvvv

def gravity_level_forces(coords:np.array,depth_array:np.array, rim:float,expnt=1.)->np.array:
    """Force to attract a node to its level gravity circle.
    The lower the node is in the callgraph, the outer circle it will be.

    Most external circle is at distance RIM.
    By lowering EXPNT, one can enlarge the inner circles.

    Depth zero is sent at ythe center
    Max depth is at rim

    0   1   2   3   4   
    <--------------->

    """
    max_depth = np.max(depth_array)
    
    rad=np.linalg.norm(coords,axis=1)
    gravity_pits_radius = (depth_array /max_depth)**expnt * rim 
    radvec = coords/(rad[:,np.newaxis]+EPS)
    intensity = (rad-gravity_pits_radius)
    motion = -radvec *intensity[:,np.newaxis]
    return  motion


def gravity_frontier(coords:np.array, rim:float,expnt=2, axis=None)->np.array:
    """Force to  limit nodes to a circular region of radius RIM
    """
    if axis is None:
        rad=np.linalg.norm(coords,axis=1)
        radvec = coords/(rad[:,np.newaxis]+EPS)
    else:
        rad = np.abs(coords[:,axis])
        radvec = np.zeros_like(coords)
        radvec[:,axis] = coords[:,axis]/(rad+EPS)
        
    intensity = np.clip((rad/rim)**expnt,None,1)
    motion = - intensity[:,np.newaxis] * radvec * rim
    return  motion
