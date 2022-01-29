def classify( mystrickgraph ):
    rows = mystrickgraph.get_rows()
    stitchtypes = mystrickgraph.get_nodeattr_stitchtype()
    down, up, left, right = mystrickgraph.get_borders()

    chasm_stitches = [ s for s in up if s not in rows[-1] ]

    asd = [ mystrickgraph.get_nodes_near_nodes( [q], 3 ) for q in chasm_stitches ]
    raise Exception( mystrickgraph.get_threads() )
    print( up )
    print( chasm_stitches )
    print( asd )
    
    return { "crack_width": (1,2,3) }
