"""Identifier for middle chasm from top of strickgraph.
See createcloth.abstract_identifier

"""
from ..strickgraph import strickgraph
from collections.abc import Container
from .method_classify import classify, chasm_properties
from . import method_generate_example as mge

class chasm_identifier():
    """Classifier for chasms"""
    def classify( self, target_strickgraph ):
        """Classify the chasms of a strickgraph. Raises Exception, when no 
        chasm is found or given strickgraph is not valid for classifier

        :param strickgraph:
        :rtype: chasm_properties
        """
        return classify( target_strickgraph )

    def create_strickgraph( self, attributes ):
        """Generator for strickgraph

        :param attributes: Attributes which are fulfilled by return strickgraph
        :type attributes: chasm_properties
        :returns: Strickgraph with chasm, fullfilling given attributes
        :rtype: strickgraph
        """
        return mge.generate_example( **props, height=7, width=20 )


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

