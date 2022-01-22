"""This is an classifier module. For this should be some kind of guide, what 
an classifier should be able to do an some kind of generell coding-,
and naming-conventions.

It should contain following methods:
    * find_attributes
    * example_strickgraph_from_attributes
    * strickgraph_classifies(im not sure)
    * attributes_valid(im not sure)

Also it can contain following methods:
    * generate example attribute-compositions
    * alterators to alterate single attributes in a strickgraph

Also contains extra sets of possible attributes, if attributes arent
basic types (like ints or strings).
Attributes should be explained by a module, class or something similer 
and arte to be identified my strings.

:todo: objects may be more intuitive, than strings. maybe this should be
        further inspected
:todo: add own multisidealteratorclass inside this package, which augment
        the alterator with a from_attributes_of_plainknit-generator. Remove
        this generator from baseclass from createcloth.verbesserer

:cvar rowstates: set of all possible attributes for single rows
"""
#from typing import Iterable

#vector_plainknit_attribute = 

from . import rowstates

startsides = { "left", "right" }
"""possible values for 'startside'-attribute"""

#upedges: Iterable[ int ]

attributes = { "upedges", "startside", "linetypes" }

from .class_identifier import create_graph_from_linetypes
from .class_identifier import plainknit_strickgraph_identifier_a as plainknit_strickgraph_identifier
from .create_example_strickgraphs import create_example_strickset

from .method_isplain import isplain

def _load_alterator( filename ):
    from ..verbesserer import class_multi_sidealterator as _csa
    import pkg_resources
    try:
        abs_filename = pkg_resources.resource_filename( __name__, filename )
        with open( abs_filename, "rb" ) as increaser_file:
            myalterator = _csa.multi_sidealterator.fromxml( increaser_file.read() )
        return myalterator
    except Exception as err:
        return None

plainknit_increaser = _load_alterator( "plainknit_increaser.xml" )
"""increaser from file as in '.plainknit_increaser_file.xml'"""

plainknit_decreaser = _load_alterator( "plainknit_decreaser.xml" )
"""decreaser from file as described in '.plainknit_decreaser_file.xml'"""

