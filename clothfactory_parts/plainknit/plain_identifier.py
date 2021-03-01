import networkx as netx
"""
plainknit identifier
A strickgraph is plainknit if following things are true:
    top knots are only yarnover
    bottom knots are only bindoff
    left and right rand have the same one of following structures:
        plain: ('knit', 'knit','knit','knit','knit')
        increase: ('knit', 'knit', 'yarnover','knit','knit')
        doubleincrease: ('knit', 'knit', 'yarnover','knit','yarnover')
        decrease: ('knit', 'knit', 'k2tog','knit','knit')
        doubledecrease: ('knit', 'knit', 'k2tog','knit','k2tog')
    left and right rand in one line have the same structure
    all other knots (innerknots) are only 'knit'
    innerlinelength is at least 10 knots wide
"""

start = ('yarnover', 'yarnover', 'yarnover', 'yarnover', 'yarnover')
end = ('bindoff', 'bindoff', 'bindoff', 'bindoff', 'bindoff')
enddecrease = ('bindoff', 'bindoff', 'bind2off', 'bindoff', 'bindoff')
plain = ('knit', 'knit', 'knit', 'knit', 'knit')
increase = ('knit', 'knit', 'yarnover', 'knit', 'knit')
doubleincrease = ('knit', 'knit', 'yarnover', 'knit', 'yarnover')
decrease = ('knit', 'knit', 'k2tog', 'knit', 'knit')
doubledecrease = ('knit', 'knit', 'k2tog', 'knit', 'k2tog')
iddict = {plain:"plain", increase:"increase", doubleincrease:"doubleincrease", \
        decrease:"decrease", enddecrease: "enddecrease", \
        doubledecrease:"doubledecrease", start:"start", end: "end" }
rev_iddict = { value: key for key, value in iddict.items() }


def identify_single_line( line, stitchtypes_to_node ):
    if len( line ) < 10:
        return False
    line = [ stitchtypes_to_node[ entry ] for entry in line ]
    start = tuple( line[:5] )
    end = tuple( reversed(line[-5:]) )
    inner = set( line[5:-5] )
    if start in iddict.keys() and end == start: 
        if start in (plain, increase, doubleincrease, decrease, doubledecrease)\
                and inner in (set(("knit",)), set()):
            return start
        elif start in (end, enddecrease) \
                and inner in ( set(("bindoff",)), set() ):
            return start
        elif start in (start,) and inner in ( set(("yarnover",)), set() ):
            return start
    print( "\n\n\n", start, inner )
    return False

def isplain( mystrickgraph ):
    stitchtypes_to_node = netx.get_node_attributes( mystrickgraph,"stitchtype")
    rows = mystrickgraph.get_rows()
    #if rows[0] == start
    linetype = []
    for row in rows:
        tmp = identify_single_line( row, stitchtypes_to_node )
        if not tmp:
            line = [ stitchtypes_to_node[ entry ] for entry in row ]
            print( linetype, line )
            return False
        linetype.append( iddict[ tmp ] )
    #if rows[-1] == end
    return linetype
