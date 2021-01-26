import networkx as netx

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors



def myvis3d( mystrickgraph ):
    test_if_all_nodes_are_there( mystrickgraph )
    x = netx.get_node_attributes( mystrickgraph, "x" )
    y = netx.get_node_attributes( mystrickgraph, "y" )
    z = netx.get_node_attributes( mystrickgraph, "z" )

    graph = mystrickgraph

    myarray = []
    for node in set(mystrickgraph.nodes()).difference(["start", "end"]):
        myarray.append( [ x[node], y[node], z[node] ])
    myarray = np.array( myarray )
    myarray = myarray.T

    edgelist = []
    length = netx.get_edge_attributes( graph, "tension" )
    for tmpedge in graph.in_edges("end", keys=True ):
        length.pop( tmpedge )
    for tmpedge in graph.out_edges( "start", keys=True ):
        length.pop( tmpedge )
    minima, maxima = length[ list(length)[0] ], length[ list(length)[0] ]
    for tmpedge in length:
        try:
            tmpxs = ( x[tmpedge[0]], x[tmpedge[1]] )
            tmpys = ( y[tmpedge[0]], y[tmpedge[1]] )
            tmpzs = ( z[tmpedge[0]], z[tmpedge[1]] )
        except KeyError as err:
            err.args = ( *err.args, length )
            raise err
        edgelist.append((tmpxs, tmpys, tmpzs, length[ tmpedge ]))
        minima = min( minima, length[ tmpedge ])
        maxima = max( maxima, length[ tmpedge ])



    norm = colors.Normalize( vmin=minima, vmax =maxima, clip=True)
    mapper = cm.ScalarMappable( norm=norm, cmap=cm.coolwarm_r )
    fig = plt.figure()
    ax = fig.add_subplot( 111, projection='3d')
    #ax.scatter( myarray[0], myarray[1], myarray[2] )

    for tmpedge in edgelist:
        ax.plot( tmpedge[0], tmpedge[1], tmpedge[2], \
                        color=mapper.to_rgba(tmpedge[3]) )
    plt.show()

def test_if_all_nodes_are_there( mystrickgraph ):
    x = netx.get_node_attributes( mystrickgraph, "x" )
    y = netx.get_node_attributes( mystrickgraph, "y" )
    z = netx.get_node_attributes( mystrickgraph, "z" )
    allnodes = set().union( \
            x.keys(), \
            y.keys(), \
            z.keys(), \
            mystrickgraph.nodes(), \
            )
    allnodes = allnodes.difference( ["start", "end"] )
    for node in allnodes:
        if node not in x:
            raise Exception( node, "x", x )
        elif node not in y:
            raise Exception( node, "y", y )
        elif node not in z:
            raise Exception( node, "z", z )
        elif node not in mystrickgraph.nodes():
            raise Exception( node, "graphnodes", mystrickgraph.nodes() )
