from .create_surfacemap import get_surfacemap
from .gridrelaxator import gridrelaxator, InstabilityError
import networkx as netx
import io

from .create_surfacemap import surfacemap as type_surfacemap

"""
:todo: replace hshable_set with frozenset
"""


def relax_strickgraph_on_surface( strickgraph, wavefrontfilename,
                                                numba_support = False):
    """
    :rparam: returns a graph with node attributes as the positions
            eg: x = netx.get_node_attributes( graph, 'x' )
    :param strickgraph: selfexplanatroy
    :todo: calculate the error margin
    """
    #surfacemap =get_surfacemap( wavefrontfilename, numba_support=numba_support)
    surfacemap =meshinterpreter_dict[type(wavefrontfilename)](wavefrontfilename)
    border = strickgraph.get_borders()

    gridgraph = prepare_gridcopy( strickgraph )

    no_solution = True
    strengthmult =  2.0
    maximal_error = 1e-6 #this should be caculated
    # maximal error can be estimated with consideration of strength to movement
    # and maximal Spiel(german) of each node
    while no_solution:
        try:
            myrelaxator = gridrelaxator( gridgraph, surfacemap, border,\
                                    strengthmultiplier=strengthmult, \
                                    numba_support =numba_support )
            myrelaxator.relax( maximal_error )
            no_solution = False
        except InstabilityError:
            strengthmult = strengthmult * 0.7
    return myrelaxator.get_positiongrid()


def prepare_gridcopy( strickgraph ):
    gridgraph = netx.Graph( strickgraph )

    #tidy the graph up for usage in gridrelaxator
    gridgraph.remove_node("start")
    gridgraph.remove_node("end")
    for ( node1, node2, edgedata ) in gridgraph.edges( data=True ):
        edgedata.clear()
        edgedata.update({ "length":0.1, "strength":1 })
    return gridgraph

meshinterpreter_dict={}
def get_surfacemap_from_iobufferedstream( wavefrontfilename ):
    return get_surfacemap( wavefrontfilename, numba_support=False)
meshinterpreter_dict.update({ io.BufferedReader: \
                            get_surfacemap_from_iobufferedstream })

def get_surfacemap_identity( surfacemap ):
    return surfacemap
meshinterpreter_dict.update({ type_surfacemap: \
                                get_surfacemap_identity })

def ququq_generate_tension_graph( strickgraph, surfacemap ):
    """
    generates a graph similar to the strickgraph
    the nodes holds as attributes things like tension
    the edge also holds physical properties like tension
    :rtype tensiongraph: networkx.Graph
    """
    pass



def weave_positiongraph_into_strickgraph( strickgraph, positiongraph ):
    for nodeattr in [ "x", "y", "z" ]:
        attribute_dictionary = netx.get_node_attributes( positiongraph, \
                                                                    nodeattr )
        netx.set_node_attributes( strickgraph, attribute_dictionary, nodeattr)

    for edgeattr in [ "tension", "currentlength" ]:
        attribute_dictionary = netx.get_edge_attributes( positiongraph, \
                                                                    edgeattr)
        # identify the attributes by the points, orderindependent
        attribute_dictionary = { hashable_set(key): attribute_dictionary[key] \
                                        for key in attribute_dictionary }
        # {edge[1],edge[2]} is set of points of the edge

        attribute_dictionary = { \
                        edge: \
                        attribute_dictionary.get( \
                                hashable_set((edge[0],edge[1])), {} )\
                        for edge in strickgraph.edges( keys=True ) \
                        }

        netx.set_edge_attributes( strickgraph, attribute_dictionary, edgeattr )


class hashable_set( set ):
    def __hash__( self ):
        return sum([ x.__hash__() for x in self ])
