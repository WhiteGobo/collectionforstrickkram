"""
main function here is tomanual

:todo: support for load_stitchinfo. support seems not complete because example
        character_dictionary
"""
import networkx as netx
import regex
import itertools as it
from collections.abc import Container

from .. import strickgraph as mod_strickgraph
from .datacontainer import strick_datacontainer
#from . import handknitting_terms
#from . import machine_terms
import logging
logger = logging.getLogger( __name__ )
from typing import Tuple
from itertools import zip_longest

from dataclasses import dataclass, field
from collections.abc import Mapping
import copy

class class_special_commands( Container ):
    """Class for identifying special commands inside the manual"""
    def __getitem__( self, x ):
        if not self.__contains__( x ):
            raise KeyError( f"{x} isnt contained")
        mymatch = regex.match( r"(?P<com>\S+)(?P<val>\d+)", x )
        if mymatch["com"] == "switch":
            return ( "switch_thread", int(mymatch["val"]))
        elif mymatch["com"] == "tunnel":
            return ( "save_noose", int(mymatch["val"]))
        elif mymatch["com"] == "load":
            return ( "load_noose", int(mymatch["val"]))
        raise Exception( "oops something went wrong, strange input", x )

    def __contains__( self, x ):
        try:
            mymatch = regex.match( r"(?P<command>\S+)(?P<qq>\d+)", x )
        except TypeError:
            return False
        if not mymatch:
            return False
        if mymatch.span()[1] < len(x):
            return False
        asddict = mymatch.groupdict()
        return asddict[ "command" ] in [ "switch", "tunnel", "load" ]

    def get( self, x, default=None ):
        if self.__contains__( x ):
            self.__getitem__( x )
        else:
            return default



class strick_manualhelper( strick_datacontainer ):
    def to_manual( self, stitchinfo, manual_type="machine" ):
        statuses, commands = create_knit_commandarray( self, stitchinfo )
        stitchtypes = self.get_nodeattr_stitchtype()
        startside = self.get_startside()
        rows = [[]]
        nooses = {}
        noose_int = 0
        for c in commands:
            if c[0] == "save_noose":
                nooses[ c[1] ] = noose_int
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

    @classmethod
    def from_manual( cls, manual, stitchinfo, manual_type="machine", \
                                        startside="right", reverse=False ):
        manual = transform_manual_to_listform( manual )
        mystitchinfo = stitchinfo
        if manual_type in mod_strickgraph.machine_terms:
            revi = 1 if startside=="right" else 0
            for i in range( len(manual) ):
                if i == revi:
                    manual[ i ].reverse()
        elif manual_type in mod_strickgraph.handknitting_terms:
            pass
        else:
            raise Exception( "dont knot manual_type %s" %(manual_type) )

        if reverse:
            _reverse_every_row( manual )
        manual = transform_to_single_key( manual )
        manual = symbol_to_stitchid( manual, mystitchinfo )
        commands = []
        first=True
        sidelist = ["right", "left"] if startside=="right" else ["left", "right"]
        special_commands = class_special_commands()
        for i, row in enumerate( manual ):
            tmpside = sidelist[ i%2 ]
            if first:
                first = False
            else:
                commands.append( ("turn",) )
            for manual_command in row:
                if manual_command in special_commands:
                    commands.append( special_commands[ manual_command ] )
                else:
                    st_type = manual_command
                    commands.append(("knit", st_type, tmpside ))
        mymachine = machine_knitter_producer_commands( stitchinfo )
        status = strickgraph_creation_status()
        for com in commands:
            try:
                status = mymachine.execute( status, *com )
            except ValueError as err:
                raise BrokenManual() from err
        mystrickgraph2 = cls( status.stricknodes, status.strickedges )
        return mystrickgraph2


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


class BrokenManual( Exception ):
    pass


def symbol_to_stitchid( manual, mystitchinfo ):
    #namedict = { mystitchinfo.symbol[x]:x for x in mystitchinfo.symbol }
    namedict = mystitchinfo.stitchsymbol_to_stitchid
    special_commands = class_special_commands()
    for i in range( len(manual)):
        assert all( x in namedict or x in special_commands \
                        for x in manual[i]), (i,manual)
        try:
            manual[i] = [ namedict.get(x,x) for x in manual[i] ]
        except KeyError as err:
            raise KeyError("manual contains keys, that are not supported", \
                                                mystitchinfo.stitchsymbol ) from err
    return manual


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

def create_knit_commandarray( strickgraph, stitchinfo ):
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

    myknitter = machine_knitter_producer( stitch_needednooses, stitch_neededstitches, stitch_neededthread, dict_threads, rows, stitchinfo )
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

@dataclass
class machine_knitter_producer_status( Mapping ):
    stitch_to_generated_nooses: dict = field( default_factory=dict )
    stitchtype: dict = field( default_factory=dict )
    knitted_stitches: frozenset = frozenset()
    saving_needle: tuple = tuple()
    working_needle: tuple = tuple()
    saved_singlenooses: frozenset = frozenset()
    current_thread: int = 0
    thread: dict = field( default_factory=dict )
    used_nooses: dict = field( default_factory=dict)
    noose_to_stitch: dict = field( default_factory=dict )
    def __getitem__( self, attr ):
        return copy.deepcopy( self.__dict__[attr] )
    def __iter__( self ):
        for q in self.__dict__:
            yield q
    def __len__( self ):
        return len( self.__dict() )
    def __hash__( self ):
        sorted_knitted = tuple( sorted( self.knitted_stitches, key=hash ) )
        nooses = ( self.used_nooses[n_id] for n_id in self.saved_singlenooses )
        sorted_nooses = tuple( sorted( nooses, key=hash ))
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

class strickgraph_creation_status(machine_knitter_producer_status):
    def __init__( self, *args, stricknodes = None, strickedges=None, **kwargs ):
        super().__init__( *args, **kwargs )
        if stricknodes is not None and strickedges is not None:
            self.stricknodes = stricknodes
            self.strickedges = strickedges
        elif stricknodes is None and strickedges is None:
            self.stricknodes = {}
            self.strickedges = []


class machine_knitter_producer_commands:
    def __init__( self, stitchinfo ):
        self.valid_commands = command_valid()
        self.stitchinfo = stitchinfo

    def execute( self, status, command, *command_args ):
        if ( command, *command_args ) not in self.valid_commands:
            raise ValueError( "command not valid" )
        if command=="turn":
            return self.turn_needles( status )
        elif command=="knit":
            extraoptions = {}
            if len( command_args ) >= 3:
                try:
                    stitchname = command_args[2]
                except Exception as err:
                    raise Exception( command_args ) from err
                new_nooses = status.stitch_to_generated_nooses[ stitchname ]
                extraoptions = { "generated_noose_ids": new_nooses }
            return self.knit_stitch( status, *command_args, **extraoptions )
        elif command=="save_noose":
            noose_id = command_args[0]
            return self.save_noose( status, noose_id )
        elif command=="load_noose":
            noose = command_args[0]
            return self.load_noose( status, noose )
        elif command=="switch_thread":
            thread = command_args[0]
            return self.change_thread( status, thread )

    def turn_needles( self, status ):
        info = dict(status)
        info["working_needle"], info["saving_needle"] \
                = info["saving_needle"], info["working_needle"]
        return type(status)( **info )

    def knit_stitch( self, status, stitchtype, stitchside, stitchname=None, \
                            generated_noose_ids=None):
        """

        :type generated_noose_ids: Iterable
        :param generated_noose_ids:
        :todo: stitchtyype to number nooses must be added somehow
        :raises: ValueError
        """
        info = dict( status )
        def namegen():
            i=0
            while True:
                yield str(i)
                i+=1
        if stitchname is not None and stitchname in info["stitchtype"]:
            if info["stitchtype"][stitchname] != stitchtype:
                raise ValueError("wrong stitchtype to already defined stitch")
        elif stitchname is None:
            stitchname = ( n for n in namegen() \
                            if n not in info["stitchtype"] ).__next__()
            info["stitchtype"][stitchname] = stitchtype
        if generated_noose_ids is None:
            generated_noose_ids = [ (stitchname, i) \
                                for i in range(self.stitchinfo.upedges[stitchtype]) ]
        number_needed_nooses = self.stitchinfo.downedges[stitchtype]
        assert len(generated_noose_ids) == self.stitchinfo.upedges[stitchtype]
        if len( info["working_needle"] ) >= number_needed_nooses:
            used_nooses = tuple(info["working_needle"][ :number_needed_nooses ])
            info["working_needle"] = info["working_needle"][ number_needed_nooses: ]
            info["knitted_stitches"] = info["knitted_stitches"]\
                                        .union( [stitchname] )
            info["saving_needle"] = tuple(generated_noose_ids) + info["saving_needle"]
            info["thread"][info["current_thread"]] \
                    = info["thread"].get(info["current_thread"], tuple()) \
                    + (stitchname,)
            for new_noose in generated_noose_ids:
                info["noose_to_stitch"][ new_noose ] = stitchname
        else:
            raise ValueError( "not enough nooses for stitch" )
        if "stricknodes" in info:
            info["stricknodes"][stitchname] \
                            = { "side":stitchside, "stitchtype":stitchtype}
            try:
                prev = info["thread"][info["current_thread"]][ -2 ]
                info["strickedges"].append( ( prev, stitchname, "next" ) )
            except IndexError:
                pass
            for downnoose in used_nooses:
                downstitch = info["noose_to_stitch"][downnoose]
                info["strickedges"].append( ( downstitch, stitchname, "up" ) )
        return type(status)( **info )

    def save_noose( self, status, noose_id ):
        """

        :raises: IndexError
        :todo: rework how nooses are saved. Save via custom id but nooses 
                themselve have ids, so there should be a mapping for this
        """
        info = dict(status)
        assert len( info["working_needle"] ) >= 1
        info["saved_singlenooses"] = info["saved_singlenooses"] \
                                    .union([noose_id])
        noose = info["working_needle"][ 0 ]
        info["working_needle"] = info["working_needle"][ 1: ]
        noosedict = dict(info["used_nooses"])
        assert noose_id not in noosedict
        noosedict[ noose_id ] = noose
        info["used_nooses"] = noosedict
        #info["used_nooses"] = info["used_nooses"] + ( noose_id, )
        return type(status)( **info )

    def load_noose( self, status, noose_id ):
        """

        :raises: KeyError
        :todo: see save_noose
        """
        info = dict( status )
        noosedict = dict(info["used_nooses"])
        noose = noosedict[ noose_id ]
        assert noose_id in info["saved_singlenooses"]
        info[ "saved_singlenooses" ] = info[ "saved_singlenooses" ]-{noose_id}
        info["saving_needle"] = (noose,) + info["saving_needle"]
        return type(status)( **info )

    def change_thread( self, status, thread ):
        info = dict( status )
        info["current_thread"] = thread
        return type(status)( **info )


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
                            stitch_neededthread, thread_to_stitch, rows, \
                            stitchinfo ):
        super().__init__( stitchinfo )
        self.stitches_needednooses = stitches_needednooses
        self.stitch_neededthread = stitch_neededthread
        self.stitch_neededstitches = stitch_neededstitches
        self.thread_to_stitch = thread_to_stitch
        self.rows = rows

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
            yield ("knit", st_type, "left", st ), 1
        for noose_id in status.saved_singlenooses:
            yield ("load_noose", noose_id), 1
        if len( status.working_needle ) > 0:
            noose_id = (i for i in ladder() if i not in status.used_nooses).__next__()
            yield ( "save_noose", noose_id ), 2
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
