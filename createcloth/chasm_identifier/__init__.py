"""Identifier for middle chasm from top of strickgraph.
See createcloth.abstract_identifier

"""
from ..strickgraph import strickgraph
from collections.abc import Container

class sequence_int_container( Container ):
    """Contains all object of type Iterable[ int ]"""
    def __contains__( self, myobj ):
        try:
            oldlen=len(list( myobj ))
        except TypeError:
            return False
        myobj = list( myobj )

        cond1 = len(myobj) == oldlen
        cond2 = all( isinstance( i, int ) for i in myobj )
        return cond1 and cond2

attributes = { "crack_width": sequence_int_container() }

from .method_classify import classify
#def classify( mystrickgraph: strickgraph ):
#    pass

def create_strickgraph( attributes ) -> strickgraph:
    pass

def find_path( input_attributes, output_attributes ):
    pass
