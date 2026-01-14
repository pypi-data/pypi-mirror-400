import numpy as np
#from quadtree import QuadTree

EPS = 1e-10

class QuadTree():
    def __init__(
            self,
            coords:np.array,
            xmin:float=-1,
            xmax:float=1,
            ymin:float=-1,
            ymax:float=1,
            max_in_quad=4,
            median_splitting:bool=False):
        """The QuadTree Holder. 
        
        Actually the initial QuadCell object
        With a bit of initialization
        """
        
        npts,_=coords.shape
       
        #print("QuadCell", coords)
        self.q_root = QuadCell(
            list(range(npts)),
            list(coords[:,0]),
            list(coords[:,1]), 
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            max_in_quad=max_in_quad,
            median_splitting=median_splitting)
        
    def content(self)->list:
        return self.q_root.content()

    def ids_clustered(self)->list:
        return [quad.ids for quad in self.q_root.quad_list()]
       
class QuadCell():
    def __init__(
        self,
        ids:list,
        coor_x:list,
        coor_y:list,
        xmin:float,
        xmax:float,
        ymin:float,
        ymax:float,
        max_in_quad:int,
        median_splitting:bool=False):
        """
        A QuadTree recursive Cell

        [RECURSIVE]        

        If subdivided, the ordering is:
         nw (North West) ,ne (North East) , se (South East), sw (South West)

        """
        
            
        npts=len(ids)
        
        self.ids=ids
        self.quads=[]

        if npts>max_in_quad:
            x =np.array(coor_x)
            y = np.array(coor_y)
            if x.max()-x.min() < EPS and y.max() - y.min() < EPS:
                return

            x_mid = 0.5*(xmin+xmax)
            y_mid = 0.5*(ymin+ymax)
            if median_splitting:
                x_mid = np.median(x)
                y_mid = np.median(y)
            
            
            id_ne =  []
            id_nw =  []
            id_se =  []
            id_sw =  []
            i=0
            for x,y in zip(coor_x,coor_y):

                if x<=x_mid:
                    if y<=y_mid:
                        id_se.append(i)
                    else:
                        id_ne.append(i)
                else:
                    if y<=y_mid:
                        id_sw.append(i)
                    else:
                        id_nw.append(i)
                i+=1            
            q_ne =  QuadCell(
                [ids[i] for i in id_ne],
                [coor_x[i] for i in id_ne],
                [coor_y[i] for i in id_ne],
                xmin,x_mid,
                y_mid,ymax,
                max_in_quad
            )
            q_nw = QuadCell(
                [ids[i] for i in id_nw],
                [coor_x[i] for i in id_nw],
                [coor_y[i] for i in id_nw],
                x_mid,xmax,
                y_mid,ymax,
                max_in_quad
            )
            q_sw = QuadCell(
                [ids[i] for i in id_sw],
                [coor_x[i] for i in id_sw],
                [coor_y[i] for i in id_sw],
                x_mid,xmax,
                ymin,y_mid,
                max_in_quad
            )
            q_se = QuadCell(
                [ids[i] for i in id_se],
                [coor_x[i] for i in id_se],
                [coor_y[i] for i in id_se],
                xmin,x_mid,
                ymin,y_mid,
                max_in_quad
            )
            self.quads=[q_ne,q_nw,q_sw,q_se]


    def content(self)->list:
        """Return a nested list of the coords Ids

        [RECURSIVE]        

        This is not necessary for a Barnes-Hut.
        Yet, it allows to understand the nesting of this QuadCell
        Keep it in case someone want to extend the present Class in a fork.
        """
        if not self.quads:
            return self.ids
        else:
            return [ quad.content() for quad in self.quads ]

    def quad_list(self)->list:
        """Return a flat list of the coords Ids clustered by Quad.

        [RECURSIVE]        

        Empty quads are skipped!
        """
        if not self.quads:
            return [self]
        else:
            out = []
            for quad in self.quads:
                if len(quad.ids)>0:
                    out.extend(quad.quad_list())
            return out


