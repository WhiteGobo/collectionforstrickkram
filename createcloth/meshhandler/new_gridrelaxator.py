import networkx as netx
from typing import Tuple, Callable, Hashable, Dict
from scipy.optimize import minimize
from scipy.sparse import lil_matrix, dok_matrix
from scipy.sparse.linalg import spsolve
import numpy as np
from itertools import chain
from ..strickgraph import strickgraph
from .PlySurfaceHandler import plysurfacehandler

def uniqueindex_generator():
    i = 0
    while True:
        yield i
        i = i+1

class vertice_param_position_container():
    nextindex = iter( uniqueindex_generator() )
    def __init__( self, vertexindex ):
        self.vertexindex = vertexindex
        self.u_index = self.nextindex.__next__()
        self.v_index = self.nextindex.__next__()
        #self.x_index = nextindex.__next__()
        #self.y_index = nextindex.__next__()
        #self.z_index = nextindex.__next__()
        self.maxindex = max( self.u_index, self.v_index )


def relax_gridgraph( gridgraph:strickgraph, surfacemap: plysurfacehandler ) \
                                                    -> Dict[ Hashable, Dict ]:
    border = gridgraph.get_borders()
    gridgraph = gridgraph.give_real_graph()
    graphnodes_list: list[ Hashable ]
    edges_list: list[ Tuple[ int, int ]]
    border_up: list[ int ]
    border_left: list[ int ]
    border_down: list[ int ]
    border_right: list[ int ]
    vertice_positions: list[ Tuple[ float, float, float ] ]
    vertice_indexcontainer_list: list[  vertice_param_position_container ]
    sum_edgelength: Callable
    edgelength: list[ float ]

    graphnodes_list = list( gridgraph.nodes() )
    edges_list = edges_to_vertices_from_graph( graphnodes_list, gridgraph )
    edgelength = [ 0 for e in edges_list ]
    down, up, left, right = ( [ graphnodes_list.index(v) for v in line ] \
                                for line in border )
    variablenodes = set(range( len( graphnodes_list ) ))
    for line in ( down, up, left, right ):
        variablenodes.difference_update( line )

    vertice_positions = estimate_startpositions( len(graphnodes_list), \
                                                        edges_list, up, left, \
                                                        down, right )
    vertice_indexcontainer_list = list( vertice_param_position_container(i) \
                                for i in range(len( vertice_positions )) \
                                if i in variablenodes )
    vertice_indexcontainer_list_border = list( \
                                vertice_param_position_container(i) \
                                for i in range(len( vertice_positions )) \
                                if i not in variablenodes )
    maxindex = max( v.maxindex for v in vertice_indexcontainer_list )
    params = np.zeros( ( maxindex+1, ) )
    for v in vertice_indexcontainer_list:
        i = v.vertexindex
        params[ v.u_index ], params[ v.v_index ] = vertice_positions[ i ]
    energy, grad_energy_to_params = _get_minimize_function_springenergy(\
                                    vertice_indexcontainer_list, \
                                    vertice_indexcontainer_list_border, \
                                    vertice_positions, \
                                    edges_list, edgelength,
                                    surfacemap )

    mybounds = [(0,1)]*len(params)
    foundparams = minimize( energy, params, jac = grad_energy_to_params, \
                                        bounds=mybounds, \
                                        options={ 'gtol':1e-8, 'disp':False },\
                                        )
    foundparams = foundparams.x
    foundpositions = {}
    #for i, v in enumerate( graphnodes_list ):
    for vertice_indices in vertice_indexcontainer_list:
        i = vertice_indices.vertexindex
        s = foundparams[ vertice_indices.u_index ]
        t = foundparams[ vertice_indices.v_index ]
        v = graphnodes_list[ i ]
        x, y, z = surfacemap.get_value_to_st( s, t )
        data = {}
        foundpositions[ v ] = data
        data["x"] = x
        data["y"] = y
        data["z"] = z
    for vertice_indices in vertice_indexcontainer_list_border:
        i = vertice_indices.vertexindex
        s, t = vertice_positions[ i ]
        x, y, z = surfacemap.get_value_to_st( s, t )
        v = graphnodes_list[ i ]
        data = {}
        foundpositions[ v ] = data
        data["x"] = x
        data["y"] = y
        data["z"] = z
    return foundpositions


def estimate_startpositions( number_vertices, edges_list, \
                                                    border_up, border_left, \
                                                    border_down, border_right ):
    positions = np.zeros( ( number_vertices, 2 ) )
    startpositions = np.zeros( ( number_vertices, 2 ) )
    max_up_index = len( border_up ) - 1
    for i, vindex in enumerate( border_up ):
        startpositions[ vindex ] = ( i/max_up_index, 1 )
    max_down_index = len( border_down ) - 1
    for i, vindex in enumerate( border_down ):
        startpositions[ vindex ] = ( i/max_down_index, 0 )
    max_left_index = len( border_left )-1
    for i, vindex in enumerate( border_left ):
        startpositions[ vindex ] = ( 0, i/max_left_index )
    max_right_index = len( border_right )-1
    for i, vindex in enumerate( border_right ):
        startpositions[ vindex ] = ( 1, i/max_right_index )

    interaction_matrix = lil_matrix( (number_vertices, number_vertices) )
    for v1, v2 in edges_list:
        interaction_matrix[v1,v1] -= 1
        interaction_matrix[v2,v2] -= 1
        interaction_matrix[v1,v2] += 1
        interaction_matrix[v2,v1] += 1
    for v in chain(border_up, border_down, border_left, border_right):
        for i in range( number_vertices ):
            interaction_matrix[ v, i ] = 0
        interaction_matrix[ v, v ] = 1

    positions = spsolve( interaction_matrix.tocsr(), startpositions )
    return positions


def edges_to_vertices_from_graph( verticeindices, gridgraph ):
    edgelist = []
    for e in gridgraph.edges():
        v1, v2 = e[:2]
        index1 = verticeindices.index( v1 )
        index2 = verticeindices.index( v2 )
        edgelist.append( (index1, index2) )
    return edgelist


def _get_minimize_function_springenergy( \
                    vertice_list: list[vertice_param_position_container],
                    vertice_list_border: list[vertice_param_position_container],
                    startpositions: list[ Tuple[ float, float]],
                    edges: list[ Tuple[ int, int ]], \
                    edgelength: list[ float ], \
                    surfacemap, \
                    ) -> Tuple[ Callable, Callable ]:
    """
    create energy based on formular
    """
    if not len(vertice_list) + len(vertice_list_border) == len(startpositions):
        raise Exception( "sourcecode error, got different length",\
                            len(vertice_list), len(vertice_list_border), \
                            len(startpositions))
    if not len( edges) == len(edgelength):
        raise Exception( "sourcecode error, got different length" )
    len_allvertices = len(vertice_list) + len(vertice_list_border)
    len_params = len( vertice_list ) * 2
    default_position_xyz = np.zeros((len(startpositions),3))
    for v in chain( vertice_list, vertice_list_border ):
        i = v.vertexindex
        u, v = startpositions[ i ]
        x, y, z = surfacemap.get_value_to_st( u, v )
        default_position_xyz[ i, 0 ] = x
        default_position_xyz[ i, 1 ] = y
        default_position_xyz[ i, 2 ] = z
    inner_edges = list( filter_to_inneredges( edges, vertice_list_border ) )
    matrix_posxyz_to_edgexyz = lil_matrix(( len(inner_edges), \
                                            len(default_position_xyz) ))
    for edge_index, e in enumerate( inner_edges ):
        v1, v2 = e
        matrix_posxyz_to_edgexyz[ edge_index, v1 ] = 1
        matrix_posxyz_to_edgexyz[ edge_index, v2 ] = -1
    def foo( params ):
        position_xyz = np.array( default_position_xyz )
        for vert in vertice_list:
            u = params[ vert.u_index ]
            v = params[ vert.v_index ]
            x, y, z = surfacemap.get_value_to_st( u, v )
            position_xyz[ vert.vertexindex, : ] = (x, y, z)
        edge_xyz = matrix_posxyz_to_edgexyz * position_xyz
        edge_lengths_square = np.square( np.linalg.norm( edge_xyz, axis=1 ) )
        q = sum( edge_lengths_square )
        return q
    matrix_u_array_to_params = dok_matrix((len_allvertices, len_params))
    matrix_v_array_to_params = dok_matrix((len_allvertices, len_params))
    for vert in vertice_list:
        i = vert.vertexindex
        u = vert.u_index
        v = vert.v_index
        matrix_u_array_to_params[ i, u ] = 1
        matrix_v_array_to_params[ i, v ] = 1
    matrix_u_array_to_params = matrix_u_array_to_params.tocsr()
    matrix_v_array_to_params = matrix_v_array_to_params.tocsr()

    def grad_foo( params ):
        position_xyz = np.array( default_position_xyz )
        dxyz_dst = np.zeros( (len(startpositions), 2, 3) )
        for vert in vertice_list:
            u = params[ vert.u_index ]
            v = params[ vert.v_index ]
            x, y, z = surfacemap.get_value_to_st( u, v )
            position_xyz[ vert.vertexindex, : ] = (x, y, z)
            dxyz_dst[ vert.vertexindex, :, : ] \
                            = surfacemap.get_derivate_to_st( u, v )
        edge_xyz = matrix_posxyz_to_edgexyz * position_xyz
        asd = edge_xyz.T * matrix_posxyz_to_edgexyz
        a = np.sum( dxyz_dst[:,0,:] * asd.T, axis = 1 )
        b = np.sum( dxyz_dst[:,1,:] * asd.T, axis = 1 )
        gradparams = a * matrix_u_array_to_params
        gradparams += b * matrix_v_array_to_params
        return gradparams

    return foo, grad_foo

def filter_to_inneredges( edges_list, border ):
    border_vertices = set( v.vertexindex for v in border )
    for v1, v2 in edges_list:
        if not( v1 in border_vertices and v2 in border_vertices ):
            yield (v1, v2)
