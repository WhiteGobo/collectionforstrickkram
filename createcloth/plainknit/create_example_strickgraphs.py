from ..strickgraph import strickgraph
from typing import Iterable, Tuple, Iterator, Dict
import itertools as it
from .rowstates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
from .state import WrongSide, WrongDownUpEdges
from ..stitchinfo import basic_stitchdata as glstinfo
import math

import numpy as np


from ..strickgraph import strickgraph
def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    sides = ("right", "left") if startside=="right" else ("left", "right")
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    iline = range(len(downedges))
    allinfo = zip( linetypes, downedges, upedges, iline )
    try:
        graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                for s, down, up, i in allinfo ]
    except Exception as err:
        raise Exception( [str(a) for a in linetypes], downedges, upedges, iline ) from err
        raise err
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph



def method1( pairlist: Iterable[ Tuple[ str, str ]], \
                                    side="both", reverse=False,
                                    oldtranlatorlist = [] ):
    """ ??? """

    myersetzer = manstomulti( pairlist, reverse = reversed, side = "both", \
                                oldtranslatorlist = oldtranslatorlist )

def create_example_strickset( strickgraphsize, \
                                min_row_length=12, startright=True )-> Iterator:
    """Method for creating example strickgraphs with plainknit lineidentifiers

    :param strickgraphsize: number of rows of example
    :type strickgrapsize: int
    :param min_row_length: minimal length of all rows
    :type min_row_length: int
    :param startright: Lever if startside of first row is right
    :type startright: bool
    :returns: Iterator of example attribute constellation
    :rtype: Iterator[ plainknitattributetuple ]
    :todo: isplain will be removed
    """
    if strickgraphsize < 3:
        raise Exception( "strickgraphsize must be at least 3" )
    available_startrows = ( start, )
    available_middlerows = ( leftplane, rightplane, lefteaves, righteaves, \
                                                plain, increase, decrease )
    available_endrows = ( end, enddecrease )

    middlerows = it.repeat( available_middlerows, strickgraphsize-2 )
    possible_rowtypelist = it.product( available_startrows, *middlerows, \
                                                available_endrows )
    from .method_isplain import isplain
    brulist = []
    graphs_to_upedges = dict()
    for rowtypelist in possible_rowtypelist:
        if isplain( rowtypelist ):
            brulist.append( rowtypelist )
            differences = it.product( *(rowtype.get_updowndifference_examples()\
                                        for rowtype in rowtypelist[1:-1] ))
            upedges = [ tuple(it.accumulate( it.chain( (0,), d ) )) \
                                    for d in differences ]
            upedges = [ tuple( single + min_row_length - min(t) \
                                    for single in t ) \
                                    for t in upedges ]
            upedges = [ q for q in upedges if isplain(rowtypelist, upedges=q) ]
            graphs_to_upedges[ rowtypelist ] = upedges
    sides = ["right", "left"] if startright else ["left", "right"]
    for linetypes, possible_upedges in graphs_to_upedges.items():
        for upedges in possible_upedges:
            tmpup = list( upedges ) + [ upedges[-1], ]
            tmpdown = [ upedges[0], ] + list( upedges )
            try:
                iline = range(len(tmpup))
                calc_stitches = lambda rowtype, up, down, i: \
                                len(rowtype.create_example_row( down, up, \
                                side=sides[i%2] ))
                stitches_per_line = [ calc_stitches( rowtype, up, down, i )\
                                for rowtype, up, down, i \
                                in zip( linetypes, tmpup, tmpdown, iline ) ]
                if isplain( linetypes, upedges ):
                    yield linetypes, upedges, stitches_per_line
            except WrongDownUpEdges as err:
                pass
            except WrongSide:
                pass



def find_to_graph_onedifferencegraphs( maingraph, brulist, min_row_length=10 ):
    """Needed for creating increaser and decreaser"""
    maingraph_row_lengths = [1,2,3]
    for graphtype in brulist:
        firstrowlength = maingraph_row_lengths


def create_stitchnumber_to_examplestrick( q, startside="right" ):
    """Creates a mapping of a stitches_per_line via class_idarray to 
    possible linetypes and their real stitches_per_line. The stitches-per-line
    are saved as class_idarray. This is to compare different stitches-per-line
    which are comparable, if they are widened or shortened.

    :type q: Iterable[ Tuple[ linetype, ... ] ]
    :param q: Possible strickgraph represented from linetypes
    :returns: Mapping of id from stitches-per-line to possible linetypes 
            and their real stitches-per-line
    :rtype: Dict[ class_idarray, 
            List[ Tuple[Iterable[linetypes], Iterable[int]] ] ]
    """
    brubru = {}
    def mysort( q ):
        linetypes, original_upedges, stitches_per_line = q
        return sum( {start:0, end:0, plain:1, increase:2, decrease:2 }\
                    .get( line, 6 ) for line in linetypes )
    q = sorted( q, key=mysort )
    for linetypes, original_upedges, stitches_per_line in q:
        idarray = class_idarray( stitches_per_line )

        tmplist = brubru.setdefault( idarray, list() )
        tmplist.append( (linetypes, original_upedges) )

        #less_graph = create_graph_from_linetypes( linetypes, original_upedges, startside=startside )
    return brubru

class class_idarray():
    """Helperclass for creation of increaser and decreaser"""
    def __init__( self, stitches_per_line ):
        self.stitches_per_line = tuple( i - stitches_per_line[0] \
                                    for i in stitches_per_line)
    def __repr__( self ):
        return f"clidarr: {self.stitches_per_line}"
    def __hash__( self ):
        return self.stitches_per_line.__hash__()
    def __len__( self ):
        return len(self.stitches_per_line)
    def __add__( self, addtuple:Iterable[ int ] ):
        """
        :raises: TypeError
        """
        asdf = np.add( self.stitches_per_line, addtuple )
        return type(self)( asdf )
    def __eq__(self, other):
        if type( self ) == type(other):
            return self.stitches_per_line == other.stitches_per_line
        elif type( other ) == tuple:
            return self.stitches_per_line == other
        else:
            return False


from collections import Counter
def normalise( v1, v2 ):
    q = Counter( b -a for a, b in zip(v1, v2) )
    mindiff = max( q.keys(), key=q.get )
    norm = tuple( x - mindiff for x in v2 )
    return norm

def normalise_upedges( v1, v2, upedges2 ):
    q = Counter( b -a for a, b in zip(v1, v2) )
    mindiff = max( q.keys(), key=q.get )
    norm = tuple( number_edges - mindiff for number_edges in upedges2 )
    return norm


def order_to_nearest_neighbours( list_of_linelength, increase=True ):
    """

    :type list_of_linelength: Iterator[ Tuple[ int,... ] ]
    :rtype: Dict[ (int,int), Iterable[ int ] ]
    :returns: mapping of which linelength is neighboured to which one depending
            on linelengths and changedline. 
            Gives only increase or decrease depending on input 'increase. 
            linelength are described by integers
    """
    uniform_linelength_to_index: Dict[ uniform_linelength, int ] = {}
    for i, linelength in enumerate( list_of_linelength ):
        uni_ll = tuple( j-linelength[0] for j in linelength )
        uniform_linelength_to_index.setdefault( uni_ll, list() ).append( i )
    
    def asdf( v1, v2, changed_line ):
        diffarray = [ a-b for a,b in zip( v1, v2) ]
        maximal_distance = max( abs(i-changed_line) \
                                for i, diff in enumerate(diffarray) \
                                if diff!=0 )
        number_diff_lines = sum( 1 for diff in diffarray if diff!=0 )
        absolute_difference = sum( abs(diff) for diff in diffarray )
        return ( maximal_distance, number_diff_lines, absolute_difference )
    nearest_indices_to_index = {}
    for start_uni_ll, indexlist in uniform_linelength_to_index.items():
        number_rows = len( start_uni_ll )
        other_unill_list = list( filter( lambda x: x != start_uni_ll, \
                            uniform_linelength_to_index.keys() ) )
        normed_unill_list = [ normalise( start_uni_ll, ls ) \
                            for ls in other_unill_list ]
        for changed_line in range( number_rows ):
            if increase:
                onlyincrease_key = lambda unill: unill[ changed_line ] \
                                            > start_uni_ll[ changed_line ]
            else:
                onlyincrease_key = lambda unill: unill[ changed_line ] \
                                            < start_uni_ll[ changed_line ]
            filtered_unill_list = [ unill for unill in normed_unill_list \
                                            if onlyincrease_key(unill) ]
            if len( filtered_unill_list ) == 0:
                continue
            mykey = lambda v2: asdf( start_uni_ll, v2, changed_line )
            nearest_uni_ll = sorted( filtered_unill_list, key=mykey )[ 0 ]
            for firstindex in indexlist:
                secondunill = tuple( i-nearest_uni_ll[0] for i in nearest_uni_ll)
                possible_seconds = uniform_linelength_to_index[ secondunill ]
                nearest_indices_to_index[ (firstindex, changed_line) ] \
                                            = possible_seconds
    return nearest_indices_to_index
    


def order_neighbouring( brubru, startside ):
    """ Helperfunction for creation of increaser and decreaser for 
    plainknitstrick

    :todo: tidy up this function
    :param startside: must be 'right' or 'left'
    :type startside: str
    """
    assert startside in ( "right", "left" )
    from . import rowstates as es
    from itertools import compress
    myergebnis = []
    inthings = {}
    outthings = {}
    for idarray, qpartial in brubru.items():
        #adding rowlength
        for k in range( len(idarray) ):
            for adder in [{k:2}, {k:2,k-1:1}, {k:2,k+1:1}]:
                if min(adder) <0 or max(adder)>=len(idarray):
                    continue
                newidarray = idarray + [ adder.get(i, 0) \
                                        for i in range(len(idarray)) ]
                for linetype_in, upe2 in qpartial:
                    for linetype_out, upedges in brubru.get( newidarray, list() ):
                        unsimilarity_vector = tuple( i!=j \
                                    for i,j in zip(linetype_out,linetype_in ))
                        reduce_to_differencelines = lambda vector: tuple( \
                                    compress( range(-k,len(vector)-k), vector ))
                        q = reduce_to_differencelines( unsimilarity_vector )
                        try:
                            maxdiff = max( abs(i) for i in q )
                        except ValueError: #q is empty
                            maxdiff = 0
                        if maxdiff < 2:
                            upedges_out = upedges
                            tmp = [ i for i, t in enumerate(zip(upe2,upedges_out))\
                                    if abs(i-k)>2]
                            notneardifference_rows = [ t[0]-t[1] \
                                    for i, t in enumerate(zip(upedges_out,upe2)) \
                                    if abs(i-k)>2]
                            try:
                                difference_upedges_inandout = notneardifference_rows[0]
                            except IndexError as err: #to few rows
                                difference_upedges_inandout = upedges_out[k] - upe2[k] -2
                            upedges_in = tuple( ue + difference_upedges_inandout \
                                                                for ue in upe2 )

                            qqdiff = sum( upedges_in )-sum(upedges_out)
                            from ..verbesserer.class_side_alterator import multi_sidealterator as multialt
                            newneighbourtuple = multialt.linetypepair(
                                    linetype_out,
                                    linetype_in, 
                                    upedges_out, 
                                    upedges_in, 
                                    k, startside
                                    )
                            #assert abs(qqdiff) <= 3, "most likely plane follows with increase, which is not covered by plain-strick %s, %s, %s" %(str(newneighbourtuple), idarray, newidarray)
                            tmpin = (linetype_in, idarray, k)
                            tmpout = (linetype_out, newidarray, k)
                            assert tmpin not in inthings
                            assert tmpout not in outthings
                            inthings[ tmpin ] = newneighbourtuple
                            outthings[ tmpout ] = newneighbourtuple
                            assert newneighbourtuple not in myergebnis
                            myergebnis.append( newneighbourtuple )
    return myergebnis

