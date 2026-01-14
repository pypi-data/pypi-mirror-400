import numpy as np
from typing import Tuple
def gen_grid_layout_data(ni:int=10,nj:int=10)->Tuple[np.array, np.array, np.array]:
    coords=[]
    conn=[]

    
    def _idx(i,j,ni,nj):
        return (j+i*nj)
    for i in range(ni):
        for j in range(nj):
            x = i*1./ni
            y = j*1./nj
            coords.append( (x,y)) 
            c = _idx(i,j,ni,nj)
            if i>0:
                cmi= _idx(i-1,j,ni,nj)
                conn.append((c,cmi))
            if j>0:
                cmj= _idx(i,j-1,ni,nj)
                conn.append((c,cmj))
                    
    coords = np.array(coords)
    conn=np.array(conn)      
    depth=np.ones(coords.shape[0])
    
    return coords, conn, depth