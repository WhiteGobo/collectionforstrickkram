import numpy as np
from scipy.sparse.linalg import spsolve as solve
import networkx as netx
import itertools as it

def solve_gridspringgraph( rectangle_minmax_xy, rand, calcgraph ):
    amin, amax = rectangle_minmax_xy[0]
    bmin, bmax = rectangle_minmax_xy[1]
    graph, randnodes_to_mapposition_dict = _set_randposition( amin, amax, \
                                                            bmin, bmax, \
                                                            rand,\
                                                            calcgraph )

    nodevalues = _calculate_initialposition(rand[0]+rand[1]+rand[2]+rand[3],\
                                            calcgraph, \
                                            randnodes_to_mapposition_dict )
    
    returnlist = []
    for i in range( 2 ):
        tmp_nodeattr = [ "x", "y" ][i]
        tmpdict = { node: nodevalues[node][i] for node in nodevalues }
        returnlist.append( tmpdict )
    return returnlist


    for i in range(2):
        tmp_nodeattr = ["xmap", "ymap", "xreal", "yreal", "zreal"][ i ]
        tmpdict = { node:nodevalues[node][ i ] for node in nodevalues }
        netx.set_node_attributes( calcgraph, tmpdict, tmp_nodeattr )
    raise Exception( tmpdict )
    return calcgraph


def _set_randposition( amin, amax, bmin, bmax, rand, calcgraph ):
    """
    sets border position with euidistants nodes
    """
    (down, up, left, right) = rand #mass assignment
    #amin = surfacemap.xmin()
    #bmin = surfacemap.ymin()
    #amax = surfacemap.xmax()
    #bmax = surfacemap.ymax()

    #nodetypes = { x:"constantposition" for x in up+down+left+right }
    #netx.set_node_attributes( calcgraph, nodetypes, "calctype" )

    # map coord are a,b; real coords are x,y,z
    nodevalues = {}
    for tmpnode in down:
        i = down.index( tmpnode )
        a = amin + (amax-amin)*(i/(len(down)-1)) #ranges from 0 to 1
        nodevalues.update( {tmpnode:( a, bmin )} )
        #x, y, z = surfacemap( a, bmin )
        #nodevalues.update( {tmpnode:( a, bmin, x, y, z )} )
    for tmpnode in up:
        i = up.index( tmpnode )
        a = amin + (amax-amin)*(i/(len(up)-1)) #ranges from 0 to 1
        nodevalues.update( {tmpnode:( a, bmax )} )
        #x, y, z = surfacemap( a, bmax )
        #nodevalues.update( {tmpnode:( a, bmax, x, y, z )} )
    for tmpnode in left:
        i = left.index( tmpnode )
        b = bmin + (bmax-bmin)*(i/(len(left)-1)) #ranges from 0 to 1
        nodevalues.update( {tmpnode:( amin, b )} )
        #x, y, z = surfacemap( amin, b )
        #nodevalues.update( {tmpnode:( amin, b, x, y, z )} )
    for tmpnode in right:
        i = right.index( tmpnode )
        b = bmin + (bmax-bmin)*(i/(len(right)-1)) #ranges from 0 to 1
        nodevalues.update( {tmpnode:( amax, b )} )
        #x, y, z = surfacemap( amax, b )
        #nodevalues.update( {tmpnode:( amax, b, x,y,z )} )
    #for i, tmp_nodeattr in it.zip_longest( range(5), ["mapa", \
    #                                   "mapb", "realx", "realy", "realz"] ):
    for i in range(2):
        tmp_nodeattr = ["mapa", "mapb", "realx", "realy", "realz"][ i ]
        tmpdict = { node:nodevalues[node][ i ] for node in nodevalues }
        netx.set_node_attributes( calcgraph, tmpdict, tmp_nodeattr )
    return calcgraph, nodevalues




def _calculate_initialposition( rand, gridgraph, \
                                randnodes_to_mapposition_dict ):
    """
    :todo: remove this function
    _set_randposition must be called
    solves simple spring equations for the gridgraph. rand will be set as
    constant positions. for restnodes the equation is:
        einstein-sum-convention
        for a,b,weight in edges_to_a: a.x*weight = b.x*weight
    :todo: rand and randnodes doing the same thing, remove duplicate
    """
    #nodetypes = netx.get_node_attributes( gridgraph, "calctype" )
    #nodex = netx.get_node_attributes( gridgraph, "xmap" )
    #nodey = netx.get_node_attributes( gridgraph, "ymap" )
    #randnodes = [ node for node in nodetypes \
    #                if nodetypes[node]=="constantposition"]
    #randpositiondict = { node:( nodex[node], nodey[node] ) \
    #                    for node in randnodes }
    randpositiondict = randnodes_to_mapposition_dict
    nodemappositions = _springgrid2d_relaxation( gridgraph, \
                                                randpositiondict)
    nodevalues = {}
    for node in nodemappositions:
        xmap = nodemappositions[ node ][0]
        ymap = nodemappositions[ node ][1]
        nodevalues.update({ node:( xmap, ymap )})
        #xreal,yreal,zreal = surfacemap( xmap, ymap )
        #nodevalues.update({ node:( xmap, ymap, xreal, yreal, zreal ) })
    return nodevalues


def _springgrid2d_relaxation( viewgraph, constantposition_dict ):
    """
    relaxate a grid of points connected by spring on a PLANAR surface
    This method is used to give a starting value of the position of all the
    points on the abbildung of 3d surface to a planar surface
    :type graph: networkx.Graph; freezed
    :type constantposition_dict: dictionary
    :param constantposition_dict: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    """
    order_nodes = list( viewgraph.nodes() )
    x_sol, y_sol = _springgrid2d_createsolutionvector( viewgraph, \
                                    constantposition_dict, order_nodes )

    adj_sparsematrix = _springgrid2d_equationmatrix( viewgraph, \
                                    constantposition_dict, order_nodes )

    x_solved = solve( adj_sparsematrix, x_sol )
    y_solved = solve( adj_sparsematrix, y_sol )
    
    nodepositions = {}
    for i in range( len(order_nodes) ):
        nodepositions.update({order_nodes[i]:( x_solved[i], y_solved[i] )})
    return nodepositions

def _springgrid2d_equationmatrix( graph, position, orderedlist, \
                                    springconstant=None ):
    """
    sets matrix for equation equal to:
        einstein-sum-convention
        for a,b,weight in edges_to_a: a.x*weight = b.x*weight
    :type graph: networkx.Graph
    :type positions: dictionary
    :type orderedlist: list
    :param positions: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    :param orderedlist: list equal to graph.nodes(). gives an order for nodes
    """
    if type( graph ) != netx.Graph:
        raise Exception( "please dont use other graph types than a simple "\
                            + "networkx.Graph for springcalculations" )
    #create interaction equation for every node
    adj_sparsematrix = netx.linalg.adjacency_matrix( graph, orderedlist, \
                                                    weight = springconstant )
    adj_lilmatrix = adj_sparsematrix.tolil()
    for i in range( len( orderedlist ) ):
        tmpnode = orderedlist[i]
        adj_lilmatrix[ i,i ] = -1 * len( list(graph.neighbors( tmpnode )))

    #sets equation to constant for specific rows(j) 
    #   matrix[i][j] = (if i==j: =1; else: =0)
    for tmpnode in position:
        i = orderedlist.index( tmpnode )
        for j in range( len( orderedlist )):
            adj_lilmatrix[ i, j ] = 0
        adj_lilmatrix[ i,i ] = 1

    sparsematrix_type = type(adj_sparsematrix)
    return sparsematrix_type( adj_lilmatrix )


def _springgrid2d_createsolutionvector( graph, positions, orderedlist ):
    """
    For all the node inside the grid all springforces must sum up to 0.
    for all the edgepoints the solution is the same as the solutionvector, that 
    is created here.
    :type graph: networkx.Graph
    :type positions: dictionary
    :type orderedlist: list
    :param positions: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    :param orderedlist: list equal to graph.nodes(). gives an order for nodes
    """
    x_vector = np.zeros( len(orderedlist) )
    y_vector = np.zeros( len(orderedlist) )
    for node in positions:
        index = orderedlist.index( node )
        x_vector[ index ] = positions[ node ][0]
        y_vector[ index ] = positions[ node ][1]
    return x_vector, y_vector

