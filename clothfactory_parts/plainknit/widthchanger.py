import networkx as netx
from createcloth.strickgraph import tomanual
from createcloth.builtin_verbesserer import insertcolumn_left as verb_insertcolumn_left
from createcloth.builtin_verbesserer import insertcolumn_right as verb_insertcolumn_right
from createcloth.builtin_verbesserer import removecolumn_left as verb_removecolumn_left
from createcloth.builtin_verbesserer import removecolumn_right as verb_removecolumn_right
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo
from .plain_identifier import isplain

class failedOperation( Exception ):
    pass

def _extend_condition1( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[ i+1 ] in ("decrease",), \
                    linetypes[ i ] in ("decrease",), \
                    linetypes[ i-1 ] in ("decrease","plain"), \
                    ))
    except IndexError:
        return False
def _extend_condition2( linetypes, lowlinenumber, highlinenumber ):
    i, j = lowlinenumber, highlinenumber
    try:
        return all(( \
                    linetypes[ i+1 ] in ("plain",), \
                    linetypes[ i ] in ("extend",), \
                    linetypes[ i-1 ] in ("decrease","plain"), \
                    ))
    except IndexError:
        return False
extend_condition_list = ( _extend_condition1, _extend_condition2, )
def linepair_can_be_extended( linetypes, lowlinenumber, highlinenumber ):
    for extend_condition in extend_condition_list:
        if extend_condition( linetypes, lowlinenumber, highlinenumber ):
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
            #print( tomanual( mystrickgraph,globalstitchinfo,manual_type="machine"))
    else:
        raise failedOperation( "add columns failed" )



def remove_columns( mystrickgraph, rows_with_too_much_pressure ):
    longestconnectedrowlist = find_removecolumns( mystrickgraph, \
                                                rows_with_too_much_pressure )
    myrows = mystrickgraph.get_rows()
    for i in longestconnectedrowlist:
        verb_removecolumn_left.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][1] )
        verb_removecolumn_right.replace_in_graph_with_exception( \
                                                mystrickgraph, myrows[i][-2] )

        
def find_removecolumns( mystrickgraph, rows_with_too_much_pressure ):
    linetypes = isplain( mystrickgraph )
    lineforadd = [ i for i in range( len(linetypes)) \
                    if linetypes[i] in ("plain")]#, "increase") ]
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
    return longestconnectedlist


def find_addcolumns( mystrickgraph, rows_with_too_much_tension ):
    linetypes = isplain( mystrickgraph )
    print("lastdings: ", linetypes )
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


def find_row_for_inset( mystrickgraph, rows_with_too_much_tension, \
                                            rows_with_too_much_pressure ):
    rowpairs = [ (i, i+1) for i in rows_with_too_much_tension \
                        if i+1 not in rows_with_too_much_pressure ]
    rowpairs += [ (i-1, i) for i in rows_with_too_much_tension \
                        if i-1 not in rows_with_too_much_pressure ]
    linetypes = isplain( mystrickgraph )
    linepairforinset = [ (i,j) for i,j in rowpairs \
                        if linepair_can_be_extended( linetypes, i, j ) ]
    return linepairforinset[-1]
