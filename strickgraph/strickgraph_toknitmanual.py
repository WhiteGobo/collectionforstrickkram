import networkx as netx

def tomanual( strickgraph ):
    rows = find_rows( strickgraph )
    nodeattributes = netx.get_node_attributes( strickgraph, "stitchtype" )
    #print(rows)
    print(nodeattributes)

    text = ""
    for tmprow in rows:
        newline = transform_rowtomanualline( tmprow, nodeattributes )
        text = text + newline + "\n"
    return text
    
character_dictionary={"knit":"k", "firstrow":"r", "lastrow":"l", "k2tog":"k"}
def transform_rowtomanualline( row, stitchtypes_dictionary ):
    line = ""
    lastcharacter = stitchtypes_dictionary[ row.pop(0) ]
    times = 1
    if len(row) > 0:
        for node in row:
            newcharacter = stitchtypes_dictionary[ node ]
            if lastcharacter == newcharacter:
                times = times + 1
            else:
                line = _transrtm_addline( line, times, lastcharacter )
                times = 1
                lastcharacter = newcharacter
    line = _transrtm_addline( line, times, lastcharacter )
    return line

def _transrtm_addline( line, times, lastcharacter ):
    line = line + " %d%s"%( times, character_dictionary[ lastcharacter ] )
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
    rows.append( currentrow )
    tmpnode = "start"
    nextnode = tmpdict[ tmpnode ]
    while nextnode !="end":
        if (tmpnode, nextnode) in nextrowedges:
            currentrow = []
            rows.append( currentrow )
        currentrow.append( nextnode )
        tmpnode = nextnode
        nextnode = tmpdict[ tmpnode ]
    return rows


if __name__=="__main__":
    #for testing
    import strickgraph_fromgrid as qq
    mygraph = netx.grid_2d_graph( 4,4 )
    firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
    asd = qq.create_strickgraph_from_gridgraph( mygraph, firstrow )
    print("transform following edges:", asd.edges, "\n")

    manual = tomanual( asd ) 
    print( "mymanual:\n", manual )
