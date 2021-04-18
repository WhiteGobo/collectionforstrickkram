from datagraph_factory.datagraph import datatype, edgetype
from .. import strickgraph

class strickgraph_property_plainknit( datatype ):
    def __init__( self, *args ):
        super().__init__()
        self.args = (*args,)

tmpvalid = lambda: ((strickgraph.strickgraph_container, \
                            strickgraph_property_plainknit),)
strickgraph_isplainknit = edgetype( tmpvalid, "isplain", "" )
del( tmpvalid )

tmpvalid = lambda: ((strickgraph.strickgraph_container, \
                            strickgraph_property_plainknit), )
strickgraph_isnotplainknit = edgetype( tmpvalid, "isnotplain", "" )
del( tmpvalid )
