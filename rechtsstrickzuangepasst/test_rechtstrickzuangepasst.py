import unittest
import networkx as netx
from ..strickgraph import strickgraph_fromgrid as fromgrid
import pkg_resources
from ..meshhandler.main import relax_strickgraph_on_surface
from . import brain
from ..meshhandler import get_surfacemap


class test_rechtsstrickzuangepasst( unittest.TestCase ):
    def setUp( self ):
        self.asd, self.filename, self.datagraph = None, None, None

        mygraph = netx.grid_2d_graph( 10,10 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        self.asd = fromgrid.create_strickgraph_from_gridgraph( mygraph,firstrow)
        filename = pkg_resources.resource_stream( __name__, \
                                           "../meshhandler/meshfortests.ply" )
        self.mysurfacemap = get_surfacemap( filename )
        filename.close()

        #datagraph = relax_strickgraph_on_surface( self.asd, mysurfacemap, \
        #                                            numba_support=False )
        #self.asd.update( self.datagraph )

    def test_firsttest( self ):
        brain.main( self.asd, self.mysurfacemap )
        pass
