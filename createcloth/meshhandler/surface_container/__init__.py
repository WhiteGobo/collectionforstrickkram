from .. import ply_handler as _ply
import itertools
from collections import Counter
from .create_surfacemap import surfacemap
import numpy as np


class surface():
    def __init__( self, vertex_positions, faces, up, right, down, left ):
        self.vertices = vertex_positions
        self.faces = faces
        self.up = up
        self.right = right
        self.down = down
        self.left = left

    def to_plyfile( self, filepath ):
        #xyzmatrix = [ (ulength,), (vlength,), (x.reshape(x.size),), \
        #                    (y.reshape(y.size),), (z.reshape(z.size),)]
        vertexpipeline = ( \
                            (b"float", b"x"), \
                            (b"float", b"y"), \
                            (b"float", b"z"), \
                            )
        facespipeline = ((b"list", b"uchar", b"uint", b"vertex_indices" ), )
        borderpipeline = ( \
                            (b"uint", b"rightup"), \
                            (b"uint", b"leftup"), \
                            (b"uint", b"leftdown"), \
                            (b"uint", b"rightdown"), \
                            )
        vert = np.array( self.vertices )
        vertexpos = [ vert[:,0], vert[:,1], vert[:,2] ]
        facesindex = [self.faces, ]
        lu, ru, rd, ld = get_edgevertices( self.up, self.down )
        borderindices = [ (lu,), (ru,), (rd,), (ld,) ]

        myobj = _ply.ObjectSpec.from_arrays([ \
                            ("vertex", vertexpipeline, vertexpos ), \
                            ("faces", facespipeline, facesindex ), \
                            ("rand", borderpipeline, borderindices ), \
                            #("matrix", matrixpipeline, xyzmatrix), \
                            ])
        _ply.export_plyfile( filepath , myobj, "ascii" )

    @classmethod
    def from_plyfile( cls, filepath ):
        myobj = _ply.load_ply_obj_from_filename( filepath )
        vertex_positions = myobj[ "vertex" ].get_filtered_data( "x", "y", "z")
        faces = myobj[ "face" ].get_filtered_data( "vertex_indices" )
        faces = [ f[0] for f in faces ]

        tmp = myobj["rand"].get_filtered_data( "leftup", "rightup", \
                                                "rightdown", "leftdown" )
        leftup_vertex, rightup_vertex, rightdown_vertex, leftdown_vertex=tmp[0]
        randnodecycle = get_rand_array( faces )
        up, right, down, left = get_border( randnodecycle, leftup_vertex, \
                            rightup_vertex, rightdown_vertex, leftdown_vertex)

        return cls( vertex_positions, faces, up, right, down, left )



def get_rand_array( faces ):
    tmp = ( face_to_edges(single) for single in faces )
    alledges = itertools.chain( *tmp )
    alledges = [ frozenset(edge) for edge in alledges ]
    countedges = Counter( alledges )
    if set() != set( alledges ).difference([ edge \
                                for edge, n in countedges.items() if n < 3 ]):
        raise Exception("This is not a surface. following edges were "\
                        +"found more than twice: %s" \
                        %(str([ edge for edge, n in countedges.items() \
                        if n > 2 ])))
    randedges = [ edge for edge, n in countedges.items() if n == 1 ]
    tmpnodes = Counter( itertools.chain( *randedges ) )
    if not all(( number==2 for number in tmpnodes.values() )):
        raise Exception( "border is not unambiguous. Algorithm needs surface "\
                        "without holes." )
    randedges = [ frozenset(e) for e in randedges ]

    node_to_edges = dict()
    my_add_edge = lambda node, e: node_to_edges.setdefault( node, set()).add(e)
    for edge in randedges:
        a,b = edge
        my_add_edge( a, edge )
        my_add_edge( b, edge )
    startnode, tmp = iter( randedges ).__next__()
    del( tmp )
    usednodes = [ startnode ]
    usededges = set()
    currentnode = startnode
    for i in range( len(randedges)-1 ):
        tmpedges = node_to_edges[ currentnode ]
        freeedges = tmpedges.difference( usededges )
        nextedge = iter( freeedges ).__next__()
        freenodes = nextedge.difference( usednodes )
        nextnode = iter( freenodes ).__next__()
        usednodes.append( nextnode )
        usededges.add( nextedge )
        currentnode = nextnode
    return usednodes

def get_edgevertices( up_list, down_list ):
    leftup = up_list[0]
    rightup = up_list[-1]
    rightdown = down_list[0]
    leftdown = down_list[-1]
    return leftup, rightup, rightdown, leftdown

def get_border( randnodecycle, leftup_vertex, rightup_vertex, \
                                rightdown_vertex, leftdown_vertex):
    leftupindex = randnodecycle.index( leftup_vertex )
    randnodecycle = list( randnodecycle )
    randnodecycle = randnodecycle[leftupindex:] + randnodecycle[:leftupindex+1]
    leftupindex = 0
    rightupindex = randnodecycle.index( rightup_vertex )
    rightdownindex = randnodecycle.index( rightdown_vertex )
    leftdownindex = randnodecycle.index( leftdown_vertex )
    #make sure nodes are ordered clockwise
    if rightupindex > rightdownindex:
        randnodecycle.reverse()
        leftupindex = randnodecycle.index( leftup_vertex )
        rightupindex = randnodecycle.index( rightup_vertex )
        rightdownindex = randnodecycle.index( rightdown_vertex )
        leftdownindex = randnodecycle.index( leftdown_vertex )
    if not rightdownindex < leftdownindex:
        raise Exception("border is not ordered via cornerpoints")

    #leftupindex = 0
    upborder = randnodecycle[ : rightupindex+1 ]
    rightborder = randnodecycle[ rightupindex : rightdownindex+1 ]
    downborder = randnodecycle[ rightdownindex : leftdownindex+1 ]
    leftborder = randnodecycle[ leftdownindex : ]

    return upborder, rightborder, downborder, leftborder


def face_to_edges( face ):
    tmp = list( face )
    tmp.append(tmp[0])
    edges = list( itertools.zip_longest( tmp[0:-1], tmp[1:] ) )
    return edges
