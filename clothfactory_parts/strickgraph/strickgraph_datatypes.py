from datagraph_factory.datagraph import datatype, edgetype
from datagraph_factory.processes import DATATYPE, EDGETYPE
from createcloth.meshhandler.main import add_edgelength
import networkx as netx
from createcloth.strickgraph import strickgraph as strickgraph_class
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo

class strickgraph_container( datatype ):
    """
    :type strickgraph: createcloth.strickgraph.strickgraph
    """
    def __init__( self, strickgraph ):
        self.strickgraph = strickgraph

    @classmethod
    def load_from( cls, filepath, stinfo=globalstitchinfo ):
        with open( filepath, "r" ) as mymanual:
            mantext = mymanual.readlines()
        mystrickgraph = strickgraph_class.from_manual( mantext, stinfo )
                    #manual_type="thread", startside="right", reversed=False )
        return cls( mystrickgraph )

    def save_to( self, filepath, stinfo=globalstitchinfo ):
        manualtext = self.strickgraph.to_manual( stinfo )
        with open( filepath, "w" ) as mymanual:
            mymanual.write( manualtext )

class strickgraph_stitchdata( datatype ):
    def __init__( self, stitchlist, plain_stitch, \
                    plain_startrow, plain_endrow ):
        self.plain_stitch = plain_stitch
        self.plain_startrow = plain_startrow
        self.plain_endrow = plain_endrow
        self.stitchlist = stitchlist

class strickgraph_spatialdata( datatype ):
    def __init__( self, posgraph ):
        x_data = netx.get_node_attributes( posgraph, "x" )
        y_data = netx.get_node_attributes( posgraph, "y" )
        z_data = netx.get_node_attributes( posgraph, "z" )
        self._xdict = x_data
        self._ydict = y_data
        self._zdict = z_data

        default_length = 0.1
        add_edgelength( posgraph, default_length )
        nodetopairset = lambda x,y, d: frozenset((x,y))
        tmp = netx.get_edge_attributes( posgraph, "currentlength" )
        self.edgelengthdict = { nodetopairset(*key) : value \
                                for key, value in tmp.items() }
        tmp = netx.get_edge_attributes( posgraph, "length" )
        self.calmlengthdict = { nodetopairset(*key) : value \
                                for key, value in tmp.items() }



    def _get_xposition_to( self ):
        return self._xdict
    xposition = property( fget = _get_xposition_to )
    def _get_yposition_to( self ):
        return self._ydict
    yposition = property( fget = _get_yposition_to )
    def _get_zposition_to( self ):
        return self._zdict
    zposition = property( fget = _get_zposition_to )

    def _get_edgelength( self ):
        return self.edgelength
    edgelength = property( fget = _get_edgelength )


class strickgraph_property_relaxed( datatype ):
    def __init__( self, tensionrows=None, pressurerows=None):
        self.tensionrows = tensionrows
        self.pressurerows = pressurerows

tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_have_tension = edgetype( tmpvalid, \
                                            "some springs have tension", \
                            "source strickgraph has edges which are too long")
del( tmpvalid )

tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_have_pressure = edgetype( tmpvalid, \
                "some springs have pressure",\
                "source strickgraph has edges which are too short" )
del( tmpvalid )

tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_are_relaxed = edgetype( tmpvalid, \
                "springs are relaxed", \
                "source strickgraph has no edges which are "\
                +"too long or too short" )
del( tmpvalid )

tmpvalid = lambda: ((strickgraph_container, strickgraph_stitchdata),)
stitchdata_of_strick = edgetype( tmpvalid, \
                                "stitchdata of strick", "" )
del( tmpvalid )

tmpvalid = lambda: ((strickgraph_container,\
                    strickgraph_spatialdata),)
stitchposition = edgetype( tmpvalid, "stitch position", "" )
del( tmpvalid )