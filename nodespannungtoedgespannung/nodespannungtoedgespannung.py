import networkx as netx

def main( grid, valuename ):
    a,b,c = create_solutionspace( grid )
    values = netx.get_node_attributes( grid, valuename )
    fill_loesungspace_with_nodevalues( a, b, c, values )

def create_solutionspace( grid ):
    """
    creates a with zero filled numpy array as space for calculations
    :rparam loesungsspace: numpy.array with zeros
    :rtype loesungsspace: numpy.array
    :rparam nodetoindex_dict: corresponds to given node an index of loesungspace
    :rtype nodetoindex_dict: dict
    :rparam edgetoindex_dict: corresponds to given edge an index of loesungspace
    :rtype edgetoindex_dict: dict
    """
    mynodes = grid.nodes()
    myedges = grid.edges()
    loesungsspace = np.zeros(( len(mynodes) + len(myedges), ))
    nodetoindex_dict = dict()
    edgetoindex_dict = dict()
    i=0
    for node in mynodes:
        nodetoindex_dict.update({ node:i })
        i = i+1
    for edge in myedges:
        edgetoindex_dict.update({ edge:i })
        i = i+1

    return loesungspace, nodetoindex_dict, edgetoindex_dict


def fill_loesungspace_with_nodevalues( loesungspace, node_to_values, \
                                                    nodetoindex_dict ):
    """
    :type loesungspace: numpy.array
    :type node_to_values: dict
    :type nodetoindex_dict: dict
    """
    for node in node_to_values:
        i = nodetoindex_dict[ node ]
        value = node_to_value[ node ]
        loesungspace[i] = value

def create_connectionmatrix( grid ):
    """
    Creates a lilmatrix, which shows the connectionsbetween nodes on the edges
    every node corresponds a value. this value reflect in a value corresponding
    to the edges:
    value_edge = 0.5 * ( value_node1 + value_node2 )
    the matrix gives a solutionmatrix for this problem, when you dont know the
    values on the edges but only on the nodes. in the loesungsspace nodes are
    initialized with their value and the edges with 0
    """
    
    loesungsmatrix = scipy.sparse.lil_matrix( len(loesungspace), \
                                                len(loesungspace))
    for node in nodetoindex_dict:
        i = nodetoindex_dict[ node ]
        loesungsmatrix[i, i] = 1

    for edge in edgetoindex_dict:
        node1 = edge[0]
        node2 = edge[1]
        index_edge = edgetoindex_dict[ edge ]
        index_node1 = nodetoindex_dict[ node1 ]
        index_node2 = nodetoindex_dict[ node2 ]
        loesungsmatrix[index_edge, index_edge] = -2
        loesungsmatrix[index_edge, index_node1] = 1
        loesungsmatrix[index_edge, index_node2] = 1

