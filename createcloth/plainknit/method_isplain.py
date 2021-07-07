from .state import start, end, leftplane, rightplane, \
                    lefteaves, righteaves, enddecrease, \
                    plain, increase, decrease

def isplain( linetypes ):
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
