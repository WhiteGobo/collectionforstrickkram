def fetch_neighbour_to_row( graph, row ):
    neighbours = []
    for node in row:
        tmpneighbours = graph.neighbors( node )
        neighbours = neighbours + [ newnode for newnode in tmpneighbours \
                                                if newnode not in row
                                                and newnode not in neighbours]
    return neighbours

def fetch_next_node( strickgraph, node ):
    nodeedges = strickgraph.edges( node )
    nodeattributes = netx.get_node_attributes( strickgraph, "edgetype")
    for tmpedge in nodeedges:
        if tmpedge[0] == node and nodeattributes[ tmpedge ] == "next":
            nextnode = tmpedge[1]
    return nextnode

def fetch_previous_node( strickgraph, node ):
    nodeedges = strickgraph.edges( node )
    nodeattributes = netx.get_node_attributes( strickgraph, "edgetype")
    for tmpedge in nodeedges:
        if tmpedge[1] == node and nodeattributes[ tmpedge ] == "next":
            nextnode = tmpedge[0]
    return nextnode

_keep_right = 0
_keep_left = 1
_descend_library= {}
def descend_row_keepright( strickgraph, node ):
    """
    return the node below the given node on the right
    :type strickgraph: strickgraph
    """
    nodetype = netx.get_node_attributes( strickgraph, "nodetype" )[ node ]
    return _descend_library[ ( _keep_right, nodetype ) ]( strickgraph, node )

def _knit_descend_row_keepright( strickgraph, node ):
    """
    like for _knit_descend_row_keepright
    :param node: has to be of nodetype knit
    """
    nodeedges = strickgraph.edges( node )
    nodeattributes = netx.get_node_attributes( strickgraph, "edgetype")
    possible_edges = []
    for tmpedge in nodeedges:
        if tmpedge[1] == node and nodeattributes[ tmpedge ] == "up":
            return tmpedge


_descend_library.update({ ("knit", _keep_right):_knit_descend_row_keepright} )
    

def sort_rows_as_snake( graph, rows, firstrow ):
    """
    sort all rows so that you can lay eeach row subsequently in order as
    a snake. lastelements of previous rows connect to first element in current
    :rtype sortedrows: list of tuples
    :rparam sortedrows: list where each row is sorted
    :param firstrow: list or tuple of a sorted firstrow
    :param rows: list of all rows, each row is list of points, points are hashs
    """
    newrows = [ firstrow ]
    sortedlastrow = firstrow
    for currentrow in rows[1:]: #firstrow is index 0
        sortedrow = []
        tmpelements = graph.neighbors( sortedlastrow[-1] )
        tmpelements = [x for x in tmpelements if x in currentrow]
        if len(tmpelements)>1:
            raise strick_NotImplementedError( "no climb stitch can have more "\
                                                + "than 1 upper neighbour")
        elif len(tmpelements) == 0:
            raise strick_NotValid("no first climb stitch found")
        sortedrow.append( tmpelements[0] )
        while len(sortedrow) < len(currentrow):
            thisnode = sortedrow[-1]
            tmpelements = graph.neighbors( thisnode )
            tmpelements = [ x for x in tmpelements if x in currentrow \
                                                and x not in sortedrow ]
            if len(tmpelements) != 1:
                raise strick_NotValid("not connect row given or too many "\
                                    +"too many neighbours of a node in a row" \
                                    +"; Number of neighbours: %d" \
                                    %(len(tmpelements)))
            sortedrow.append(tmpelements[0])
        sortedlastrow = sortedrow
        newrows.append( sortedrow )
    return newrows


class strick_NotImplementedError( Exception ):
    pass
class strick_NotFoundError( Exception ):
    pass
class strick_NotValid( Exception ):
    """
    This Exception symbolises that the generator cant fulfill his task with 
    given parameters
    """
    pass


def separate_to_rows( graph, firstrow ):
    visited = [x for x in firstrow] #copy
    rows = [ firstrow ]
    nextrow = fetch_neighbour_to_row( graph, firstrow )
    while len( nextrow )>0:
        rows.append(nextrow)
        visited = visited + nextrow
        nextrow = fetch_neighbour_to_row( graph, visited )
    return rows


def firstrow_to_stitches( graph, rows, rownumber=0 ):
    if rownumber!=0:
        raise Exception("the first row has to be in firstplace")
