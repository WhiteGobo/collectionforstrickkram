import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
import itertools
from .gridrelaxator import main as create_gridrelaxator


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
        raise Exception( "border is not unambiguous. Algorithm needs surface"\
                            " without holes." )
    randedges = [ frozenset(e) for e in randedges ]

    node_to_edges = dict()
    my_add_edge = lambda node, e: node_to_edges.setdefault( node, set() )\
                                                                    .add( e )
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






def generate_surfaceinterpolator( vertexpositions, st_coordinates ):
    delaunay_triang = Delaunay( st_coordinates )
    #xyz_as_uvmap = CloughTocher2DInterpolator( delaunay_triang, vertexpositions)
    xyz_as_uvmap = LinearNDInterpolator( delaunay_triang, vertexpositions)
    return xyz_as_uvmap


def relax_to_matrix( uv_to_xyz, ulength, vlength ):
    from .create_surfacemap import create_surfacemap
    mysurfacemaps = create_surfacemap( uv_to_xyz, ulength, vlength )
    myposgraph = create_gridrelaxator( mysurfacemaps, ulength, vlength )
    #print( myposgraph.nodes( data=True ) )
    tmpxyzmatrix = []
    for i in range( ulength ):
        tmpline = []
        tmpxyzmatrix.append( tmpline )
        for j in range( vlength ):
            n = myposgraph.nodes[(i,j)]
            tmpline.append(( n["x"], n["y"], n["z"] ))
    xyz_matrix = np.array(tmpxyzmatrix)
    return xyz_matrix


if __name__=="__main__":
    filename = get_args()
    main( filename )
