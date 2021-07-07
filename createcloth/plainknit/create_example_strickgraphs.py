from ..strickgraph import strickgraph
from ..verbesserer import multifrommanuals
from typing import Iterable, Tuple
import itertools as it


def method1( pairlist: Iterable[ Tuple[ str, str ]], \
                                    side="both", reverse=False,
                                    oldtranlatorlist = [] ):

    myersetzer = manstomulti( pairlist, reverse = reversed, side = "both", \
                                oldtranslatorlist = oldtranslatorlist )

from .state import start, end, leftplane, rightplane, lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
def create_example_strickset( verbessererlist, strickgraphsize ):
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
    for rowtypelist in possible_rowtypelist:
        if isplain( rowtypelist ):
            print( [ str(q) for q in rowtypelist ] )
            
        #strickgraph = foo( rowtypelist )


