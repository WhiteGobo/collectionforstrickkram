from .examplestates import start, end, leftplane, rightplane, \
                    lefteaves, righteaves, enddecrease, \
                    plain, increase, decrease
from typing import Iterable

def isplain_strickgraph( strickgraph ):
    """Method for identification of a strickgraph, if its plainknit or not"""
    raise Exception()


def isplain( linetypes, upedges:Iterable[int]=None ):
    """method for identify plainknit"""
    if upedges is not None:
        return _isplain_with_upedges( linetypes, upedges )
    else:
        return _isplain_only_linetypes( linetypes )

def _isplain_only_linetypes( linetypes ):
    pairwise = ((rightplane, leftplane), (righteaves, lefteaves))
    middlelinetypes = ( leftplane, rightplane, lefteaves, righteaves, \
                        plain, increase, decrease )
    endlinetypes = ( end, enddecrease )
    startlinetypes = ( start, )
    linetypes = list( linetypes )

    if linetypes[ 0 ] not in startlinetypes:
        return False
    if linetypes[ -1 ] not in endlinetypes:
        return False

    skipnext = False
    for i, currentline in enumerate( linetypes[1:-1], start=1 ):
        if skipnext:
            skipnext = False
            continue
        if currentline not in middlelinetypes:
            return False
        nextline = linetypes[ i+1 ]
        for a, b in pairwise:
            if currentline == a:
                if b != nextline:
                    return False
                skipnext = True
            if currentline == b:
                if a != nextline:
                    return False
                skipnext = True
    return True


def _isplain_with_upedges( linetypes, upedges:Iterable[int] ):
    upedges = list( upedges )
    downedges = list( upedges )
    upedges.append( None )
    downedges.insert( 0, None )
    differences = [None] * len( linetypes )
    for i, tmp in enumerate( zip( upedges[1:-1], downedges[1:-1] ), start=1):
        a, b = tmp
        differences[i] = a-b

    pairwise = ((rightplane, leftplane), (righteaves, lefteaves))
    middlelinetypes = ( leftplane, rightplane, lefteaves, righteaves, \
                        plain, increase, decrease )
    endlinetypes = ( end, enddecrease )
    startlinetypes = ( start, )
    linetypes = list( linetypes )

    if min( upedges[:-1] ) < 8:
        return False

    if linetypes[ 0 ] not in startlinetypes:
        return False
    if linetypes[ -1 ] not in endlinetypes:
        return False

    skipnext = False
    for i, currentline in enumerate( linetypes[1:-1], start=1 ):
        if skipnext:
            skipnext = False
            continue
        if currentline not in middlelinetypes:
            return False
        for a, b in pairwise:
            if currentline in (a, b):
                nextline = linetypes[ i+1 ]
                if differences[i] != differences[i+1]:
                    return False
                if currentline == a:
                    if b != nextline:
                        return False
                    skipnext = True
                if currentline == b:
                    if a != nextline:
                        return False
                    skipnext = True

    for linelow, lineup in zip( linetypes[:-1], linetypes[1:] ):
        if linelow in (rightplane, leftplane) and lineup == increase:
            #This is because, they have the same stitchnumbers per line as
            #if lineup is plain
            return False
        if linelow in (rightplane, leftplane) and lineup in (decrease, enddecrease):
            #this is because you can exchange a decrease with a bigger plane
            #and still have the same stitchnumbers per line
            return False
    return True
