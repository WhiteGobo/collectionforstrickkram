import networkx as netx
from createcloth.strickgraph import tomanual
from createcloth.builtin_verbesserer import \
                insertcolumn_left as verb_insertcolumn_left, \
                insertcolumn_right as verb_insertcolumn_right, \
                removecolumn_left as verb_removecolumn_left, \
                removecolumn_right as verb_removecolumn_right, \
                plain_extension_lowerleft as verb_extendcolumn_lowerleft, \
                plain_extension_lowerright as verb_extendcolumn_lowerright, \
                plain_extension_upperleft as verb_extendcolumn_upperleft, \
                plain_extension_upperright as verb_extendcolumn_upperright, \
                eaves_extension_lowerleft as verb_eavesextend_lowerleft, \
                eaves_extension_lowerright as verb_eavesextend_lowerright, \
                eaves_extension_upperleft as verb_eavesextend_upperleft, \
                eaves_extension_upperright as verb_eavesextend_upperright, \
                eaves_extension_lowerleft as verb_eavesinset_lowerleft, \
                eaves_extension_lowerright as verb_eavesinset_lowerright, \
                eaves_extension_upperleft as verb_eavesinset_upperleft, \
                eaves_extension_upperright as verb_eavesinset_upperright

from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo
from .plain_identifier import isplain

class failedOperation( Exception ):
    pass

def _extend_condition1( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[j+1] in ("decrease",), \
                    linetypes[ j ] in ("decrease","plain"), \
                    linetypes[ i ] in ("decrease",), \
                    linetypes[i-1] in ("decrease","plain"), \
                    )) or all(( \
                    linetypes[j+1] in ("decrease",), \
                    linetypes[ j ] in ("decrease",), \
                    linetypes[ i ] in ("decrease","plain"), \
                    linetypes[i-1] in ("decrease","plain"), \
                    ))
    except IndexError:
        return False
def _extend_condition2( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[j+1] in ("plain","end"), \
                    linetypes[ j ] in ("stagehiger",), \
                    linetypes[ i ] in ("stagelower",), \
                    linetypes[i-1] in ("decrease","plain"), \
                    ))
    except IndexError:
        return False
def _extend_condition3( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[j+1] in ("plain","increase",), \
                    linetypes[ j ] in ("increase",), \
                    linetypes[ i ] in ("increase","plain"), \
                    linetypes[i-1] in ("plain","increase","decrease","start"), \
                    )) or all(( \
                    linetypes[j+1] in ("plain","increase",), \
                    linetypes[ j ] in ("increase","plain"), \
                    linetypes[ i ] in ("increase",), \
                    linetypes[i-1] in ("plain","increase","decrease","start"), \
                    ))
    except IndexError:
        return False
def _extend_condition4( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[j+1] in ("plain","increase",), \
                    linetypes[ j ] in ("overhanghigher",), \
                    linetypes[ i ] in ("overhanglower",), \
                    linetypes[i-1] in ("plain","start","increase"), \
                    ))
    except IndexError:
        return False
extend_condition_list = ( _extend_condition1, _extend_condition2, _extend_condition3)
def linepair_can_be_extended( linetypes, lowlinenumber, highlinenumber ):
    for extend_condition in extend_condition_list:
        if extend_condition( linetypes, lowlinenumber, highlinenumber ):
            return True
    return False

def _remove_condition1( linetypes, linenumber ):
    i = linenumber
    try:
        return all(( \
                    linetypes[ i+1 ] in ("plain","decrease"), \
                    linetypes[ i ] in ("start",), \
                    ))
    except IndexError:
        return False
def _remove_condition2( linetypes, linenumber ):
    i = linenumber
    try:
        return all(( \
                    linetypes[ i+1 ] \
                    in ( "plain", "decrease", "enddecrease" ), \
                    linetypes[ i ] in ("plain","increase"), \
                    ))
    except IndexError:
        return False
remove_condition_list = ( _remove_condition1, _remove_condition2, )
def line_can_be_removed( linetypes, linenumber ):
    for remove_condition in remove_condition_list:
        if remove_condition( linetypes, linenumber ):
            return True
    return False

def _add_condition1( linetypes, linenumber ):
    i = linenumber
    try:
        return all(( \
                    linetypes[ i+1 ] in ( "plain", "increase", "end" ), \
                    linetypes[ i ] in ( "plain", "decrease", "start" ), \
                    ))
    except IndexError:
        return False
def _add_condition2( linetypes, linenumber ):
    i = linenumber
    return all(( \
                linetypes[0] in ("enddecrease",),
                ))
add_condition_list = ( _add_condition1, _add_condition2, )
def line_can_be_added( linetypes, linenumber ):
    for add_condition in add_condition_list:
        if add_condition( linetypes, linenumber):
            return True
    return False


def add_columns( mystrickgraph, rows_with_too_much_tension ):
    longestconnectedrowlist = find_addcolumns( mystrickgraph, \
                                                rows_with_too_much_tension )
    if longestconnectedrowlist:
        myrows = mystrickgraph.get_rows()
        for i in longestconnectedrowlist:
            verb_insertcolumn_left.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][1] ) 
            verb_insertcolumn_right.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-2] )
    else:
        raise failedOperation( "add columns failed" )



def remove_columns( mystrickgraph, rows_with_too_much_pressure ):
    longestconnectedrowlist = find_removecolumns( mystrickgraph, \
                                                rows_with_too_much_pressure )
    myrows = mystrickgraph.get_rows
    for i in longestconnectedrowlist:
        verb_removecolumn_left.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows()[i][1] )
        verb_removecolumn_right.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows()[i][-2] )

        
def find_removecolumns( mystrickgraph, rows_with_too_much_pressure ):
    linetypes = isplain( mystrickgraph )
    print( linetypes )
    lineforadd = [ i for i in range( len(linetypes)) \
                    if line_can_be_removed( linetypes, i ) ]
    rows = set( lineforadd ).intersection( rows_with_too_much_pressure )
    rows = list( rows )
    if len( rows )==0:
        raise Exception()
    rows.sort()
    oldi = rows[0]
    currentlist = [ oldi ]
    asdf = [ currentlist ]
    for i in rows[1:]:
        if i - oldi > 1:
            currentlist = list()
            asdf.append(currentlist)
        oldi = i
        currentlist.append(i)
    asdf.sort( key=len )
    longestconnectedlist = asdf[-1]
    print( longestconnectedlist )
    return longestconnectedlist


def find_addcolumns( mystrickgraph, rows_with_too_much_tension ):
    linetypes = isplain( mystrickgraph )
    lineforadd = [ i for i in range( len(linetypes)) \
                    if line_can_be_added( linetypes, i ) ]
    rows = set( lineforadd ).intersection( rows_with_too_much_tension )
    rows = list( rows )
    if len( rows )==0:
        return None
    rows.sort()
    oldi = rows[0]
    currentlist = [ oldi ]
    asdf = [ currentlist ]
    for i in rows[1:]:
        if i - oldi > 1:
            currentlist = list()
            asdf.append(currentlist)
        oldi = i
        currentlist.append(i)
    asdf.sort( key=len )
    longestconnectedlist = asdf[-1]
    return longestconnectedlist


def extend_columns( mystrickgraph, rows_with_too_much_tension ):
    rowpair, insettype = find_row_for_inset( mystrickgraph, \
                                                rows_with_too_much_tension, [] )
    if rowpair:
        myrows = mystrickgraph.get_rows()
        i, j = rowpair
        if insettype == "plane":
            if "right" == mystrickgraph.nodes[ myrows[i][0] ]["side"]:
                verb_extendcolumn_lowerright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-4] )
                verb_extendcolumn_upperleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][3] )
            else:
                verb_extendcolumn_lowerleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][3] )
                verb_extendcolumn_upperright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][-4] )
        else:
            from createcloth.visualizer import easygraph
            if "right" == mystrickgraph.nodes[ myrows[i][0] ]["side"]:
                verb_eavesextend_lowerright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-4] )
                verb_eavesextend_upperleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][3] )
            else:
                verb_eavesextend_lowerleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][3] )
                verb_eavesextend_upperright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][-4] )
    else:
        raise failedOperation( "extend columns failed" )


def inset_columns( mystrickgraph, rows_with_too_much_pressure ):
    rowpair, insettype = find_row_for_inset( mystrickgraph, \
                                            rows_with_too_much_pressure, [] )
    if rowpair:
        myrows = mystrickgraph.get_rows()
        i, j = rowpair
        if insettype == "eaves":
            if "right" == mystrickgraph.nodes[ myrows[i][0] ]["side"]:
                verb_extendcolumn_lowerright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-4] )
                verb_extendcolumn_upperleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][3] )
            else:
                verb_extendcolumn_lowerleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][3] )
                verb_extendcolumn_upperright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][-4] )
        else:
            if "right" == mystrickgraph.nodes[ myrows[i][0] ]["side"]:
                verb_eavesextend_lowerleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-4] )
                verb_eavesextend_upperright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][3] )
            else:
                verb_eavesextend_lowerleft.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][3] )
                verb_eavesextend_upperright.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[j][-4] )
    else:
        raise failedOperation( "extend columns failed" )


class InsetError( Exception ):
    def __init__( self, rowpairs, linepairforinset, linetypes, \
                            rows_with_too_much_tension, *args ):
        super().__init__( rowpairs, linepairforinset, linetypes, \
                            rows_with_too_much_tension, *args )
        self.rowpairs = rowpairs
        self.linepairforinset = linepairforinset
        self.linetypes = linetypes
        self.rows_with_too_much_tension = rows_with_too_much_tension
        

def find_row_for_inset( mystrickgraph, rows_with_too_much_tension, \
                                            rows_with_too_much_pressure ):
    rowpairs = [ (i, i+1) for i in rows_with_too_much_tension \
                        if i+1 not in rows_with_too_much_pressure ]
    rowpairs += [ (i-1, i) for i in rows_with_too_much_tension \
                        if i-1 not in rows_with_too_much_pressure ]
    linetypes = isplain( mystrickgraph )
    linepairforinset = [ (i,j) for i,j in rowpairs \
                        if linepair_can_be_extended( linetypes, i, j ) ]
    try:
        mylinepairforinset = linepairforinset[-1]
        if "increase" in set(( linetypes[i] for i in mylinepairforinset )):
            insettype = "eaves"
        else:
            insettype = "plane"
        return mylinepairforinset, insettype
    except IndexError as err:
        raise InsetError( rowpairs, linepairforinset, linetypes, \
                            rows_with_too_much_tension, len(mystrickgraph.get_rows()) ) from err
