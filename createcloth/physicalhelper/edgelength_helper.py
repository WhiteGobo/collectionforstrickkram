import networkx as netx

class threadinfo():
    """
    dimensions:
    thickness in [millimetre]
    tensure is custom property for numerik thingis
    """
    def __init__( self, thickness, tensure ):
        self.thickness = thickness
        self.tensure = tensure

    def _get_knitradius(self):
        return self.thickness*2
    plainknit_startstitchwidth = property( fget=_get_knitradius )
    plainknit_endstitchwidth = property( fget=_get_knitradius )
    plainknit_normalstitchwidth = property( fget=_get_knitradius )
    plainknit_stitchheight = property( fget=_get_knitradius )

standardthreadinfo = threadinfo( 0.005, 1.0 )

def relaxedgelength_to_strickgraph( mystrickgraph, \
                                    mythreadinfo=standardthreadinfo ):
    length_graph = netx.Graph()
    length_graph.add_nodes_from( mystrickgraph.nodes() )
    length_graph.add_edges_from( mystrickgraph.edges() )
    length_graph.remove_node("start")
    length_graph.remove_node("end")
    stitchtypes = netx.get_node_attributes( mystrickgraph, "stitchtype" )
    edgetypes = netx.get_edge_attributes( mystrickgraph, "edgetype" )
    lengthdict = {}
    for a, b in length_graph.edges():
        atype = stitchtypes[ a ]
        btype = stitchtypes[ b ]
        try:
            etype = edgetypes[ (a, b, 0) ]
        except KeyError as err:
            etype = edgetypes[ (b, a, 0) ]
        lengthdict.update( { (a,b): \
                        singleedge_length(atype, btype, etype, mythreadinfo) } )
    netx.set_edge_attributes( length_graph, lengthdict, "calmlength" )
    return length_graph


def singleedge_length( sourcetype, targettype, edgetype, mythreadinfo ):
    return 2 * mythreadinfo.thickness
