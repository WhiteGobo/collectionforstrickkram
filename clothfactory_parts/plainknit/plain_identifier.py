import networkx as netx
from collections import Counter
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
        leftplane, rightplane
        lefteaves, righteaves
    left and right rand in one line have the same structure
    all other knots (innerknots) are only 'knit'
    innerlinelength is at least 10 knots wide
"""

id_array = [ "leftplane", "rightplane", "lefteaves", "righteaves", \
                "start", "end", "enddecrease", "plain", "increase", "decrease"]
def _id_lefteaves( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "yarnover" )):
        if all(( mytype == "yarnover" \
                for mytype in line_stitchtypes[ :mycount["yarnover"] ] )):
            return "lefteaves"
    return False
def _id_righteaves( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "yarnover" )):
        if all(( mytype == "yarnover" \
                for mytype in line_stitchtypes[ mycount["knit"]: ] )):
            return "righteaves"
    return False
def _id_leftplain( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "bindoff" )):
        if all(( mytype == "bindoff" \
                for mytype in line_stitchtypes[ :mycount["bindoff"] ] )):
            return "leftplane"
    return False
def _id_rightplain( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "bindoff" )):
        if all(( mytype == "bindoff" \
                for mytype in line_stitchtypes[ mycount["knit"]: ] )):
            return "rightplane"
    return False
def _id_start( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "yarnover", )):
        return "start"
    return False
def _id_end( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "bindoff", )):
        return "end"
    return False
def _id_enddecrease( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "bindoff", "bind2off" )):
        if \
                mycount["bind2off"] == 2 \
                and line_stitchtypes[2] == "bind2off" \
                and line_stitchtypes[-3] == "bind2off":
            return "enddecrease"
    return False
def _id_plain( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", )):
        return "plain"
    return False
def _id_increase( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "yarnover" )):
        if \
                mycount["yarnover"] == 2 \
                and line_stitchtypes[2] == "yarnover" \
                and line_stitchtypes[-3] == "yarnover":
            return "increase"
    return False
def _id_decrease( line_stitchtypes ):
    mycount = Counter( line_stitchtypes )
    if mycount.keys() == set(( "knit", "k2tog" )):
        if \
                mycount["k2tog"] == 2 \
                and line_stitchtypes[2] == "k2tog" \
                and line_stitchtypes[-3] == "k2tog":
            return "decrease"
    return False
plain_id_array = [ _id_leftplain, _id_rightplain, _id_start, _id_end, \
                    _id_enddecrease, _id_plain, _id_increase, _id_decrease, \
                    _id_lefteaves, _id_righteaves ]


def identify_single_line( line, stitchtypes_to_node ):
    if len( line ) < 10:
        return False
    line_stitchtypes = [ stitchtypes_to_node[ node ] for node in line ]
    for identifier in plain_id_array:
        a = identifier( line_stitchtypes )
        if a:
            return a
    return False
    
class notplainException( Exception ):
    def __init__( self, linetypes, *args, failedline=None, \
                                                failedlinesequence=None ):
        if failedline:
            errormessage = \
                    "Couldnt identify strickgraph as plain following line "\
                    "was identified as not suitable for "\
                    f"plainknit: {failedline}"
            if len(failedline) < 10:
                errormessage += "\nline is too short, min: 10"
        elif failedlinesequence:
            errormessage = \
                    f"""
                    couldnt identify strickgraph as plain. following line
                    sequence contradicts plainknit: {failedlinesequence}
                    """
        super().__init__( errormessage, linetypes, *args )
        self.linetypes = linetypes
        self.failedline = failedline
        self.failedlinesequence = failedlinesequence


def getplainknit_linetypes( mystrickgraph ):
    f"""
    This method identify a whole strickgraph and return linetype as listed
    in {__name__}.id_array. Returns False if fails

    First identify every line as one linetype listed in {__name__}.id_array
    Second check every exclusion criterion

    :rtype: list or boolean
    """
    stitchtypes_to_node = netx.get_node_attributes( mystrickgraph,"stitchtype")
    rows = mystrickgraph.get_rows()
    linetype = []
    for row in rows:
        tmp = identify_single_line( row, stitchtypes_to_node )
        if not tmp:
            raise notplainException( linetype, \
                            failedline=[stitchtypes_to_node[e] for e in row])
        linetype.append( tmp )

    #check if planes are on both sides
    for i in range( len(linetype) ):
        a = linetype[i]
        if a in ("leftplane", "rightplane"):
            if not( linetype[i+1] in ("leftplane", "rightplane") \
                        or linetype[i-1] in ("leftplane", "rightplane")):
                raise notplainException( linetype, \
                            failedlinesequence=linetype[i-1:i+2] )
    #check if eaves are on both sides
    for i in range( len(linetype) ):
        a = linetype[i]
        if a in ("lefteaves", "righteaves"):
            if not( linetype[i+1] in ("lefteaves", "righteaves") \
                        or linetype[i-1] in ("lefteaves", "righteaves")):
                raise notplainException( linetype, \
                            failedlinesequence=linetype[i-1:i+2] )
    return linetype


def isplain( mystrickgraph ):
    try:
        return getplainknit_linetypes( mystrickgraph )
    except notplainException:
        return False
