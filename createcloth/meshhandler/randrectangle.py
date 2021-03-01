import pywavefront
import numpy as np
from collections import Counter
from scipy.interpolate import griddata as myinterp
import networkx as netx
#from pythonsimplecycles.findrand import find_rand

class randrectangle():
    """
    class to save information about the broder of a cloth. saves indexarrays
    :param up: list with index of line up of the cloth
    :param down: list with index of line down of the cloth
    :param left: list with index of line left of the cloth
    :param right: list with index of line right of the cloth
    """
    up, down, left, right = None, None, None, None
    updist, downdist, leftdist, rightdist = None, None, None, None
    mesh, vertices = None, None
    def __init__( self, downlist, rightlist, uplist, leftlist, mesh = None ):
        if downlist[-1] == rightlist[0] or rightlist[-1] == uplist[-1] \
                or uplist[0] == leftlist[-1] or leftlist[0] == downlist[0]:
            pass
        elif downlist[-1] == rightlist[0] or rightlist[-1] == uplist[0] \
                or uplist[-1] == leftlist[0] or leftlist[-1] == downlist[0]:
            leftlist.reverse()
            uplist.reverse()
        else:
            raise Exception()

        self.updatevertlists( downlist, rightlist, uplist, leftlist )
        if mesh != None:
            self.mesh = mesh
            self.vertices = mesh.vertices
            self.updatedistlists()

    def rand_array( self ):
        up_real = self.vertices[ self.up ]
        down_real = self.vertices[ self.down ]
        left_real = self.vertices[ self.left ]
        right_real = self.vertices[ self.right ]
        return up_real, down_real, left_real, right_real

    def updatevertlists( self, downlist, rightlist, uplist, leftlist ):
        up = []
        for x in uplist:
            up.append(x)
        self.up = np.array(up)
        down = []
        for x in downlist:
            down.append(x)
        self.down = np.array(down)
        left = []
        for x in leftlist:
            left.append(x)
        self.left= np.array(left)
        right = []
        for x in rightlist:
            right.append(x)
        self.right = np.array(right)


    def updatedistlists( self ):
        self.updist, self.downdist, \
                self.leftdist, self.rightdist = [],[],[],[]
        for arg in [\
                (self.updist, self.up), \
                (self.downdist, self.down), \
                (self.leftdist, self.left), \
                (self.rightdist, self.right), \
                ]:
            lastindex = arg[1][0]
            tmpdistance = 0
            for index_point in arg[1]:
                tmpdistance = tmpdistance \
                        + np.linalg.norm(self.vertices[index_point] \
                                                    - self.vertices[lastindex])
                arg[0].append( tmpdistance )
                lastindex = index_point
        self.uplength = self.updist[-1]
        self.downlength = self.downdist[-1]
        self.leftlength = self.leftdist[-1]
        self.rightlength = self.rightdist[-1]

class randrectangle_points(randrectangle):
    def __init__( self, leftdown, rightdown, rightup, leftup, mesh, mesh_graph):
        #boundary = find_rand( mesh_graph )
        boundary = myfindrand( mesh )
        try:
            tmpa = boundary.index(leftdown)
            boundary = boundary[tmpa:] + boundary[0:tmpa]
            a = boundary.index(leftdown)
            b = boundary.index(rightdown)
            c = boundary.index(rightup)
            d = boundary.index(leftup)
            if a<b and b<c and c<d:
                pass
            elif b>c and c>d:
                boundary.reverse()
                a = boundary.index(leftdown)
                b = boundary.index(rightdown)
                c = boundary.index(rightup)
                d = boundary.index(leftup)
                pass
            else:
                print("a:%d, b:%d c:%d d:%d"%(a, b, c, d) )
                raise Exception("boundarypoints arent given "\
                                + "in the correct order")
        except ValueError as err:
            errlist = list(err.args)
            errlist.append("couldnt found given pointindex in boundary")
            err.args = errlist
            print( boundary )
            raise err
        llen = len(boundary)
        down = boundary[a:b+1]
        left = boundary[d:] + boundary[0:1]
        left.reverse()
        right= boundary[b:c+1]
        up   = boundary[c:d+1]
        up.reverse()
        super().__init__( down, right, up, left, mesh )


def myfindrand( mesh ):
    randedges = findrandedges( mesh )
    return find_single_rand( randedges )

def findrandedges( mesh ):
    listedges = []
    for face in mesh.faces:
        for i in range(len(face)):
            edge = frozenset(( face[i], face[i-1] ))
            listedges.append( edge )
    edgecount = Counter( listedges )
    randedges = [ edge for edge, count in edgecount.items() if count==1 ]
    return randedges

def find_single_rand( randedges ):
    asd = netx.Graph( randedges )
    #asd.add_edges_from( randedges )
    randpath = netx.cycle_basis( asd )
    if len( list( randpath ) )!= 1:
        raise Exception( "cant handle surfaces with more than one closed "\
                        "border")
    return list( randpath )[0]

    tmponerand = []
    rand = [tmponerand]
    tmppoint = list( randedges[0] )[0]
    startpoint = tmppoint
    tmponerand.append( tmppoint )
    while len(randedges) > 0:
        tmpedge = findset_withpoint( tmppoint, randedges )
        randedges.remove( tmpedge )
        tmppoint = tmpedge.difference( set([tmppoint]) ).pop()
        tmponerand.append( tmppoint )
        if tmppoint == startpoint:
            if len(randedges) > 0:
                tmponerand = []
                rand.append( tmponerand )
                tmppoint = list( randedges[0] )[0]
    return rand


def findset_withpoint( point, set_list ):
    set_list = list(set_list)
    for edge in set_list:
        if point in edge:
            return edge
    

def control_findset_withpoint( point, set_list ):
    set_list = list(set_list)
    for edge in set_list:
        print(repr(edge) + repr(point in edge))
        if point in edge:
            return edge
