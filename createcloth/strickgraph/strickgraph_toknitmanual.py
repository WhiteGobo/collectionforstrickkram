"""
main function here is tomanual
:todo: support for load_stitchinfo. support seems not complete because example
        character_dictionary
"""
import networkx as netx
import regex

from .. import strickgraph as mod_strickgraph
from .datacontainer import strick_datacontainer
#from . import handknitting_terms
#from . import machine_terms
import logging
logger = logging.getLogger( __name__ )
from typing import Tuple


class strick_manualhelper( strick_datacontainer ):
    def to_manual( self, stitchinfo, manual_type="machine" ):
        return tomanual( self, stitchinfo, manual_type)

    @classmethod
    def from_manual( cls, manual, stitchinfo, manual_type="machine", \
                                        startside="right", reverse=False ):
        return frommanual( manual, stitchinfo, manual_type, \
                                    startside, reverse=reverse )


def tomanual( strickgraph, stitchinfo, manual_type="thread" ):
    """
    text a manual for the given complete strickgraph
    :todo: rewrite to remove reversing of rows and pass on manual_type 
            to strickgraph.get_rows
    """
    #startside = strickgraph.get_startside()
    #rows = find_rows( strickgraph )
    rows = strickgraph.get_rows( presentation_type="thread" )
    startnode = rows[0][0]
    startside = strickgraph.get_nodeattr_side()[ startnode ]
    nodeattributes = strickgraph.get_nodeattr_stitchtype()

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
    """

    :todo: strange use of global variable, has to be revisted
    """
    character_dictionary.update( stitchinfo.stitchsymbol ) #ensure up-to-date
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
            #print(rows)
            #print(nextnode)
            raise Exception("loop found", rows, nextnode)
        visited.add( nextnode )
        tmpnode = nextnode
        nextnode = tmpdict[ tmpnode ]
    return rows



class BrokenManual( Exception ):
    pass


def frommanual( manual, stitchinfo, manual_type="machine", startside="right", \
                reverse=False ):
    """helper method for reation of strick from manual"""
    manual = transform_manual_to_listform( manual )
    mystitchinfo = stitchinfo
    if manual_type in mod_strickgraph.handknitting_terms:
        _reverse_every_second_row( manual )
    elif manual_type in mod_strickgraph.machine_terms:
        pass
    else:
        raise Exception( "dont knot manual_type %s" %(manual_type) )

    if reverse:
        _reverse_every_row( manual )
    manual = transform_to_single_key( manual )
    manual = symbol_to_stitchid( manual, mystitchinfo )
    mystrickgraph = list_to_strickgraph( manual, startside, mystitchinfo )
    return mystrickgraph

def _reverse_every_row( manual ):
    for i in range( len(manual) ):
        manual[ i ].reverse()

def _reverse_every_second_row( manual ):
    for i in range( int(len(manual)/2) ):
        manual[ 2*i+1 ].reverse()

def symbol_to_stitchid( manual, mystitchinfo ):
    #namedict = { mystitchinfo.symbol[x]:x for x in mystitchinfo.symbol }
    namedict = mystitchinfo.stitchsymbol_to_stitchid
    for i in range( len(manual)):
        try:
            manual[i] = [ namedict[x] for x in manual[i] ]
        except KeyError as err:
            raise KeyError("manual contains keys, that are not supported", \
                                                mystitchinfo.stitchsymbol ) from err
    return manual

def stitchnodeid( rowindex, columnindex, stitchtype ):
    """
    sets the name of the nodes
    the naming processs can be altered, with 
    >>fromknitmanual.stitchnodeid = own_naming_function
    >>type(own_naming_function) == foo( i,j,stitchtype )

    :type rowindex: int
    :type columnindex: int
    :type stitchtype: str
    :param stitchtype: stitchtype corresponding to load_stitchinfo.types
                    practicly the name of the stitch, eg 'knit' or 'purl'
                    no abbrevation
    """
    return ( rowindex, columnindex )

def list_to_strickgraph( manual, startside, mystitchinfo ):
    """

    :rtype: strickgraph
    :todo: implement this into strickgraph
    """
    from .strickgraph_base import strickgraph
    from .strickgraph_fromgrid import turn
    downknots, upknots = None, None
    i,j = None, None
    node_edgefrom, nodeid = None, None
    #graph = strickgraph()
    #graph.add_node("start")
    laststitch = None#(0,0)
    nodeattributes = {}
    edgeswithlabels = []
    lastrow = []
    i = 0
    current_side = startside
    for row in manual:
        newrow = []
        tmprange = range( len(row) ) \
                        if current_side == "right" \
                        else range( len(row)-1, -1, -1 )
        #for j in _range_depend_on_side[current_side]( len(row) ):
        for j in tmprange:
            single: str = row[j]
            #nodeid = stitchnodeid(i,j,single)
            nodeid: Tuple[ int, int ] = ( i, j )
            downknots = mystitchinfo.downedges[ single ]
            upknots = mystitchinfo.upedges[ single ]
            extrainfo = mystitchinfo.extraoptions[ single ]
            nodeattributes[ nodeid ] = {"stitchtype":single,"side":current_side}
            nodeattributes[ nodeid ].update( extrainfo )

            #graph.add_node( nodeid, stitchtype=single, side=current_side, \
            #                                            **extrainfo )

            #if laststitch != nodeid: #else first nodewould have an edge to itsel
            if laststitch is not None:
                edgeswithlabels.append( (laststitch, nodeid, "next") )

            for k in range(downknots):
                try:
                    node_edgefrom = lastrow.pop()
                except IndexError as err:
                    err.args = (*err.args, ("in row %d the downedges doesnt "\
                                    +"match the upedges of the last row")%(i))
                    raise BrokenManual( *err.args )
                edgeswithlabels.append( (node_edgefrom, nodeid, "up") )
                #graph.add_edge( node_edgefrom, nodeid, edgetype="up" )
            for k in range( upknots ):
                newrow.append( nodeid )
            laststitch = nodeid
        if len(lastrow) > 0:
            raise BrokenManual(("in row %d the downedges doesnt "\
                                    +"match the upedges of the last row")%(i))
        lastrow = newrow
        i = i+1
        current_side = turn(current_side)
    return strickgraph( nodeattributes, edgeswithlabels )

    raise Exception()
    graph.add_node( "end" )
    graph.add_edge( laststitch, "end", edgetype="next" )
    return graph

#_range_depend_on_side = {}
#def _range_depend_on_side_right( len_nextrow ):
#    return range( len_nextrow )
#def _range_depend_on_side_left( len_nextrow ):
#    return range( len_nextrow-1, -1, -1 )
#_range_depend_on_side.update({\
#        "right": _range_depend_on_side_right,
#        "left": _range_depend_on_side_left,
#        })


def transform_to_single_key( manual ):
    newmanual = []
    for i in range(len(manual)):
        newline = []
        newmanual.append( newline )
        for j in range(len(manual[i])):
            asd = regex.match( r"(?P<number>\d+)(?P<stitch>\S+)", manual[i][j] )
            if asd:
                asddict = asd.groupdict()
                for x in range( int(asddict[ "number" ] )):
                    newline.append( str(asddict[ "stitch" ]) )
                #manual[i][j] = ( asddict[ "number" ], asddict[ "stitch" ] )
            else: # if only one stitch of the type is used the number is missing
                newline.append( manual[i][j] )
                #manual[i][j] = ( 1, manual[i][j] )
    return newmanual


def transform_manual_to_listform( manual ):
    return transformdict[type(manual)]( manual )

transformdict = {}
def _trans_manual_texttolist( manual ):
    """
    :todo: maybe transport different layouts to other function
    """
    manual = manual.replace( ",", " " )
    manual = [ x.split() for x in manual.splitlines() ]
    for i in range( len(manual)):
        j = 0
        while j <len(manual[i]):
            if manual[i][j].isdigit():
                if len(manual[i]) < j+1:
                        raise BrokenManual( "manual is broken at line %d"%(i))
                elif manual[i][j+1].isdigit():
                        raise BrokenManual( "manual is broken at line %d"%(i))
                else:
                    manual[i][j+1] = manual[i][j] + manual[i][j+1]
                    manual[i].pop(j)
            else:
                j = j+1
    return  manual
transformdict.update({ str: _trans_manual_texttolist })

def _trans_manual_listtolist( manual ):
    """
    check if itis a nested list or a list of strings (like a stream)
    """
    if isinstance( manual[0], list):
        return manual
    elif isinstance( manual[0], str ):
        manual = [ x.split() for x in manual ]
        return manual
    raise BrokenManual( "manual type cannot be interpreted" )
transformdict.update({ list: _trans_manual_listtolist })

