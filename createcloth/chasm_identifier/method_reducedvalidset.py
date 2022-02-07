from .method_classify import line_identifier, \
                            line_identifier_reversed, \
                            chasm_properties
from collections.abc import Container, Mapping, Iterable
import itertools as it

class reduced_simple_chasms( Iterable ):
    def __init__( self, height, width ):
        self.height = height
        self.width = width

    def __iter__( self ):
        for chasm_height in range( 1, self.height-2 ):
            for chasm_width in range( 1, self.width-8 ):
                possible_linetypes = ["plain", "decrease", "increase" ]
                for lines in it.product( possible_linetypes, repeat=chasm_height-1 ):
                    ll = tuple( it.chain( lines, ( "top", ) ) )
                    yield chasm_properties( chasm_height, ll, chasm_width, [0,1,2] )
