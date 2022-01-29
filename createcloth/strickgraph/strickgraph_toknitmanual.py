"""
main function here is tomanual
:todo: support for load_stitchinfo. support seems not complete because example
        character_dictionary
"""
import networkx as netx
import regex
import itertools as it

from .. import strickgraph as mod_strickgraph
from .datacontainer import strick_datacontainer
#from . import handknitting_terms
#from . import machine_terms
import logging
logger = logging.getLogger( __name__ )
from typing import Tuple
from itertools import zip_longest


class strick_manualhelper( strick_datacontainer ):
    def to_manual( self, stitchinfo, manual_type="machine" ):
        statuses, commands = create_knit_commandarray( self )
        stitchtypes = self.get_nodeattr_stitchtype()
        startside = self.get_startside()
        rows = [[]]
        nooses = {}
        noose_int = 0
        for c in commands:
            if c[0] == "save_noose":
                try:
                    nooses[ c[1] ] = noose_int
                except IndexError as err:
                    raise Exception( c ) from err
                rows[-1].append( "tunnel%i" %(noose_int) )
                noose_int += 1
            elif c[0] == "load_noose":
                rows[-1].append( "load%i" %( nooses[c[1]] ) )
            elif c[0] == "turn":
                rows.append([])
            elif c[0] == "knit":
                rows[-1].append( c[1] )
            elif c[0] == "switch_thread":
                rows[-1].append( "switch%i"%(c[1] ) )
            else:
                raise Exception( c )

        asd: list[list[list[int, str]]] \
                = shorten_command_array( rows, stitchinfo.stitchsymbol )

        if manual_type == "machine":
            for i, row in enumerate( asd ):
                qi = 1 if startside=="right" else 0
                if i%2==qi:
                    row.reverse()
        row_commands =[["".join( str(a) for a in com if a != 1) \
                        for com in row] for row in asd]
        row_commands = [ " ".join(row) for row in row_commands ]
        manual = "\n".join( row_commands )
        return manual
        raise Exception( rows, asd, manual )
        return manual


        return asd

        raise Exception( "everything worked:)" )
        return tomanual( self, stitchinfo, manual_type)

    @classmethod
    def from_manual( cls, manual, stitchinfo, manual_type="machine", \
                                        startside="right", reverse=False ):
        return frommanual( manual, stitchinfo, manual_type, \
                                    startside, reverse=reverse )


def create_manual_commands( rows, stitchtypes, threads, previous, upedges, stitchside ):
    """
    
    :type threads: Sequence[ Hashable ]
    :param threads: List of sequences of stitches, ordered by next-edges as
            threads
    :type previous: Mapping[ Hashable, Iterable[ Hashable ] ]
    :param previous: maps every stitch onto list of stitches, that must be
            prdouced beforehand
    :type stitchtypes: Mapping[ Hashable, stitchtype ]
    :param stitchtypes: Stitchtypes for every stitch-id
    :type rows: stitches ordered in rows
    """
    raise Exception( "obsolete" )
    find_thread_to = lambda stitch: ( i for i, stitches in enumerate(threads) \
                                    if stitch in stitches ).__next__()
    irow = 0 #index of current row
    iline = 0 #index of current stitch in current row
    current_thread = find_thread_to( rows[ irow ][ iline ] )
    tunnel_snake = []
    visited = []
    current_anchors, next_anchors = [], []
    hastunnels = set()
    tunnelindex = 0
    while len( visited ) < sum( len(l) for l in rows ):
        current_row = rows[ irow ]
        try:
            current_stitch = current_row[ iline ]
        except IndexError:
            yield "\n"
            irow += 1
            iline = 0
            current_anchors, next_anchors = next_anchors, []
            current_anchors.sort( rows[ irow ].index )
            continue
        if current_stitch in visited:
            yield "skip"
            iline += 1
        elif all( (current_stitch in threads[ current_thread ], \
                all( s in visited for s in previous.get( current_stitch, [])),\
                ) ):
            yield stitchtypes[ current_stitch ]
            assert current_stitch not in visited
            visited.append( current_stitch )
            next_anchors.extend( upedges[ current_stitch ] )
            iline += 1
            if current_stitch == threads[ current_thread ][-1]:
                if len( visited ) == sum( len(row) for row in rows ):
                    return
                else:
                    current_thread, irow, iline = tunnel_snake.pop( 0 )
                    yield ("jump", (irow, current_thread) )
                    #jump to end of previous line
                    assert irow != 0
                    irow -= 1
                    iline = len( rows[ irow ])
        elif all(( current_stitch not in threads[ current_thread ], \
                all( s not in visited for s in previous.get( current_stitch, []))\
                )):
            yield "skip"
            iline += 1
        elif all(( current_stitch not in threads[ current_thread ], \
                any( s in visited for s in previous.get( current_stitch, [])),\
                )):
            tunnelthread = find_thread_to( current_stitch )
            for downstitch in downedges[ current_stitch ]:
                yield ( "tunnel", tunnelthread, tunnelindex )
                hastunnel.setdefault( downstitch, [] ).append( tunnelindex )
                tunnelindex += 1
            iline += 1
            if not [ threadi for threadi, _,_ in tunnel_snake \
                                if threadi == tunnelthread ]:
                tunnel_snake.append( (tunnelthread, irow, iline ) )
        else:
            raise Exception( current_stitch,threads[ current_thread ], \
                    visited, previous.get( current_stitch, [] ),
                    current_stitch in threads[ current_thread ], \
                    all( s in visited for s in previous.get( current_stitch, [])),\
                    )



def shorten_command_array( rows, command_to_symbol ):
    shortened_commands = []
    for row in rows:
        short_row = []
        shortened_commands.append( short_row )
        short_row.append( [ 1, row[0] ] )
        for com in row[ 1: ]:
            if short_row[ -1 ][ 1 ] == com:
                short_row[ -1 ][0] += 1
            else:
                short_row.append( [1, com] )

    for short_row in shortened_commands:
        for com_list in short_row:
            com_list[1] = command_to_symbol.get( com_list[1], com_list[1] )

    return shortened_commands

    

    def to_symbol( n, c ):
        if c != "\n":
            return "".join( (str(n), stitchsymbol.get( c,c ) ))
        else:
            return "\n"*n
    shortened_commands = [ to_symbol( n, c ) for n, c in shortened_commands ]
    row_commands = [[]]
    for c in shortened_commands:
        if c != "\n":
            row_commands[-1].append( c )
        else:
            row_commands.append([])


def tomanual( strickgraph, stitchinfo, manual_type="thread" ):
    """text a manual for the given complete strickgraph

    :todo: rewrite algorithms for-loops. Because, they are shit
    """
    #startside = strickgraph.get_startside()
    #rows = find_rows( strickgraph )
    stitchsymbol = stitchinfo.stitchsymbol
    rows = strickgraph.get_rows( presentation_type="thread" )
    startnode = rows[0][0]
    startside = strickgraph.get_nodeattr_side()[ startnode ]
    nodeattributes = strickgraph.get_nodeattr_stitchtype()
    stitchtypes = strickgraph.get_nodeattr_stitchtype()


    threads = strickgraph.get_threads()
    previous = strickgraph.get_previous_stitches()


    qq = create_manual_commands( rows, stitchtypes, threads, previous )
    raise Exception( list(qq) )

    find_thread_to = lambda stitch: ( i for i, stitches in enumerate(threads) \
                                    if stitch in stitches ).__next__()
    current_thread = find_thread_to( startnode )

    visited = []
    is_not_visited = lambda x: x not in visited
    commandlist = []
    tunnel_anchors = []
    j=-1
    for i in range( len(threads)*len(rows)):
        if current_thread == None:
            break
        j += 1
        tmprow = rows[ j ]
        for s in filter( is_not_visited, tmprow ):
            if current_thread != None:
                if s in threads[ current_thread ] and all( tmps in visited \
                                            for tmps in previous.get(s,[]) ):
                    visited.append( s )
                    commandlist.append( stitchtypes[ s ] )
                    if s == threads[ current_thread ][-1]:
                        if tunnel_anchors:
                            current_thread, j = tunnel_anchors.pop(0)
                            j = j-1
                            raise Exception( "brubru" )
                            break
                        else:
                            current_thread = None
                elif any( tmps in visited for tmps in previous.get(s,[]) ):
                    commandlist.append( ( "tunnel", find_thread_to(s) ) )
                    alter_thread = find_thread_to(s)
                    if [ x for x in tunnel_anchors if x[0]==alter_thread ]:
                        pass
                    else:
                        tunnel_anchors.append( ( alter_thread, j ) )
                elif s not in threads[ current_thread ]:
                    continue
                elif s in threads[ current_thread ] and \
                        any( tmps not in visited for tmps in previous.get(s,[])):
                    print( "threads: ", threads )
                    print( "current stitch: ", s )
                    print( "thread: ", current_thread, threads[current_thread] )
                    print( "prev: ", previous.get(s, []))
                    print( "visited: ", visited )
                    raise NotImplementedError( "First make next thread as far "\
                            "as possible before coming back to this" )
                else:
                    raise NotImplementedError( "something previous is not ..." )
            else:
                raise NotImplementedError( "multiple threads not implemented" )
        commandlist.append( "\n" )
    raise Exception( commandlist )

    shortened_commands = []
    shortened_commands.append( [ 1, commandlist[0] ] )
    for com in commandlist[ 1: ]:
        if shortened_commands[ -1 ][ 1 ] == com:
            shortened_commands[ -1 ][0] += 1
        else:
            shortened_commands.append( [1, com] )
    def to_symbol( n, c ):
        if c != "\n":
            return "".join( (str(n), stitchsymbol.get( c,c ) ))
        else:
            return "\n"*n
    shortened_commands = [ to_symbol( n, c ) for n, c in shortened_commands ]
    row_commands = [[]]
    for c in shortened_commands:
        if c != "\n":
            row_commands[-1].append( c )
        else:
            row_commands.append([])

    if manual_type == "machine":
        for i, row in enumerate( row_commands ):
            if startside=="right":
                if i%2==1:
                    row.reverse()
            else:
                if i%2==0:
                    row.reverse()
    if len( row_commands[-1] )==0:
        row_commands.pop()
    row_commands = [ " ".join(row) for row in row_commands ]
    manual = "\n".join( row_commands )
    return manual

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


def asdf():
    stitch = str
    stitches: Iterable[ stitch ]
    predecessors: dict[ stitch, Iterable[ stitch ]]

    upedges: Sequence[ Tuple[ stitch, stitch ] ]
    upedges_from = { e[0]:i for i, e in enumerate( upedges ) }
    downedges_from = { e[1]:i for i, e in enumerate( upedges ) }

    holder_nooses = []
    saved_tunnels = []
    next_nooses = []

    raise Exception( "to be continued" )


from . import method_Astar #import Astar, TargetUnreachable

def _find_requisites_for_stitches( upedges, nextedges, threads, stitchside, \
                                                        lefttoright_rows ):
    """

    :param lefttoright_rows: from strickgraph.get_rows(
                presentation_type='machine', lefttoright_side='right' )
    :type lefttoright_rows: Iterable[ Hashable ]
            "knitted_stitches": set(),
    """
    all_stitches = stitchside.keys()
    stitch_needednooses: dict[Hashable, list] = { s:list() for s in all_stitches }
    stitch_neededstitches: dict[ Hashable, list] = { s:[] for s in all_stitches }
    stitch_neededthread: dict[ Hashable, int ] = { s:None for s in all_stitches }
    for i, e in enumerate( upedges ):
        st1, st2 = e
        stitch_needednooses.setdefault( st2, list() ).append( i )
    for st1, st2 in nextedges:
        #stitch_needednooses.setdefault( st2, [list(),list(),None] )[1].append(st1)
        stitch_neededstitches.setdefault( st2, [] ).append( st1 )
    for ithread, thread_stitches in enumerate( threads ):
        for st in thread_stitches:
            stitch_neededthread[ st ] = ithread
            #stitch_needednooses.setdefault( st, [list(),list(),None] )[2] = ithread

    stitch_position = {}
    for i, row in enumerate( lefttoright_rows ):
        for j, st in enumerate( row ):
            stitch_position[ st ] = (i,j)
    noose_ordering = {}
    for i, e in enumerate( upedges ):
        st1, st2 = e
        noose_ordering[ i ] = tuple( stitch_position[x][1] for x in (st1, st2) )

    #sorting needednooses for single stitches
    for st, nooselist in stitch_needednooses.items():
        extra_options = { "reverse": stitchside[st] == "left" }
        nooselist = sorted( nooselist, key=noose_ordering.get, **extra_options )
        stitch_needednooses[ st ] = tuple( nooselist )

    return stitch_needednooses, stitch_neededstitches, stitch_neededthread

def _find_generated_nooses( upedges, threads ):
    stitch_generatenooses = {}
    for i, e in enumerate( upedges ):
        st1, st2 = e
        stitch_generatenooses.setdefault( st1, list() ).append( i )
    for ithread, thread_stitches in enumerate( threads ):
        for st in thread_stitches:
            stitch_generatenooses.setdefault( st, list() )
    return stitch_generatenooses

def create_knit_commandarray( strickgraph ):
    """

    :todo: nooseordering works only, if nooses, dont skip rows
    :todo: nooseordering is not uniformly ordered from left to right but
            instead leaf to right for left-knitted stitches and viceversa
    """
    stitches = strickgraph.get_nodeattr_stitchtype()
    stitchside = strickgraph.get_nodeattr_side()
    upedges = [ (v1, v2) for v1, v2, data in strickgraph.get_edges_with_labels() \
                                                    if data=="up" ]
    nextedges = [ (v1, v2) for v1, v2, data in strickgraph.get_edges_with_labels()\
                                                    if data=="next" ]
    threads = strickgraph.get_threads()
    rows = strickgraph.get_rows( presentation_type='machine', \
                                                    lefttoright_side='right' )

    stitch_generatenooses = _find_generated_nooses( upedges, threads )
    stitch_needednooses, stitch_neededstitches, stitch_neededthread \
            = _find_requisites_for_stitches( upedges, nextedges, threads, \
                                                    stitchside, rows )
    dict_threads = { i:stitch_list for i, stitch_list in enumerate( threads )}

    myknitter = machine_knitter_producer( stitch_needednooses, stitch_neededstitches, stitch_neededthread, dict_threads, rows )
    options = {
            "stitch_to_generated_nooses": stitch_generatenooses, 
            "stitchtype": stitches,
            }
    source_status = machine_knitter_producer_status( **options, 
                            knitted_stitches=frozenset(), current_thread=0 )
    target_statuses = [ machine_knitter_producer_status( **options, \
                            knitted_stitches=frozenset(stitches), current_thread=i )\
                            for i in dict_threads ]
    class pathnode:
        knitter = myknitter
        def __init__( self, status ):
            self.status = status
        def mindist( self, target ):
            return self.knitter.minimal_distance( self.status, target.status )
        def neighbours( self ):
            cls = type( self )
            for command, cost in self.knitter.possible_commands( self.status ):
                newstatus = self.knitter.execute( self.status, *command )
                yield cls( newstatus ), cost, command
        def __eq__( self, other ):
            return self.status == other.status
        def __hash__( self ):
            return hash( self.status )
        def __repr__( self ):
            return str([ dict(self.status)[a] \
                     for a in ["knitted_stitches","saving_needle","working_needle","saved_singlenooses"]])
    source = pathnode( source_status )
    targets = [ pathnode( status ) for status in target_statuses ]
    path, edges = method_Astar.Astar( source, targets )
    return [ n.status for n in path ], edges


from abc import ABC, abstractmethod
class abs_knitter_status( ABC ):
    @abstractmethod
    def __iter__( self ):
        pass
    @abstractmethod
    def to_graph( self ):
        pass
    @abstractmethod
    def __hash__( self ):
        pass
    @abstractmethod
    def __eq__( self, other ):
        pass


class costfunction( ABC ):
    """Inputs of sorted, as example ints"""
    @abstractmethod
    def __gt__( self ):
        """Method used by sorted"""
        pass
    @abstractmethod
    def __add__( self, other ):
        """Must be addable"""
        pass

from collections.abc import Container
class abstract_machine( ABC ):
    """
    
    :cvar possible_commands: if command is generally valid it is 
                contained in possible_commands.
    :todo: possible_commands might be better as method
    """
    valid_commands: Container

    @abstractmethod
    def execute( self, status, command, *command_args ):
        """Executes command and returns new status"""
        pass
    @abstractmethod
    def possible_commands( self, status ):
        """Gives back all possible commands to execute next with an arbitrary
        costvalue.
        
        :rtype: Iterator[ command_array, costfunction ]
        :returns: a list of all possible commands combined with an arbitrary
                cost
        """
        pass
    @abstractmethod
    def minimal_distance( self, first_status, second_status ):
        """Gives a lower bound to the cost to get from first status to
        second status. Real cost should never be lower.

        :rtype: costfunction
        :returns: Minimal distance to get from first to second status
        """
        pass

from dataclasses import dataclass
from collections.abc import Mapping
import copy
@dataclass
class machine_knitter_producer_status( Mapping ):
    stitch_to_generated_nooses: dict
    stitchtype: dict
    knitted_stitches: frozenset = frozenset()
    saving_needle: tuple = tuple()
    working_needle: tuple = tuple()
    saved_singlenooses: frozenset = frozenset()
    current_thread: int = 0
    used_nooses: tuple = tuple()
    def __getitem__( self, attr ):
        return copy.deepcopy( self.__dict__[attr] )
    def __iter__( self ):
        for q in self.__dict__:
            yield q
    def __len__( self ):
        return len( self.__dict() )
    def __hash__( self ):
        sorted_knitted = tuple( sorted( self.knitted_stitches, key=hash ) )
        sorted_nooses = tuple( sorted( self.saved_singlenooses, key=hash ))
        return hash( (sorted_knitted, self.saving_needle, \
                        self.working_needle, sorted_nooses, \
                        self.current_thread ))
    def __eq__( self, other ):
        try:
            cond1 = self.knitted_stitches == other.knitted_stitches
            cond2 = self.saving_needle == other.saving_needle
            cond3 = self.working_needle == other.working_needle
            cond4 = self.saved_singlenooses == other.saved_singlenooses
            cond5 = self.current_thread == other.current_thread
        except AttributeError:
            return False
        return all(( cond1, cond2, cond3, cond4, cond5 ))
    def get_attributes( self ):
        return copy.deepcopy( self.__dict__ )


class machine_knitter_producer_commands:
    def turn_needles( self, status ):
        info = dict(status)
        info["working_needle"], info["saving_needle"] \
                = info["saving_needle"], info["working_needle"]
        return machine_knitter_producer_status( **info )

    def knit_stitch( self, status, stitchtype, stitchname=None, \
                            generated_noose_ids=None):
        """

        :type generated_noose_ids: Iterable
        :param generated_noose_ids:
        :todo: stitchtyype to number nooses must be added somehow
        """
        info = dict( status )
        def namegen():
            i=0
            while True:
                yield str(i)
                i+=1
        if stitchname is None:
            raise Exception()
            stitchname = ( n for n in namegen() if n not in info["stitchtype"] )
            info["stitchtype"][stitchname] = stitchtype
        if generated_noose_ids is None:
            raise NotImplementedError()
            #generated_noose_ids = info["stitch_to_generated_nooses"][ stitchname ]
        #thread = info["stitch_neededthread"][stitchname]
        #predecessors = info["stitch_neededstitches"][stitchname]
        working_needle_req = self.stitches_needednooses[ stitchname ]
        number_needed_nooses = len(working_needle_req)
        #stitchtype to number of nooses
        #if info["knitted_stitches"].issuperset( predecessors )\
        #                    and thread == info["current_thread"]:
        #if all( r==info["working_needle"][i] for i,r in enumerate( working_needle_req ) ):
        #assert len(generated_noose_ids) == stitchinfo[stitchtype]["upedges"]
        if len( info["working_needle"] ) >= number_needed_nooses:
            info["working_needle"] = info["working_needle"][ number_needed_nooses: ]
            info["knitted_stitches"] = info["knitted_stitches"]\
                                        .union( [stitchname] )
            info["saving_needle"] = tuple(generated_noose_ids) + info["saving_needle"]
            #for new_noose in generated_noose_ids:
            #    info["saving_needle"] = (new_noose,) + info["saving_needle"]
        else:
            raise Exception()
        return machine_knitter_producer_status( **info )

    def save_noose( self, status, noose_id ):
        """

        :raises: IndexError
        :todo: rework how nooses are saved. Save via custom id but nooses 
                themselve have ids, so there should be a mapping for this
        """
        info = dict(status)
        assert len( info["working_needle"] ) >= 1
        info["saved_singlenooses"] = info["saved_singlenooses"] \
                                    .union(info["working_needle"][:1])
        noose = info["working_needle"][ 0 ]
        info["working_needle"] = info["working_needle"][ 1: ]
        #noosedict = dict(info["used_nooses"])
        #noosedict[ "noose_id" ] = noose
        info["used_nooses"] = info["used_nooses"] + ( noose_id, )
        return machine_knitter_producer_status( **info )

    def load_noose( self, status, noose_id ):
        """

        :raises: KeyError
        :todo: see save_noose
        """
        info = dict( status )
        assert noose in info["saved_singlenooses"]
        #noosedict = dict(info["used_nooses"])
        #noose = noosedict.pop( noose_id )
        info[ "saved_singlenooses" ] = info[ "saved_singlenooses" ]-{noose_id}
        info["saving_needle"] = (noose_id,) + info["saving_needle"]
        return machine_knitter_producer_status( **info )

    def change_thread( self, status, thread ):
        info = dict( status )
        info["current_thread"] = thread
        return machine_knitter_producer_status( **info )


class command_valid:
    def __contains__( self, command ):
        comstring = command[0]
        return comstring in ["switch_thread", "knit", "load_noose", \
                            "save_noose", "turn"]

def ladder():
    i=0
    while True:
        yield i
        i += 1

class machine_knitter_producer( machine_knitter_producer_commands ):
    def __init__( self, stitches_needednooses, stitch_neededstitches, \
                            stitch_neededthread, thread_to_stitch, rows ):
        self.valid_commands = command_valid()
        self.stitches_needednooses = stitches_needednooses
        self.stitch_neededthread = stitch_neededthread
        self.stitch_neededstitches = stitch_neededstitches
        self.thread_to_stitch = thread_to_stitch
        self.rows = rows

    def execute( self, status, command, *command_args ):
        if ( command, *command_args ) not in self.valid_commands:
            raise ValueError( "command not valid" )
        if command=="turn":
            return self.turn_needles( status )
        elif command=="knit":
            stitchname = command_args[1]
            new_nooses = status.stitch_to_generated_nooses[ stitchname ]
            return self.knit_stitch( status, *command_args, \
                    generated_noose_ids = new_nooses)
        elif command=="save_noose":
            noose_id = command_args[0]
            return self.save_noose( status, noose_id )
        elif command=="load_noose":
            noose = command_args[0]
            return self.load_noose( status, noose )
        elif command=="switch_thread":
            thread = command_args[0]
            return self.change_thread( status, thread )

    def _find_knitable_stitch( self, status ):
        for st, working_needle_req in self.stitches_needednooses.items():
            thread = self.stitch_neededthread[st]
            predecessors = self.stitch_neededstitches[st]
            if st not in status.knitted_stitches:
                if status.knitted_stitches.issuperset( predecessors ) \
                            and thread == status.current_thread:
                    try:
                        if all( r==status.working_needle[i] \
                                for i,r in enumerate( working_needle_req ) ):
                            yield st
                    except IndexError:
                        pass

    def possible_commands( self, status ):
        yield ("turn",), 1
        for st in self._find_knitable_stitch( status ):
            st_type = status.stitchtype[st]
            yield ("knit", st_type, st), 1
        for noose in status.saved_singlenooses:
            yield ("load_noose", noose), 1
        if len( status.working_needle ) > 0:
            inoose = (i for i in ladder() if i not in status.used_nooses).__next__()
            assert type(inoose) == int
            yield ( "save_noose", inoose ), 2
        #for i in status.threads:
        for i in self.thread_to_stitch:
            if i != status.current_thread:
                yield ( "switch_thread", i ), 1

    def minimal_distance( self, first, second ):
        if first.knitted_stitches.difference( second.knitted_stitches ):
            raise method_Astar.TargetUnreachable()

        missing_stitches = second.knitted_stitches\
                            .difference( first.knitted_stitches )
        missing_threads = [ i for i, t in self.thread_to_stitch.items() \
                            if len(missing_stitches.union(t))>0 \
                            and i != first.current_thread ]
        missing_stitches_rows = [ missing_stitches.intersection(row) \
                            for row in self.rows ]
        row_to_need_noose = lambda row: it.chain.from_iterable( \
                            self.stitches_needednooses[st] \
                            for st in row )
        missing_nooses_rows = [[ no for no in row_to_need_noose(row) \
                                if no not in first.working_needle ] \
                                for row in missing_stitches_rows ]
        missing_nooses_rows = [ row for row in missing_nooses_rows \
                                if len(row) > 0 ]
        switch_thread_cost = 0 if first.current_thread == second.current_thread \
                                else 1
        noose_switching_cost = abs( len(first.saved_singlenooses) \
                                - len(second.saved_singlenooses))
        return len( missing_stitches ) + switch_thread_cost + noose_switching_cost \
                + 2*len( missing_threads ) + len(missing_nooses_rows)
