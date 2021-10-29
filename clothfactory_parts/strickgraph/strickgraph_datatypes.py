from datagraph_factory import datatype, edgetype
from datagraph_factory.processes import DATATYPE, EDGETYPE
#from createcloth.meshhandler.main import add_edgelength
import networkx as netx
from createcloth.strickgraph import strickgraph as strickgraph_class
from createcloth.stitchinfo import basic_stitchdata as globalstitchinfo
from createcloth.stitchinfo import stitchdatacontainer
import numpy as np

from typing import Dict, Tuple, Hashable, Iterable

class strickgraph_container( datatype ):
    """

    :type strickgraph: createcloth.strickgraph.strickgraph
    :ivar strickgraph: Strickgraphthingy
    :type strickgraph: :class:`strickgraph_class`
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

    def save_as( self, filepath, stinfo=globalstitchinfo ):
        manualtext = self.strickgraph.to_manual( stinfo )
        with open( filepath, "w" ) as mymanual:
            mymanual.write( manualtext )

class strickgraph_stitchdata( datatype ):
    """

    :ivar plain_stitch: asdf
    :ivar plain_startrow: qwer
    :ivar plain_endrow: asqw
    :ivar stitchlist: erdf
    :ivar stitchinfo: fdwq
    """
    def __init__( self, stitchinfo, plain_stitch, \
                    plain_startrow, plain_endrow ):
        self.plain_stitch = plain_stitch
        self.plain_startrow = plain_startrow
        self.plain_endrow = plain_endrow
        self.stitchlist = stitchinfo
        self.stitchinfo = stitchinfo

    @classmethod
    def load_from( cls, filepath ):
        mystitchinfo = stitchdatacontainer.from_xmlfile( filepath )
        plain_stitch = globalstitchinfo.strickstitch["plainknit"]
        plain_startrow = globalstitchinfo.strickstart["plainknit"]
        plain_endrow = globalstitchinfo.strickend["plainknit"]
        return cls( mystitchinfo, plain_stitch, plain_startrow, plain_endrow)
        with open( filepath, "r" ) as file:
            plain_stitch = file.readline()
            plain_startrow = file.readline()
            plain_endrow = file.readline()
        return cls( globalstitchinfo, plain_stitch, plain_startrow,plain_endrow)


    def save_as( self, filepath ):
        self.stitchinfo.to_xmlfile( filepath )
        #with open( filepath, "w" ) as file:
        #    txt = "\n".join([self.plain_stitch, self.plain_startrow, \
        #                            self.plain_endrow])
        #    file.write( txt )

class strickgraph_spatialdata( datatype ):
    """

    :ivar _xdict: (Dict) a
    :ivar _ydict: (Dict) b
    :ivar _zdict: (Dict) c
    :ivar edges: (List[ Tuple( Hashable, Hashable)]) all edges, no multi, \
            non directional
    :ivar edgelengthdict: (Dict) edge to real length
    :ivar calmlengthdict: (Dict) edge to length, without spring force
    """
    def __init__( self, x_pos: Dict[Hashable,float], y_pos, z_pos, \
                                edges: Iterable[ Tuple[ Hashable, Hashable ]],\
                                edge_restinglength: Iterable[ float ] =None):
        self.edges = tuple( edges )
        self._xdict = x_pos
        self._ydict = y_pos
        self._zdict = z_pos

        vec = lambda v: ( x_pos[v], y_pos[v], z_pos[v] )
        tolength = lambda e: np.linalg.norm( np.subtract(vec(e[0]), vec(e[1])) )
        self.edgelengthdict = { e: tolength(e) for e in self.edges }
        if edge_restinglength is not None:
            self.calmlengthdict = { e: l \
                    for e, l in zip(self.edges, edge_restinglength) }
        else:
            self.calmlengthdict = { e: 0.0 for e in self.edges }

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

    def save_as( self, filepath ):
        import pickle
        savedata = [ self.edges, self._xdict, self._ydict, \
                    self._zdict, self.calmlengthdict ]
        with open( filepath, "wb" ) as savefile:
            pickle.dump( savedata, savefile )

    @classmethod
    def load_from( cls, filepath ):
        import pickle
        with open( filepath, "rb" ) as loadfile:
            savedata = pickle.load( loadfile )
        edges, x, y, z, calmlength_dict = savedata
        edges = tuple( edges )
        calmlength = [ calmlength_dict[e] for e in edges ]
        return cls( x, y, z, edges, calmlength )


class strickgraph_property_relaxed( datatype ):
    """

    :ivar tensionrows: asdf
    :ivar pressurerows: qwer
    """
    def __init__( self, tensionrows=None, pressurerows=None):
        self.tensionrows = tensionrows
        self.pressurerows = pressurerows

_soshtens_tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_have_tension: edgetype = edgetype( _soshtens_tmpvalid, \
                                            "some springs have tension", \
                                            __name__ )
"""Property that strickgraph has parts under tension
source strickgraph has edges which are too long

"""

_soshpress_tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_have_pressure: edgetype = edgetype( _soshpress_tmpvalid, \
                "some springs have pressure", __name__ )
"""some springs have pressure
source strickgraph has edges which are too short
"""

_sosrel_tmpvalid = lambda: ((strickgraph_container, strickgraph_property_relaxed),)
springs_of_strickgraph_are_relaxed: edgetype = edgetype( _sosrel_tmpvalid, \
                "springs are relaxed", __name__ )
"""All springs are relaxed
source strickgraph has no edges which are too long or too short

"""

_stdata_tmpvalid = lambda: ((strickgraph_container, strickgraph_stitchdata),)
stitchdata_of_strick: edgetype = edgetype( _stdata_tmpvalid, \
                                "stitchdata of strick", __name__ )
"""Stitchdata to Strickgraph"""

_stpos_tmpvalid = lambda: ((strickgraph_container,\
                    strickgraph_spatialdata),)
stitchposition: edgetype = edgetype( _stpos_tmpvalid, "stitch position", __name__ )
"""Stitchposition to Strickgraph"""
