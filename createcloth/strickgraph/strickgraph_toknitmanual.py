"""
main function here is tomanual
:todo: support for load_stitchinfo. support seems not complete because example
        character_dictionary
"""
import networkx as netx


class strick_manualhelper:
    def to_manual( self, stitchinfo, manual_type="machine" ):
        return tomanual( self, stitchinfo, manual_type)

    @classmethod
    def from_manual( cls, manual, stitchinfo, manual_type="machine", \
                                        startside="right", reverse=False ):
        from . import fromknitmanual as frmman
        return frmman.frommanual( manual, stitchinfo, manual_type, \
                                    startside, reverse=reverse )


def tomanual( strickgraph, stitchinfo, manual_type="thread" ):
    """
    text a manual for the given complete strickgraph
    :todo: rewrite to remove reversing of rows and pass on manual_type 
            to strickgraph.get_rows
    """
    startside = strickgraph.get_startside()
    #rows = find_rows( strickgraph )
    rows = strickgraph.get_rows( presentation_type="thread" )
    nodeattributes = netx.get_node_attributes( strickgraph, "stitchtype" )

    text = ""
    for tmprow in rows:
        newline = transform_rowtomanualline( tmprow, nodeattributes, stitchinfo)
        text = text + newline + "\n"

    text_matrix = [ x.split() for x in text.splitlines() ]
    if startside=="left":
        _reverse_every_row( text_matrix )

    if manual_type == "machine":
        _reverse_every_second_row( text_matrix )
    text_list = [ " ".join(x) for x in text_matrix ]
    text = "\n".join(text_list)
    return text
    
def _reverse_every_row( manual ):
    for i in range( int(len(manual)) ):
        manual[ i ].reverse()
def _reverse_every_second_row( manual ):
    for i in range( int(len(manual)/2) ):
        manual[ 2*i+1 ].reverse()

character_dictionary={}
#character_dictionary.update( stitchinfo.symbol )
def transform_rowtomanualline( row, stitchtypes_dictionary, stitchinfo ):
    character_dictionary.update( stitchinfo.symbol ) #ensure up-to-date
    mycharacter_dictionary = character_dictionary

    line = ""
    lastcharacter = stitchtypes_dictionary[ row.pop(0) ]
    times = 1
    if len(row) > 0:
        for node in row:
            newcharacter = stitchtypes_dictionary[ node ]
            if lastcharacter == newcharacter:
                times = times + 1
            else:
                line = _transrtm_addline( line, times, lastcharacter, \
                                                mycharacter_dictionary )
                times = 1
                lastcharacter = newcharacter
    line = _transrtm_addline( line, times, lastcharacter, \
                                                mycharacter_dictionary )
    return line


def _transrtm_addline( line, times, lastcharacter, mycharacter_dictionary ):
    line = line + " %d%s"%( times, mycharacter_dictionary[ lastcharacter ] )
    return line


def find_rows( strickgraph ):
    alledges = netx.get_edge_attributes( strickgraph, "edgetype" )

    nextrowedges = netx.get_edge_attributes( strickgraph, "breakline" )
    nextrowedges = [ (x,y) for (x,y,infos) in nextrowedges ]

    tmpedges = list( alledges )
    tmpedges = [ x for x in tmpedges if alledges[x]=="next" ]
    tmpdict = { x:y for (x,y, infos) in tmpedges }

    rows = []
    currentrow = []
    visited = set()
    rows.append( currentrow )
    tmpnode = "start"
    nextnode = tmpdict[ tmpnode ]
    while nextnode !="end":
        if (tmpnode, nextnode) in nextrowedges:
            currentrow = []
            rows.append( currentrow )
        currentrow.append( nextnode )
        if nextnode in visited:
            print(rows)
            print(nextnode)
            raise Exception("loop found")
        visited.add( nextnode )
        tmpnode = nextnode
        nextnode = tmpdict[ tmpnode ]
    return rows

