from typing import Iterable, Dict, Hashable, Iterator, Tuple
import itertools as it

def strickgraph_to_border( rows, edges_with_direction, nodetoside ):
    """Finds the border of given graph. border is clockwise.

    :type rows: Iterable[ Iterable[ Hashable ] ]
    :param rows: Rows of nodes. Must be sorted from left to right, 
            and last row must be top-row
    :type edges_with_direction: Iterable[ Tuple[Hashable, Hashable, str]]
    :param edges_with_direction: List of all edges with direction 'next' or 'up'
    :type nodetoside: Dict[ Hashable, str ]
    :param nodetoside: Mapping of nodes to side 'left' or 'right'
    :rtype: Iterable[ Hashable ]
    :returns: Clockwise border of graph
    :todo: document how rows must be sorted
    """
    #edges_with_direction = mystrick.get_edges()
    #rows = mystrick.get_rows()
    #nodetoside = mystrick.get_nodeside()
    upneighbours, downneighbours, leftneighbour, rightneighbour \
            = edges_to_directional_neighbours( edges_with_direction, nodetoside )
    
    get_clock_neigh = lambda node, direction:  neighbournode_clockwise( \
                                    node, upneighbours, downneighbours, \
                                    leftneighbour, rightneighbour, \
                                    direction, nodetoside, rows )

    border = [ rows[-1][0] ]
    lastdirection = "right"# if nodetoside[border[-1]]=="right" else "left"
    for i in upneighbours:
        n = border[ -1 ]
        neighs = get_clock_neigh( n, lastdirection )
        nextnode, nextdirection = iter( neighs ).__next__()
        if nextnode == border[0]:
            break
        else:
            border.append( nextnode )
            lastdirection = nextdirection
    return border
        

def neighbournode_clockwise( node, upneighbours, downneighbours, \
                                    leftneighbour, rightneighbour, \
                                    startdirection, nodetoside, \
                                    rows, rowindex=None ) \
                                    -> Iterator[ Tuple[ Hashable, str ] ]:
    """Sort neighbours clockwise, starting with given startdirection. Binds
    to each neighbour the walkdirection as string
    """
    assert startdirection  in ( "left", "right", "up", "down" )
    if rowindex is None:
        rowindex = [ i for i, line in enumerate(rows) if node in line ][0]
    ups = list( upneighbours.get( node, []) )
    right = rightneighbour.get( node, None )
    rights = [right] if right is not None else []
    downs = list( downneighbours.get( node, []) )
    left = leftneighbour.get( node, None)
    lefts = [left] if left is not None else []
    if nodetoside[ node ] == "left":
        if ups:
            ups.sort( reverse=True, key=rows[ rowindex+1 ].index )
        if downs:
            downs.sort( reverse=False, key=rows[ rowindex-1 ].index )
    else:
        if ups:
            ups.sort( reverse=False, key=rows[ rowindex+1 ].index )
        if downs:
            downs.sort( reverse=True, key=rows[ rowindex-1 ].index )

    d_lefts = ("left" for i in lefts)
    d_rights = ("right" for i in rights)
    d_ups = ("up" for i in ups)
    d_downs = ("down" for i in downs)
    if startdirection == "up":
        nodes = it.chain( lefts, ups, rights, downs )
        direction = it.chain( d_lefts, d_ups, d_rights, d_downs )
    elif startdirection == "right":
        nodes = it.chain( ups, rights, downs, lefts )
        direction = it.chain( d_ups, d_rights, d_downs, d_lefts )
    elif startdirection == "down":
        nodes = it.chain( rights, downs, lefts, ups )
        direction = it.chain( d_rights, d_downs, d_lefts, d_ups )
    else:
        nodes = it.chain( downs, lefts, ups, rights )
        direction = it.chain( d_downs, d_lefts, d_ups, d_rights )
    return zip( nodes, direction )

def edges_to_directional_neighbours( edges_with_direction, nodetoside ):
    """Creates for each cardinal direction one dictionary. left and right
    are only single nodes, while up and down are list of nodes
    """
    upneighbours, downneighbours, leftneighbour, rightneighbour = {}, {}, {}, {}
    for v1, v2, direction in edges_with_direction:
        if direction == "up":
            upneighbours.setdefault( v1, list() ).append( v2 )
            downneighbours.setdefault( v2, list() ).append( v1 )
        elif direction == "next":
            if nodetoside[v1] == "left" and nodetoside[v2] == "left":
                leftneighbour[v1] = v2
                rightneighbour[v2] = v1
            elif nodetoside[v1] == "right" and nodetoside[v2] == "right":
                leftneighbour[v2] = v1
                rightneighbour[v1] = v2
            elif nodetoside[v1] == "left" and nodetoside[v2] == "right":
                upneighbours.setdefault( v1, list() ).append( v2 )
                downneighbours.setdefault( v2, list() ).append( v1 )
            elif nodetoside[v1] == "right" and nodetoside[v2] == "left":
                upneighbours.setdefault( v1, list() ).append( v2 )
                downneighbours.setdefault( v2, list() ).append( v1 )
    return upneighbours, downneighbours, leftneighbour, rightneighbour

        
