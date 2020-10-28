from strickgraph_helper import fetch_neighbour_to_row, separate_to_rows, \
                                sort_rows_as_snake
from strickgraph_helper import strick_NotImplementedError, strick_NotFoundError
import networkx as netx

def create_strickgraph_from_gridgraph( graph, firstrow ):
    rows = _rowmanagment( graph, firstrow )
    strickgraph = netx.MultiDiGraph( graph )
    #strickgraph.add_node("start")
    #strickgraph.add_node("end")
    strickgraph.clear_edges()
    _managestitches( strickgraph, rows, graph )
    return strickgraph


def _rowmanagment( graph, firstrow ):
    rows = separate_to_rows( graph, firstrow )
    rows = sort_rows_as_snake( graph, rows, firstrow )
    return rows

rightside = "right"
leftside = "left"
turndict={ rightside:leftside, leftside:rightside }

def turn(side):
    return turndict[side]

def _add_nodes( strickgraph, rows, graph, startturn=rightside ):
    for currentrow in rows:
        for tmpnode in currentrow:
            my_stitchgenerator( tmpnode, strickgraph, rows, graph )

def _managestitches( strickgraph, rows, graph ):
    rowindex = 0
    sorted_restrowlist = []
    for currentrow in rows:
        sorted_restrowlist = sorted_restrowlist + currentrow

    while len( sorted_restrowlist ) > 0:
        tmpnode = sorted_restrowlist.pop( 0 )
        if tmpnode not in rows[rowindex]:
            rowindex = rowindex + 1
        my_stitchgenerator( tmpnode, strickgraph, rows, graph, 
                            sorted_restrowlist, rowindex )
    strickgraph.add_edge( "start", rows[0][0], edgetype="next" )
    strickgraph.add_edge( rows[-1][-1], "end", edgetype="next" )


stitchgenerator_lib={}

def my_stitchgenerator( node, strickgraph, rows, graph, sorted_restrowlist, \
                        rowindex ):
    zustand = [1,0,0] #[lastrow=2 or firstrow=0, upneighbours, downneighbours]
    if rowindex == 0:
        zustand[0] = 0
    elif rowindex == len(rows)-1:
        zustand[0] = 2
    tmpneighbours = list( graph.neighbors( node ) )
    tmpnext = [ x for x in tmpneighbours if x in sorted_restrowlist ]
    def sort_equalsortedlist( value ):
        return sorted_restrowlist.index( value )
    tmpnext.sort( key = sort_equalsortedlist )
    tmpprevious = [ x for x in tmpneighbours if x not in tmpnext ]
    zustand[2] = len(tmpnext)-1
    zustand[1] = len(tmpprevious)-1
    tmpgenerator = stitchgenerator_lib[ tuple( zustand ) ]
    tmpgenerator( strickgraph, node, tmpnext )


def firstrow_stitch( strickgraph, node, nextneighbours ):
    nextattributes = {"edgetype":"next"}
    if len(nextneighbours) == 2:
        (nextknot, upknot) = nextneighbours #is valid cause nextn. is sorted
    else:
        nextknot = nextneighbours[0]
        upknot = nextknot
        nextattributes.update({"breakline":1})
    netx.set_node_attributes( strickgraph, {node:{"stitchtype":"firstrow"}} )
    strickgraph.add_edge( node, nextknot, **nextattributes )
    strickgraph.add_edge( node, upknot, edgetype="up" )


stitchgenerator_lib.update({ 
        (0,0,1):firstrow_stitch, #the first stitch
        (0,-1,1):firstrow_stitch,
        (0,0,0):firstrow_stitch, #the last stitch of the first row
    })


def lastrow_stitch( strickgraph, node, nextneighbours ):
    if len(nextneighbours) == 1:
        nextknot = nextneighbours[0]
        strickgraph.add_edge( node, nextknot, edgetype="next" )
    netx.set_node_attributes( strickgraph, {node:{"stitchtype":"lastrow"}} )

stitchgenerator_lib.update({
        (2,1,0):lastrow_stitch,
        (2,1,-1):lastrow_stitch, #the last stitch
        (2,0,0):lastrow_stitch, #the first stitch of the row
        })


def knit_stitch( strickgraph, node, nextneighbours ):
    nextknot = nextneighbours[0]
    nextattributes = {"edgetype":"next"}
    if len(nextneighbours) == 2:
        upknot = nextneighbours[1]
    else:
        nextattributes.update({"breakline":1})
        upknot = nextneighbours[0]
    
    strickgraph.add_edge( node, upknot, edgetype="up" )
    strickgraph.add_edge( node, nextknot, **nextattributes )
    netx.set_node_attributes( strickgraph, {node:{"stitchtype":"knit"}} )

stitchgenerator_lib.update({
        (1,1,1):knit_stitch,
        (1,1,0):knit_stitch, #the first stitch of the row
        (1,0,1):knit_stitch, #the last stitch of the row
        })

