from datagraph_factory.datagraph import datatype, edgetype
from .. import strickgraph

class strickgraph_property_plainknit( datatype ):
    """Determines if the Strickgraph is plainknit or not"""
    def __init__( self, *args ):
        super().__init__()
        self.args = (*args,)

_sp_tmpvalid = lambda: ((strickgraph.strickgraph_container, \
                            strickgraph_property_plainknit),)
strickgraph_isplainknit:edgetype = edgetype( _sp_tmpvalid, "isplain", "" )
"""Strickgraph is plainknit Strickgraph"""

_sinp_tmpvalid = lambda: ((strickgraph.strickgraph_container, \
                            strickgraph_property_plainknit), )
strickgraph_isnotplainknit:edgetype = edgetype( _sinp_tmpvalid, "isnotplain", "" )
"""Strickgraph is not plainknit Strickgraph"""
