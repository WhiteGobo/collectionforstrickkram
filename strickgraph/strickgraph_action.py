import networkx as netx
import strickgraph_stitchtypes as stitchtypes
from networkx.classes.reportview import InEdgeView, OutEdgeView

def sanity_check( strickgraph ):
    """
    :rtype: boolean
    :return: returns True if graph is valid and False if Graph is not
    """
    return True


def insert_node( insertedge, strickgraph, nodetype, nodeidentifier=None ):
    if nodetype not in stitchtypes.stitchtypes:
        raise Exception( "stitchtype %s is not implemented" %(repr(nodetype)))
    edgetype = netx.get_edge_attributes( strickgraph, "edgetype" )[insertedge]
    if edgetype != "next":
        raise Exception( "can only insert at edgetype next" )

    if None == nodeidentifier:
        nodeidentifier = find_newnodename( strickgraph )
    
    strickgraph.remove_edge( insertedge )
    strickgraph.add_node( nodeidentifier, nodetype=nodetype )
    strickgraph.add_edge( insertedge[0], nodeidentifier, edgetype="next" )
    strickgraph.add_edge( nodeidentifier, insertedge[1], edgetype="next" )
    return nodeidentifer

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
    edges = netx.get_node_attributes( strickgraph, "edgetype" )
    nextedges = [ x for x in edges if edges[x] == "next" ]
    areatobeworkedon = []
    toprightnode  = helper.fetch_next_node( strickgraph, topleftnode )
    areatobeworkdon.append( (topleftnode, toprightnode) )
    for dy in range( 1, deep ):
        tmpnode1 = helper.descend_row_keepright( strickgraph, toprightnode )
        tmpnode2 = helper.descend_row_keepright( strickgraph, topleftnode )
        areatobeworkdon.append( (tmpnode1, tmpnode2) )
    #deep-1 equals -1:
    lastnode = insertnode( strickgraph, areatobeworkedon[-1][0], \
                                        areatobeworkedon[-1][1] )
    thisnode = None
    for dy in range( 1, deep-1 ):
        thisnode = insertnode( strickgraph, areatobeworkedon[-1-dy][0], \
                                            areatobeworkedon[-1-dy][1] )
        strickgraph.add_edge( lastnode, thisnode, edgetype = "up" )
        lastnode = thisnode
    netx.set_node_attributes( strickgraph, topleftnode, nodetype="k2tog" )
    strickgraph.add_edge( lastnode, topleftnode, edgetype = "up" )


