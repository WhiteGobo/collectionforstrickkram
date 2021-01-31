from .nodespannungtoedgespannung import main as toedgevalues
import unittest
import networkx as netx
from ..strickgraph import strickgraph_fromgrid as fromgrid
import pkg_resources
from ..meshhandler.main import relax_strickgraph_on_surface


class test_toedgetension( unittest.TestCase ):
    def setUp( self ):
        self.asd, self.filename, self.datagraph = None, None, None

        mygraph = netx.grid_2d_graph( 10,10 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        self.asd = fromgrid.create_strickgraph_from_gridgraph( mygraph,firstrow)
        self.filename = pkg_resources.resource_stream( __name__, \
                                            "../meshhandler/meshfortests.ply" )
        self.datagraph = relax_strickgraph_on_surface( self.asd, self.filename,\
                                                        numba_support=False )
        self.filename.close()
        self.asd.update( self.datagraph )

    def test_firsttest( self ):
        print( self.datagraph.edges(data=True))
        #print( netx.get_node_attributes( self.asd, "spannung" ))
        #toedgevalues( self.asd, "spannung" )
