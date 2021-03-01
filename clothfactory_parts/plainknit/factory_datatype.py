from ..strickgraph_datatypes import strickgraph_container
from datagraph_factory.datagraph import datatype, edgetype

class strickgraph_property_plainknit( datatype ):
    pass

strickgraph_isplainknit = edgetype( strickgraph_container, \
                            strickgraph_property_plainknit, "isplain", "" )
strickgraph_isnotplainknit = edgetype( strickgraph_container, \
                            strickgraph_property_plainknit, "isnotplain", "" )

