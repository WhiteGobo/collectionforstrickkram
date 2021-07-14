from ..strickgraph import strickgraph
from ..verbesserer import multifrommanuals
from typing import Iterable, Tuple, Iterator
import itertools as it
from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease


def method1( pairlist: Iterable[ Tuple[ str, str ]], \
                                    side="both", reverse=False,
                                    oldtranlatorlist = [] ):

    myersetzer = manstomulti( pairlist, reverse = reversed, side = "both", \
                                oldtranslatorlist = oldtranslatorlist )

def create_example_strickset( verbessererlist, strickgraphsize, \
                            min_row_length=12 ) -> Iterator:
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
            differences = it.product( *(rowtype.get_downupdifference_examples()\
                                        for rowtype in rowtypelist[1:-1] ))
            upedges = [ tuple(it.accumulate( it.chain( (0,), d ) )) \
                                    for d in differences ]
            upedges = [ tuple( single + min_row_length - min(t) \
                                    for single in t ) \
                                    for t in upedges ]
            upedges = [ q for q in upedges \
                                    if isplain(rowtypelist, upedges=q) ]
            graphs_to_upedges[ rowtypelist ] = upedges
    #print({ ", ".join( str(q) for q in a): b \
    #        for a,b in graphs_to_rowlengths.items() })
    for linetypes, possible_upedges in graphs_to_upedges.items():
        for upedges in possible_upedges:
            yield linetypes, upedges



def find_to_graph_onedifferencegraphs( maingraph, brulist, min_row_length=10 ):
    maingraph_row_lengths = [1,2,3]
    for graphtype in brulist:
        firstrowlength = maingraph_row_lengths
