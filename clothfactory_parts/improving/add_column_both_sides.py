import networkx as netx
from createcloth.strickgraph import tomanual
from createcloth.builtin_verbesserer import insertcolumn_left as verb_insertcolumn_left
from createcloth.builtin_verbesserer import insertcolumn_right as verb_insertcolumn_right
from createcloth.builtin_verbesserer import removecolumn_left as verb_removecolumn_left
from createcloth.builtin_verbesserer import removecolumn_right as verb_removecolumn_right
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo

plain_types = ( "knit" )
variable_types = ( "yarnover", "knit", "k2tog" )
def check_single_line( row, mystrickgraph ):
    stitchtypes = netx.get_node_attributes( mystrickgraph, "stitchtype" )
    a = stitchtypes[ row[0] ] in plain_types
    aa = stitchtypes[ row[1] ] in plain_types
    b = stitchtypes[ row[2] ] in variable_types
    c = stitchtypes[ row[3] ] in plain_types
    d = stitchtypes[ row[4] ] in variable_types
    e = stitchtypes[ row[5] ] in plain_types
    f = stitchtypes[ row[-1] ] in plain_types
    ff = stitchtypes[ row[-2] ] in plain_types
    g = stitchtypes[ row[-3] ] in variable_types
    h = stitchtypes[ row[-4] ] in plain_types
    i = stitchtypes[ row[-5] ] in variable_types
    j = stitchtypes[ row[-6] ] in plain_types
    return all( (a,aa,b,c,d,e,f,ff,g,h,i,j) )


addable_type1 = ( "yarnover", "knit" )
addable_type2 = ( "yarnover", "knit", "k2tog" )
def check_single_line_addable( row, mystrickgraph ):
    stitchtypes = netx.get_node_attributes( mystrickgraph, "stitchtype" )
    a = stitchtypes[ row[0] ] == "knit"
    aa = stitchtypes[ row[1] ] == "knit"
    b = stitchtypes[ row[2] ] in addable_type2
    c = stitchtypes[ row[3] ] == "knit"
    d = stitchtypes[ row[4] ] in addable_type1
    e = stitchtypes[ row[5] ] == "knit"
    f = stitchtypes[ row[-1] ] == "knit"
    ff = stitchtypes[ row[-2] ] == "knit"
    g = stitchtypes[ row[-3] ] in addable_type2
    h = stitchtypes[ row[-4] ] == "knit"
    i = stitchtypes[ row[-5] ] in addable_type1
    j = stitchtypes[ row[-6] ] == "knit"
    return all( (a,aa,b,c,d,e,f,ff,g,h,i,j) )

def check_if_plain( mystrickgraph ):
    rows = mystrickgraph.get_rows()
    for row in rows[1:-1]:
        if check_single_line( row, mystrickgraph ):
            pass
        else:
            return False
    #for row in rows[0,-1]: #check if only bindoff or only yarnover
    #    pass
    return True

def add_columns( mystrickgraph, rows_with_too_much_tension ):
    longestconnectedrowlist = find_addcolumns( mystrickgraph, \
                                                rows_with_too_much_tension )
    myrows = mystrickgraph.get_rows()
    for i in longestconnectedrowlist:
        print( i, longestconnectedrowlist )
        suc, info = verb_insertcolumn_left.replace_in_graph_withinfo( \
                                                mystrickgraph, myrows[i][1] ) 
        print( tomanual( mystrickgraph, globalstitchinfo, manual_type="machine" ))
        if not suc:
            st = netx.get_node_attributes( mystrickgraph, "stitchtype" )
            raise Exception( list((st[e] for e in mystrickgraph.get_rows()[i])), *info )
            raise Exception( *info )
        suc, info = verb_insertcolumn_right.replace_in_graph_withinfo( \
                                                mystrickgraph, myrows[i][-2] )
        print( tomanual( mystrickgraph, globalstitchinfo, manual_type="machine" ))
        if not suc:
            raise Exception( *info )

        
def remove_columns( mystrickgraph, rows_with_too_much_pressure ):
    longestconnectedrowlist = find_addcolumns( mystrickgraph, \
                                                rows_with_too_much_pressure )
    myrows = mystrickgraph.get_rows()
    for i in longestconnectedrowlist:
        print( i )
        suc, info = verb_removecolumn_left.replace_in_graph_withinfo( \
                                                mystrickgraph, myrows[i][1] )
        print( tomanual( mystrickgraph, globalstitchinfo, manual_type="machine" ))
        if not suc:
            raise Exception( *info )
        suc, info = verb_removecolumn_right.replace_in_graph_withinfo( \
                                                mystrickgraph, myrows[i][-2] )
        print( tomanual( mystrickgraph, globalstitchinfo, manual_type="machine" ))
        if not suc:
            raise Exception( *info )
        

def find_addcolumns( mystrickgraph, rows_with_too_much_tension ):
    add_columns = []
    add_columns.append( 0 )
    rows = mystrickgraph.get_rows()
    for i in range( 1, len(rows)-1 ):
        row = rows[i]
        if check_single_line( row, mystrickgraph ):
            add_columns.append( i )
    add_columns.append( len(rows)-1 )

    rows = set( add_columns ).intersection( rows_with_too_much_tension )
    rows = list( rows )
    if len( rows )==0:
        raise Exception()
    rows.sort()
    oldi = rows[0]
    currentlist = list((oldi,))
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
