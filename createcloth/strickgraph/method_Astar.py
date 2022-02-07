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
    def __repr__( self ):
        return "inf"

_infty = _class_infty()

class TargetUnreachable( Exception ):
    """This Exception should be used if method mindist detects an 
    unreachable target from the given node. 
    See InputDelcaration.pathnode.mindist for further information
    """
    pass

def greedy( source, targets ):
    cameFrom: dict[ pathnode, Iterable[pathnode] ] = {}
    edgebetween = {}
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
    openSets = [{source}]
    visited_nodes = []
    global currentnode
    currentnode = None
    def gather_next_currentnode():
        global currentnode
        while openSets:
            current_openSet = openSets[ -1 ]
            q = sorted( current_openSet, key= predicted_pathlength.get )
            for n in q:
                current_openSet.remove( n )
                if n not in visited_nodes:
                    currentnode = n
                    visited_nodes.append( currentnode )
                    return True
            openSets.pop( -1 )
        return False
    while gather_next_currentnode():
        #print( "\n", currentnode, currentnode in visited_nodes, len( visited_nodes))
        try:
            if currentnode in targets:
                return reconstruct_path( currentnode )
        except Exception:
            raise Exception( targets, currentnode )
        startdistance = traveled_pathlength[ currentnode ]
        new_openSet = set()
        openSets.append( new_openSet )
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
                if neigh not in visited_nodes:
                    new_openSet.add( neigh )
    raise ValueError( "No Path found" )

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
    edgebetween = {}
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

    openSet = { source }
    nextnodekey = lambda node: ( \
            predicted_pathlength[node], \
            traveled_pathlength[node])
    visited_nodes = []
    while openSet:
        q = sorted( openSet, key= nextnodekey )
        currentnode = q[0]

        if currentnode in targets:
            return reconstruct_path( currentnode )
        q = len( openSet )
        openSet.remove( currentnode )
        q2 = len( openSet )
        #print( "\n", currentnode, q, q2 )

        startdistance = traveled_pathlength[ currentnode ]
        for neigh, extradistance, edgetype in currentnode.neighbours():
            tentative_finallength = startdistance + extradistance
            if traveled_pathlength.get( neigh, _infty ) > tentative_finallength:
                try:
                    min_distance = find_goal_distance( neigh )
                except TargetUnreachable:
                    continue
                #print( edgetype, traveled_pathlength.get( neigh, _infty ), tentative_finallength, tentative_finallength+min_distance )
                #print( neigh )
                cameFrom[ neigh ] = currentnode
                edgebetween[ currentnode, neigh ] = edgetype
                traveled_pathlength[ neigh ] = tentative_finallength
                predicted_pathlength[ neigh ] = tentative_finallength \
                                                + min_distance
                openSet.add( neigh )
            #if newOpenSet:
            #    openSet = newOpenSet
        #input()
    q = sorted( predicted_pathlength, key= nextnodekey )
    #print( q )
    raise ValueError( "No Path found" )
