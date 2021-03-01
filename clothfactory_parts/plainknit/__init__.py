"""
"""
import pkg_resources as _pkg
__doc__ = __doc__ + _pkg.resource_string( __name__, "README").decode( "utf-8" )

from .factory_datatype import strickgraph_property_plainknit, \
        strickgraph_isplainknit, \
        strickgraph_isnotplainknit

from .factory_leaf import \
        test_if_strickgraph_is_plainknit, \
        relax_pressure, \
        relax_tension


