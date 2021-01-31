"""
These functions are for manipulating single stitches
These functions are obsolete. There should be only graph-substitution
:todo: substitue all these functions with graph-substitution
"""
import networkx as netx
from . import strickgraph_stitchtypes as stitchtypes
from networkx.classes.reportviews import InEdgeView, OutEdgeView
from . import strickgraph_helper as helper

def sanity_check( strickgraph ):
    """
    :rtype: boolean
    :return: returns True if graph is valid and False if Graph is not
    """
    return True


def insert_node( insertnode1, insertnode2, strickgraph, nodetype, \
                                        nodeidentifier=None ):
    """
    :todo:remake error throwing for only the baseclass strickgraph
    """
    insertedge = (insertnode1, insertnode2)
    if nodetype not in stitchtypes.stitchtypes:
        raise Exception( "stitchtype %s is not implemented" %(repr(nodetype)))
    try:
        edgetype = netx.get_edge_attributes( strickgraph,"edgetype")[(*insertedge,0)]
    except KeyError:
        insertedge = (insertedge[1], insertedge[0])
        edgetype = netx.get_edge_attributes( strickgraph,"edgetype")[(*insertedge,0)]
    if edgetype != "next":
        raise Exception( "can only insert at edgetype next" )

    if None == nodeidentifier:
        nodeidentifier = find_newnodename( strickgraph )
    
    strickgraph.remove_edge( insertedge[0], insertedge[1] )
    strickgraph.add_node( nodeidentifier, nodetype=nodetype )
    strickgraph.add_edge( insertedge[0], nodeidentifier, edgetype="next" )
    strickgraph.add_edge( nodeidentifier, insertedge[1], edgetype="next" )
    return nodeidentifier

def cut_node( node, strickgraph ):
    prevnode, nextnode = None, None
    attributes = netx.get_edge_attributes( strickgraph, "edgetype" )
    adjacentedges = strickgraph.edges( node )
    for tmpedge in adjacentedges:
        if attributes[tmpedge] == "next" and tmpedge[0] == node:
            nextnode = tmpedge[1]
        elif attributes[tmpedge] == "next" and tmpedge[1] == node:
            prevnode = tmpedge[0]
    strickgraph.add_edge( prevnode, nextnode, edgetype="next" )


def find_newnodename( strickgraph ):
    nodeidentifier = 0
    while nodeidentifier in strickgraph.nodes():
        nodeidentifier = nodeidentifier + 1
    return nodeidentifier


def insert_column_onlyknits( strickgraph, topleftnode, deep ):
    if topleftnode not in strickgraph.nodes():
        raise Exception("node where to insert is not in graph, node:%s" \
                %( repr(topleftnode) ))
    edges = netx.get_node_attributes( strickgraph, "edgetype" )
    nextedges = [ x for x in edges if edges[x] == "next" ]
    areatobeworkedon = []
    toprightnode  = helper.fetch_next_node( strickgraph, topleftnode )
    areatobeworkedon.append( (topleftnode, toprightnode) )
    tmpnode1, tmpnode2 = toprightnode, topleftnode
    for dy in range( 1, deep ):
        tmpnode1 = helper.descend_row_keepright( strickgraph, tmpnode1 )
        tmpnode2 = helper.descend_row_keepright( strickgraph, tmpnode2 )
        areatobeworkedon.append( (tmpnode1, tmpnode2) )
    #deep-1 equals -1:
    lastnode = insert_node( areatobeworkedon[-1][0], areatobeworkedon[-1][1],\
                            strickgraph, "knit" )
    thisnode = None
    for dy in range( 1, deep-1 ):
        thisnode = insert_node( areatobeworkedon[-1-dy][0], \
                        areatobeworkedon[-1-dy][1],strickgraph, "knit" )
        strickgraph.add_edge( lastnode, thisnode, edgetype = "up" )
        lastnode = thisnode
    netx.set_node_attributes( strickgraph, {topleftnode:"k2tog"}, "nodetype" )
    strickgraph.add_edge( lastnode, topleftnode, edgetype = "up" )



