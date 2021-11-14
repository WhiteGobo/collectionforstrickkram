from ..strickgraph import strickgraph
from typing import Iterable, Tuple, Iterator
import itertools as it
from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
from .state import WrongSide, WrongDownUpEdges
from ..stitchinfo import basic_stitchdata as glstinfo

import numpy as np


from ..strickgraph import strickgraph
def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    """Create graph only from linetypes

    :todo: there is double?? in create_verbesserer
    """
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

def create_example_strickset( verbessererlist, strickgraphsize, \
                            min_row_length=12, startright=True ) -> Iterator:
    """Method for creating example strickgraphs with plainknit lineidentifiers"""
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


def create_stitchnumber_to_examplestrick( q ):
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
    from .examplestates import start, end, enddecrease,  lefteaves, righteaves,\
            leftplane, rightplane, plain, increase, decrease
    brubru = {}
    def mysort( q ):
        linetypes, original_upedges, stitches_per_line = q
        return sum( {start:0, end:0, plain:1, increase:2, decrease:2 }\
                    .get( line, 3 ) for line in linetypes )
    q = sorted( q, key=mysort )
    for linetypes, original_upedges, stitches_per_line in q:
        idarray = class_idarray( stitches_per_line )

        tmplist = brubru.setdefault( idarray, list() )
        tmplist.append( (linetypes, original_upedges) )

        less_graph = create_graph_from_linetypes( linetypes, original_upedges )
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
        return self.stitches_per_line == other.stitches_per_line


def order_neighbouring( brubru ):
    """ Helperfunction for creation of increaser and decreaser for 
    plainknitstrick

    :todo: remove this function
    """
    myergebnis = []
    tmpbib = {}
    for idarray, qpartial in brubru.items():
        #adding rowlength
        from . import examplestates as es
        for k in range( len(idarray) ):
            for adder in [{k:2}, {k:2,k-1:1}, {k:2,k+1:1}]:
                newidarray = idarray + [ adder.get(i, 0) \
                                        for i in range(len(idarray)) ]
                for linetype_out, upedges in qpartial:
                    for linetype_in, upe2 in brubru.get( newidarray, list() ):
                        unsimilarity_vector = tuple( i!=j \
                                    for i,j in zip(linetype_out,linetype_in ))
                        from itertools import compress
                        reduce_to_differencelines = lambda vector: tuple( \
                                    compress( range(-k,len(vector)-k), vector ))
                        q = reduce_to_differencelines( unsimilarity_vector )
                        try:
                            maxdiff = max( abs(i) for i in q )
                        except ValueError: #q is empty
                            maxdiff = 0
                        if maxdiff < 2:
                            upedges_out = upedges
                            #i-1 because its upedges not stitches in line
                            #upedges_in = tuple( x + adder.get( i, 0 ) \
                            #            for i, x in enumerate( upedges ) )

                            tmp = [ i \
                                    for i, t in enumerate(zip(upe2,upedges_out)) if abs(i-k)>2]
                            notneardifference_rows = [ t[1]-t[0] \
                                    for i, t in enumerate(zip(upe2,upedges_out)) if abs(i-k)>2]
                            upedges_in = tuple( ue+notneardifference_rows[0] \
                                    for ue in upe2 )

                            qqdiff = sum( upedges_in )-sum(upedges_out)
                            assert abs(qqdiff) <= 5, "most likely plane follows with increase, which is not covered by plain-strick"
                            newneighbourtuple = (\
                                    linetype_out,
                                    linetype_in, 
                                    upedges_out, 
                                    upedges_in, 
                                    k, 
                                    )
                            
                            #delete this
                            if newneighbourtuple not in myergebnis:
                                myergebnis.append( newneighbourtuple )
                                tmpid = (linetype_out, upedges_out, k )
                                if tmpid in tmpbib:
                                    a = create_graph_from_linetypes( linetype_out, upedges_out )
                                    b1 = create_graph_from_linetypes( linetype_in, upedges_in )
                                    m = tmpbib[ tmpid ]
                                    b2 = create_graph_from_linetypes( m[1], m[3] )
                                    print( a.to_manual( glstinfo ))
                                    print("")
                                    print( b1.to_manual( glstinfo ))
                                    print("")
                                    print( b2.to_manual( glstinfo ))
                                    raise Exception( idarray, newidarray, "-"*5, newneighbourtuple,"-"*5,  tmpbib[tmpid] )
                                else:
                                    tmpbib[ tmpid ] = newneighbourtuple
    return myergebnis

