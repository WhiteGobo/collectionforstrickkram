try:
    from .InputDeclaration import pathnode
except Exception:
    pass

from typing import Iterable, Iterator

__all__=[ "Astar", "TargetUnreachable" ]

class _class_infty():
    def __gt__( self, other ):
        if other != self:
            return True
        else:
            return False

_infty = _class_infty()

class TargetUnreachable( Exception ):
    """This Exception should be used if method mindist detects an 
    unreachable target from the given node. 
    See InputDelcaration.pathnode.mindist for further information
    """
    pass

def Astar( source, targets ):
    """Pathfinding algorithm with abstract inputobject. 
    See for pseudocode: wikipedia https://en.wikipedia.org/wiki/A*_search_algorithm
    
    :param source: Startnode of path to search for
    :type source: pathnode
    :param target: Endnode of path to search for
    :type target: pathnode
    :returns: Path as list of nodes
    :rtype: Iterable[ pathnode ]
    :raises: TargetUnreachable
    """

    cameFrom: dict[ pathnode, Iterable[pathnode] ] = {}
    def reconstruct_path( target ):
        path = [ target ]
        edges = []
        while path[0] in cameFrom:
            path.insert( 0, cameFrom[ path[0] ] )
            edges.insert( 0, edgebetween[path[0], path[1]] )
        return path, edges

    traveled_pathlength = { source:0 } #use default value infty
    find_goal_distance = lambda source: min( source.mindist(t) for t in targets )
    predicted_pathlength = { source: find_goal_distance( source ) }
    edgebetween = {}

    openSet = { source }
    nextnodekey = lambda node: ( predicted_pathlength[node], \
                                    traveled_pathlength[node])
    while openSet:
        currentnode = min( openSet, key= nextnodekey )
        if currentnode in targets:
            return reconstruct_path( currentnode )
        openSet.remove( currentnode )

        startdistance = traveled_pathlength[ currentnode ]
        #print( currentnode, nextnodekey( currentnode) )
        for neigh, extradistance, edgetype in currentnode.neighbours():
            tentative_finallength = startdistance + extradistance
            if traveled_pathlength.get( neigh, _infty ) > tentative_finallength:
                try:
                    min_distance = find_goal_distance( neigh )
                except TargetUnreachable:
                    continue
                cameFrom[ neigh ] = currentnode
                edgebetween[ currentnode, neigh ] = edgetype
                traveled_pathlength[ neigh ] = tentative_finallength
                predicted_pathlength[ neigh ] = tentative_finallength \
                                                + min_distance
                openSet.add( neigh )
        #input()
    raise ValueError( "No Path found" )
