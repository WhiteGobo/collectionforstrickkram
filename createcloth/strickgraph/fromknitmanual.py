"""
Naming process can be altered via
>>fromknitmanual.stitchnodeid = own_naming_function
>>type(own_naming_function) == foo( i,j,stitchtype )
look at stitchnodeid for more information
"""

import regex
from . import handknitting_terms
from . import machine_terms
import logging
logger = logging.getLogger( __name__ )

class BrokenManual( Exception ):
    pass


def frommanual( manual, stitchinfo, manual_type="machine", startside="right", \
                reverse=False ):
    """helper method for reation of strick from manual"""
    manual = transform_manual_to_listform( manual )
    mystitchinfo = stitchinfo
    if manual_type in handknitting_terms:
        _reverse_every_second_row( manual )
    elif manual_type in machine_terms:
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
    namedict = mystitchinfo.symbol_to_stitchid
    for i in range( len(manual)):
        try:
            manual[i] = [ namedict[x] for x in manual[i] ]
        except KeyError as err:
            raise KeyError("manual contains keys, that are not supported", \
                                                mystitchinfo.symbol) from err
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
    """
    from .strickgraph_base import strickgraph
    from .strickgraph_fromgrid import turn
    downknots, upknots = None, None
    i,j = None, None
    node_edgefrom, nodeid = None, None
    #graph = strickgraph()
    #graph.add_node("start")
    laststitch = (0,0)
    nodeattributes = {}
    edgeswithlabels = []
    lastrow = []
    i = 0
    current_side = startside
    for row in manual:
        newrow = []
        for j in _range_depend_on_side[current_side]( len(row) ):
            single = row[j]
            nodeid = stitchnodeid(i,j,single)
            downknots = mystitchinfo.downedges[ single ]
            upknots = mystitchinfo.upedges[ single ]
            extrainfo = mystitchinfo.extrainfo[ single ]
            nodeattributes[ nodeid ] = {"stitchtype":single,"side":current_side}
            nodeattributes[ nodeid ].update( extrainfo )

            #graph.add_node( nodeid, stitchtype=single, side=current_side, \
            #                                            **extrainfo )

            if laststitch != nodeid: #else first nodewould have an edge to itsel
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

_range_depend_on_side = {}
def _range_depend_on_side_right( len_nextrow ):
    return range( len_nextrow )
def _range_depend_on_side_left( len_nextrow ):
    return range( len_nextrow-1, -1, -1 )
_range_depend_on_side.update({\
        "right": _range_depend_on_side_right,
        "left": _range_depend_on_side_left,
        })


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

