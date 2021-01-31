import networkx as netx
from ..meshhandler import relax_strickgraph_on_surface
from ..meshhandler import weave_positiongraph_into_strickgraph

from . import rechtsstrick_verbesserer as myverbesserer
from ..verbesserer import FindError

from ..builtin_verbesserer import insertcolumn_left as verb_insertcolumn_left
from ..builtin_verbesserer import insertcolumn_right as verb_insertcolumn_right
from ..builtin_verbesserer import removecolumn_left as verb_removecolumn_left
from ..builtin_verbesserer import removecolumn_right as verb_removecolumn_right

from ..strickgraph import tomanual

def relaxgrid( grid, surfacemap ):
    datagraph = relax_strickgraph_on_surface( grid, surfacemap )
    weave_positiongraph_into_strickgraph( grid, datagraph )
    return grid

def isrelaxedenough( grid ):
    return True

def check_border_type1( grid, start, stop ):
    """
    die Aussengrenze vom Strickstueck muss mindestens 4 nodes breit sein
    an doeser aussengrenze darf es nur rechte maschen(p), yo und k2tog geben
    yo und k2tog duerfen sich nur an der dritten stelle vom reand geben
    """
    info = border_type1_expansionplaces( grid )
    currentrow = start

    while currentrow <= stop:
        if not info[ currentrow ]:
            return False
        currentrow = currentrow + 1
    return True



def border_type1_identifier( row, grid ):
    default_false = False
    sta, end, smo = "start", "end", "smooth"
    identidict={ \
            ( sta, sta, "increase", sta, sta, sta, "increase", sta):"start",\
            ( end, end, "end", end, end, end, "end", end ):"end", \
            ( smo, smo, "smooth", smo, smo, smo, "smooth", smo ):"smooth", \
            ( smo, smo, "increase", smo, smo, smo, "increase", smo):"increase",\
            ( smo, smo, "decrease", smo, smo, smo, "decrease", smo):"decrease",\
            }
    infodict = { "knit":"smooth", "k2tog":"decrease", "yarnover":"increase",\
            "bindoff":"end"}
    infodict2 = { "yarnover":"start", "knit":"smooth", "bindoff":"end" }
    node_attributes = netx.get_node_attributes( grid, "stitchtype" )
    info = [None ] *8
    info[0] = infodict2.get( node_attributes[ row[0] ], default_false )
    info[1] = infodict2.get( node_attributes[ row[1] ], default_false )
    info[2] = infodict.get( node_attributes[ row[2] ], default_false )
    info[3] = infodict2.get( node_attributes[ row[3] ], default_false )

    info[4] = infodict2.get( node_attributes[ row[-1] ], default_false )
    info[5] = infodict2.get( node_attributes[ row[-2] ], default_false )
    info[6] = infodict.get( node_attributes[ row[-3] ], default_false )
    info[7] = infodict2.get( node_attributes[ row[-4] ], default_false )
    info = tuple( info )

    return identidict.get( tuple(info), default_false )

def border_type1_expansionplaces( grid ):
    info_for_row = []
    for row in grid.get_rows():
        tmpinfo = border_type1_identifier( row, grid )
        info_for_row.append( tmpinfo )
    return info_for_row


        




def find_outerline_lowtension_symmetry( grid ):
    """
    Find the first x rows, where the tension between both outer 
    stitches is to big
    :todo: second while-loop seems bad
    """
    tensiondict = netx.get_edge_attributes( grid, "currentlength" )
    rows = grid.get_rows()
    up, down, left, right = grid.get_borders()
    i = 0
    startindex, endindex = None,None
    #while not tension_on_both_sides_too_low( rows[i], tensiondict ):
    while not length_on_both_sides_too_low( rows[i], tensiondict ):
        i = i + 1
        if i == len(rows):
            return None, None
    startindex = i
    while i < len( rows ) - 1: #only test second statement, if this
        #if tension_on_both_sides_too_low( rows[i], tensiondict ):
        if length_on_both_sides_too_low( rows[i], tensiondict ):
            i = i + 1
        else:
            break
    endindex = i
    return startindex, endindex

def find_outerline_tension_symmetry( grid ):
    """
    Find the first x rows, where the tension between both outer 
    stitches is to big
    :todo: second while-loop seems bad
    """
    #tensiondict = netx.get_edge_attributes( grid, "tension" )
    tensiondict = netx.get_edge_attributes( grid, "currentlength" )
    raise Exception( grid.edges( data=True ) )
    rows = grid.get_rows()
    up, down, left, right = grid.get_borders()
    i = 0
    startindex, endindex = None,None
    #while not tension_on_both_sides_too_large( rows[i], tensiondict ):
    while not length_on_both_sides_too_large( rows[i], tensiondict ):
        i = i + 1
        if i == len(rows):
            return None, None
    startindex = i
    while i < len( rows ) -1:
        #if tension_on_both_sides_too_large( rows[i], tensiondict ):
        if length_on_both_sides_too_large( rows[i], tensiondict ):
            i = i + 1
        else:
            break
    endindex = i
    return startindex, endindex

def length_on_both_sides_too_low( row, lengthdict, minimal_length=0.01 ):
    l = lengthdict
    minl = minimal_length
    tmp = [ l[( row[i], row[i+1], 0 )] for i in range(0,4) ]
    print( l )
    cond1 = any( [ i < minl for i in tmp ])
    tmp = [ l[( row[i], row[i+1], 0 )] for i in range(-5,-1) ]
    cond2 = any( [ i < minl for i in tmp ])
    return cond1 and cond2


def length_on_both_sides_too_large( row, lengthdict, maximal_length=0.02 ):
    l = lengthdict
    print( l )
    maxl = maximal_length
    tmp = [ l[( row[i], row[i+1], 0 )] for i in range(0,4) ]
    print( tmp )
    cond1 = any( [ i > maxl for i in tmp ])
    tmp = [ l[( row[i], row[i+1], 0 )] for i in range(-5,-1) ]
    print( tmp )
    cond2 = any( [ i > maxl for i in tmp ])
    return cond1 and cond2

def tension_on_both_sides_too_low( row, tensiondict ):
    """
    :todo: this function alwas fails
    """
    minimal_tension = 0.0

    tens = tensiondict
    min_tens = minimal_tension
    # fails if side==left
    cond1 = any( [ tens[ row[i] ] < min_tens \
                    for i in range(1,5) ] )
    cond2 = any( [ tens[ row[i] ] < min_tens \
                    for i in range(-1,-5, -1) ] )
    return cond1 and cond2

def tension_on_both_sides_too_large( row, tensiondict ):
    maximal_tension = 0.5

    tens = tensiondict
    max_tens = maximal_tension
    # fails if side==left
    cond1 = any( [ tens[ row[i] ] > max_tens \
                    for i in range(1,5) ] )
    cond2 = any( [ tens[ row[i] ]>max_tens \
                    for i in range(-1,-5, -1) ] )
    return cond1 and cond2

def control_columnlongenough( rows, bottom, top ):
    for i in range( bottom, top):
        if len( rows[i] ) < 10:
            return False
    return True


def remove_column_both_sides( strickgraph, bottom, top ):
    """
    :param bottom: the bottom row, where the inserted column should start
    :type strickgraph: strickgraph
    :type bottom, top: int
    """
    rows = strickgraph.get_rows()
    if not control_columnlongenough( rows, bottom, top ):
        raise Exception("not implemented, row too short for add columns")
        return False
    marknodes_left = []
    marknodes_right = []
    for i in range(bottom, top):
        marknodes_left.append( rows[i][1] )
        marknodes_right.append( rows[i][-2] )

    for marknode in marknodes_left:
        success, info = verb_removecolumn_left.replace_in_graph_withinfo( strickgraph, marknode )
        if not success:
            print( info )
            return False
    for marknode in marknodes_right:
        success, info = verb_removecolumn_right.replace_in_graph_withinfo( strickgraph, marknode )
        if not success:
            print( info )
            return False
    return True

def add_column_left_side( strickgraph, bottom, top ):
    """
    :param bottom: the bottom row, where the inserted column should start
    :type strickgraph: strickgraph
    :type bottom, top: int
    """
    rows = strickgraph.get_rows()
    if not control_columnlongenough( rows, bottom, top ):
        raise Exception("not implemented, row too short for add columns")
        return False
    marknodes_left = []
    marknodes_right = []
    for i in range(bottom, top):
        marknodes_left.append( rows[i][1] )
        #marknodes_right.append( rows[i][-2] )
    for marknode in marknodes_left:
        success, info = verb_insertcolumn_left.replace_in_graph_withinfo( strickgraph, marknode )
        if not success:
            for iii in info:
                print( iii )
            verb_insertcolumn_left.print_compare_to_graph_at_position( \
                                                    strickgraph, marknode )
        #    break
            return False
    return True


def add_column_right_side( strickgraph, bottom, top ):
    """
    :param bottom: the bottom row, where the inserted column should start
    :type strickgraph: strickgraph
    :type bottom, top: int
    """
    rows = strickgraph.get_rows()
    if not control_columnlongenough( rows, bottom, top ):
        raise Exception("not implemented, row too short for add columns")
        return False
    marknodes_left = []
    marknodes_right = []
    for i in range(bottom, top):
        #marknodes_left.append( rows[i][1] )
        marknodes_right.append( rows[i][-2] )
    for marknode in marknodes_right:
        success, info = verb_insertcolumn_right.replace_in_graph_withinfo( strickgraph, marknode )
        if not success:
            for iii in info:
                print( iii )
            verb_insertcolumn_right.print_compare_to_graph_at_position( \
                                                    strickgraph, marknode )
            return False
    return True
