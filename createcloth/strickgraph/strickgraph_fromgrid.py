from .strickgraph_helper import fetch_neighbour_to_row, separate_to_rows, \
                                sort_rows_as_snake
from .strickgraph_helper import strick_NotImplementedError, strick_NotFoundError
#from . import load_stitchinfo as stitchinfo
#from .load_stitchinfo import myasd as stitchinfo
import networkx as netx


rightside = "right"
leftside = "left"
turndict={ rightside:leftside, leftside:rightside }

def turn(side):
    return turndict[side]

#def _managestitches( strickgraph, rows, graph, startside, stitchinfo, edges ):
def _managestitches( rows, startside, stitchinfo, edges ):
    """
    loops through every node in the graph to construct the strickgraph. 
    what happens with every node is upto my_stitchgenerator
    Manages information gathering for my_stitchgenerator
    :param startside: 'right' or 'left'
    """
    alternatesides =["right","left"] if startside=="right" else ["left","right"]
    import itertools as it
    sorted_restrowlist = list( it.chain( *rows ))
    nodetorowindex = {}
    for i, row in enumerate( rows ):
        for node in row:
            nodetorowindex[ node ] = i
    dictedges = {}
    upedges = {} #nodes:list[nodes]
    downedges = {} #nodes:list[nodes]
    edgelabels = []
    for v1, v2 in edges:
        i1, i2 = ( nodetorowindex[v] for v in (v1, v2) )
        if i1-i2 == -1:
            upedges.setdefault( v1, list() ).append( v2 )
            downedges.setdefault( v2, list() ).append( v1 )
            edgelabels.append( (v1, v2, "up") )
        elif i1-i2 == 1:
            upedges.setdefault( v2, list() ).append( v1 )
            downedges.setdefault( v1, list() ).append( v2 )
            edgelabels.append( (v2, v1, "up") )
        else:
            vertices_sorted = sorted((v1, v2),key=sorted_restrowlist.index)
            edgelabels.append( ( *vertices_sorted, "next" ) )
    for lowrow, highrow in zip(rows[:-1], rows[1:]):
        lastnode, firstnode = lowrow[-1], highrow[0]
        edgelabels.append( ( lastnode, firstnode, "next" ) )
    def asdf( downnumber, upnumber ):
        if ( downnumber, upnumber ) == ( 0, 1 ):
            return "yarnover"
        elif ( downnumber, upnumber ) == ( 1, 0 ):
            return "bindoff"
        elif ( downnumber, upnumber ) == ( 1, 1 ):
            return "knit"
        else:
            raise Exception()

    upnumber = { n: len(tmplist) for n, tmplist in upedges.items() }
    downnumber = { n: len(tmplist) for n, tmplist in downedges.items() }
    nodeattributes = {}
    for rowindex, row in enumerate( rows ):
        side = alternatesides[rowindex%2]
        for n in row:
            try:
                stitchtype = asdf( downnumber.get(n,0), upnumber.get( n,0) )
            except Exception as err:
                raise Exception(n) from err
            nodeattributes[ n ] = { "side":side, "stitchtype":stitchtype }
            pass
    return nodeattributes, edgelabels
    rowindex = 0
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
    return nodeattributes, edgelabels


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


from typing import Iterable, Hashable
class strick_fromgrid:
    @classmethod
    def from_gridgraph( cls, graph, firstrow:Iterable[Hashable], stitchinfo, startside="right" ):
        """ This method takes a grid and converts it to a strickgraph

        :param graph: must be convertable to a snake
        :type graph: networkx.Graph
        :param firstrow: defines the first row of the graph. 
                        is a list of connected nodes from graph: 
                        firstrow[i] in graph.nodes()
        :type firstrow: Iterable[ Hashable ]
        """
        rows = separate_to_rows( graph, firstrow )
        rows = sort_rows_as_snake( graph, rows, firstrow )
        #strickgraph = netx.MultiDiGraph( graph )
        nodeattributes = {(0, 0): {'side': 'right', 'stitchtype': 'yarnover'}, (0, 1): {'side': 'right', 'stitchtype': 'yarnover'}, (0, 2): {'side': 'right', 'stitchtype': 'yarnover'}, (0, 3): {'side': 'right', 'stitchtype': 'yarnover'}, (1, 3): {'side': 'left', 'stitchtype': 'knit'}, (1, 2): {'side': 'left', 'stitchtype': 'knit'}, (1, 1): {'side': 'left', 'stitchtype': 'knit'}, (1, 0): {'side': 'left', 'stitchtype': 'knit'}, (2, 0): {'side': 'right', 'stitchtype': 'knit'}, (2, 1): {'side': 'right', 'stitchtype': 'knit'}, (2, 2): {'side': 'right', 'stitchtype': 'knit'}, (2, 3): {'side': 'right', 'stitchtype': 'knit'}, (3, 3): {'side': 'left', 'stitchtype': 'bindoff'}, (3, 2): {'side': 'left', 'stitchtype': 'bindoff'}, (3, 1): {'side': 'left', 'stitchtype': 'bindoff'}, (3, 0): {'side': 'left', 'stitchtype': 'bindoff'}}
        edgelabels = [((0, 0), (1, 0), 'up'), ((0, 0), (0, 1), 'next'), ((0, 1), (1, 1), 'up'), ((0, 1), (0, 2), 'next'), ((0, 2), (1, 2), 'up'), ((0, 2), (0, 3), 'next'), ((0, 3), (1, 3), 'next'), ((0, 3), (1, 3), 'up'), ((1, 0), (2, 0), 'up'), ((1, 1), (1, 0), 'next'), ((1, 1), (2, 1), 'up'), ((1, 2), (1, 1), 'next'), ((1, 2), (2, 2), 'up'), ((1, 3), (1, 2), 'next'), ((1, 3), (2, 3), 'up'), ((2, 0), (3, 0), 'up'), ((1, 0), (2, 0), 'next'), ((2, 0), (2, 1), 'next'), ((2, 1), (3, 1), 'up'), ((2, 1), (2, 2), 'next'), ((2, 2), (3, 2), 'up'), ((2, 2), (2, 3), 'next'), ((2, 3), (3, 3), 'up'), ((2, 3), (3, 3), 'next'), ((3, 1), (3, 0), 'next'), ((3, 2), (3, 1), 'next'), ((3, 3), (3, 2), 'next')]
        nodeattributes, edgelabels = _managestitches( rows, startside, stitchinfo, graph.edges() )
        return cls( nodeattributes, edgelabels )

