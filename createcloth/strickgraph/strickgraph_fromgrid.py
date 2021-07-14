from .strickgraph_helper import fetch_neighbour_to_row, separate_to_rows, \
                                sort_rows_as_snake
from .strickgraph_helper import strick_NotImplementedError, strick_NotFoundError
#from . import load_stitchinfo as stitchinfo
#from .load_stitchinfo import myasd as stitchinfo
import networkx as netx



def _rowmanagment( graph, firstrow ):
    """
    converts a graph into a snake. snake is bucketed in sublist. These sublists
    are the rows.
    :type graph: networkx.Graph
    :type firstrow: list; elements==hashable
    :return rows: graph.nodes() sorted as snake, divided into sublists. every 
                list is a row of the strickgraph
    :rtype rows: list, type(list[i])==list, type(list[i][i])==hashable
    """
    rows = separate_to_rows( graph, firstrow )
    rows = sort_rows_as_snake( graph, rows, firstrow )
    return rows

rightside = "right"
leftside = "left"
turndict={ rightside:leftside, leftside:rightside }

def turn(side):
    return turndict[side]

def _managestitches( strickgraph, rows, graph, startside, stitchinfo ):
    """
    loops through every node in the graph to construct the strickgraph. 
    what happens with every node is upto my_stitchgenerator
    Manages information gathering for my_stitchgenerator
    :param startside: 'right' or 'left'
    """
    if startside == "right":
        alternatesides = ["right", "left"]
    else:
        alternatesides = ["left", "right"]
    rowindex = 0
    sorted_restrowlist = []
    for currentrow in rows:
        sorted_restrowlist = sorted_restrowlist + currentrow

    while len( sorted_restrowlist ) > 0: # 1 loop for every node
        tmpnode = sorted_restrowlist.pop( 0 ) #take next node
        if tmpnode not in rows[rowindex]:
            rowindex = rowindex + 1 #switch to next row
            if tmpnode not in rows[rowindex]:
                raise Exception("Switched to next row but still no node")
        side = alternatesides[rowindex%2]
        my_stitchgenerator( tmpnode, strickgraph, rows, graph, 
                            sorted_restrowlist, rowindex, side, stitchinfo )
    strickgraph.add_edge( "start", rows[0][0], edgetype="next" )
    strickgraph.add_edge( rows[-1][-1], "end", edgetype="next" )


stitchgenerator_lib={}
def _sortmethod_equaltolist( sortedlist ):
    def sort_method( value ):
        return sortedlist.index( value )
    return sort_method

def my_stitchgenerator( node, strickgraph, rows, graph, sorted_restrowlist, \
                        rowindex, side, stitchinfo ):
    """
    Is called for every node once.
    manages which generatorfunction is called for each node
    Generates a tuple zustand for identification which generatorfunction should
    be used
    """
    zustand = [1,0,0,0] #[lastrow=2 or firstrow=0, upneighbours, downneighbours]
    equalsortedlist = _sortmethod_equaltolist( sorted_restrowlist )
    tmpneighbours = set( graph.neighbors( node ) )
    tmpnext = [ x for x in tmpneighbours if x in sorted_restrowlist ]
    tmpnext.sort( key = equalsortedlist )
    tmpprevious = [ x for x in tmpneighbours if x not in tmpnext ]

    # zustand[0]    =0 if row==0; at bottom
    #               =2 if row==len(rows)-1; at top 
    #               =1 else
    zustand[0] = { 0:0, len(rows)-1:2 }.setdefault( rowindex, 1 )
    # zustand[1]    =0 if at start of row; 
    #               =2 if at end of row; 
    #               =1 else
    zustand[1] = { 0:0, len(rows[rowindex])-1:2}.setdefault( 
                                            rows[rowindex].index(node), 1)
    zustand[2] = len(tmpprevious)
    zustand[3] = len(tmpnext)

    stitch_generator = stitchgenerator_lib[ tuple( zustand ) ]
    return stitch_generator( strickgraph, node, tmpnext, side, stitchinfo )



def _make_node_to_stitch( strickgraph, node, stitchtype, nextknot, upknots, \
                            side, stinfo, nextbreaksline = False, end = False ):
    """
    creates with information from load_stitchinfo the knot
    the graph strickgraph needs to have the node so that this method can create
    the outedges and the the nodes properties
    :todo: more errorthrowing
    """
    if stitchtype not in stinfo.types:
        raise Exception( "stitchtype %s not included" %(stitchtype) )
    if len(upknots) != stinfo.upedges[ stitchtype ]:
        raise Exception( "stitchtype %s has %d upedges not %d"%(stitchtype, \
                                    stinfo.upedges[stitchtype],len(upknots))
                                    )

    nextattributes = {"edgetype":"next"}
    if nextbreaksline:
        nextattributes.update({ "breakline":0 })

    netx.set_node_attributes( strickgraph, {node:{"stitchtype":stitchtype, 
                                                    "side":side}} )
    if not end:
        strickgraph.add_edge( node, nextknot, **nextattributes )
    for tmpknot in upknots:
        strickgraph.add_edge( node, tmpknot, edgetype="up" )


def begin_withyarnover( strickgraph, node, nextneighbours, side, stinfo ):
    """ method for createing yarn over at start of knitthing """
    nextknot = nextneighbours[0]
    upknots = [ nextneighbours[1] ]
    
    _make_node_to_stitch( strickgraph, node, "yarnover", nextknot, upknots,side, stinfo)

stitchgenerator_lib.update({ (0,0,0,2):begin_withyarnover })

def firstrow_withyarnover( strickgraph, node, nextneighbours, side, stinfo ):
    """ method for the first row initializing the knithing with yos """
    nextknot = nextneighbours[0]
    upknots = [ nextneighbours[1] ]
    
    _make_node_to_stitch( strickgraph, node, "yarnover", nextknot, upknots,side, stinfo)

stitchgenerator_lib.update({ (0,1,1,2):firstrow_withyarnover })

def endfirstrow_withyarnover( strickgraph, node, nextneighbours, side, stinfo ):
    """ method for the first row initializing the knithing with yos """
    nextknot = nextneighbours[0]
    upknots = [ nextneighbours[0] ]
    
    _make_node_to_stitch( strickgraph, node, "yarnover", nextknot, upknots, \
                            side, stinfo, nextbreaksline = True )

stitchgenerator_lib.update({ (0,2,1,1):endfirstrow_withyarnover })


def lastrow_withbindoff( strickgraph, node, nextneighbours, side, stinfo ):
    """ method for the last row with bindofs """
    nextknot = nextneighbours[0]
    upknots = []
    
    _make_node_to_stitch( strickgraph, node, "bindoff", nextknot, upknots, \
                            side, stinfo, nextbreaksline = False )

stitchgenerator_lib.update({
        (2,1,2,1):lastrow_withbindoff,
        (2,0,1,1):lastrow_withbindoff, #the first stitch of the row
        })

def laststitch_withbindoff( strickgraph, node, nextneighbours, side, stinfo ):
    """ method for the last row with bindofs """
    nextknot = None
    upknots = []
    
    _make_node_to_stitch( strickgraph, node, "bindoff", nextknot, upknots, \
                            side, stinfo, end=True )

stitchgenerator_lib.update({
        (2,2,2,0):laststitch_withbindoff
        })


def knit_stitch( strickgraph, node, nextneighbours, side, stinfo ):
    nextknot = nextneighbours[0]
    nextattributes = {"edgetype":"next"}
    returnvalue = ""
    if len(nextneighbours) == 2:
        upknot = nextneighbours[1]
    else:
        nextattributes.update({"breakline":1})
        upknot = nextneighbours[0]
        returnvalue = "break"
    strickgraph.add_edge( node, upknot, edgetype="up" )
    strickgraph.add_edge( node, nextknot, **nextattributes )
    netx.set_node_attributes( strickgraph, \
                                {node:{"stitchtype":"knit", "side":side}} )
    return returnvalue

stitchgenerator_lib.update({
        (1,1,2,2):knit_stitch,
        (1,2,2,1):knit_stitch, #the first stitch of the row
        (1,0,1,2):knit_stitch, #the last stitch of the row
        })


class strick_fromgrid:
    @classmethod
    def from_gridgraph( cls, graph, firstrow, stitchinfo, startside="right" ):
        """
        This method takes a grid and converts it to a strickgraph
        :param graph: must be convertable to a snake
        :type graph: networkx.Graph
        :param firstrow: defines the first row of the graph. 
                        is a list of connected nodes from graph:
                            firstrow[i] in graph.nodes()
        :type firstrow: list, elements==hashable
        """
        rows = _rowmanagment( graph, firstrow )
        #strickgraph = netx.MultiDiGraph( graph )
        strickgraph = cls( graph )
        strickgraph.clear_edges()
        _managestitches( strickgraph, rows, graph, startside, stitchinfo )
        return strickgraph

