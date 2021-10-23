import unittest
import os

from . import plotter as graph_3d
from . import graph_2d

from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo

TEST_VISUALIZE = os.getenv( "INTERACTIVE" )

class TestVisualizer( unittest.TestCase ):
    """Methods to test visualizer. By nature these tests can only be done 
    with human interaction. So they will only work if youv set the 
    environment variable 'INTERACTIVE'( something like 
    'env INTERACTIVE= pythontest' )
    """
    @unittest.skipIf( TEST_VISUALIZE is None, "only test if human interaction" )
    def test_3dvisualizer( self ):
        """this method should print nearly a cube.
        Only used when environment 'INTERACTIVE' is set
        """
        print( "-"*65 )
        print( self )
        #nearly cubenodes
        nodes = ( (0,0,1), (0,1,1), (0,0,0), (1,0,1), (1,1,1), (1,1,0), (1,0,0) )
        x = { n: n[0] for n in nodes }
        y = { n: n[1] for n in nodes }
        z = { n: n[2] for n in nodes }
        edges = [ (nodes[a], nodes[b]) for a, b in \
                [(1,3),(0,1),(0,2),(0,3),(3,4),(1,4),(4,5),(2,6),(3,6),(5,6)]]
        
        print( "This method should show a 3d graph of a cube. Please close the"\
                " opened window and answer if the 3d nearly cube was seen")
        graph_3d.myvis3d( x,y,z, edges )
        confirm = input( "have you seen the 3d nearly cube?(y/N)" )
        confirm += "N"
        self.assertEqual( confirm[0], 'y', msg="User said, he couldnt see 3d-Cube" )

    @unittest.skipIf( TEST_VISUALIZE is None, "only test if human interaction" )
    def test_2dvisualizer( self ):
        """This method should print a small strickgraph.
        Only used when environment 'INTERACTIVE' is set
        """
        print( "-"*65 )
        print( self )
        man = "4yo\n4k\n4bo"
        print( "This test should draw a small graph equal to following knitting "
                "piece: '%s'.\nCan you identify the piece?" %(man) )
        asd = strickgraph.from_manual( man, glstinfo )
        graph_2d.easygraph( asd )
        confirm = input( "Could you see the graph corresponding "\
                "to the knitted piece(y/N)?" )
        confirm += "N"
        self.assertEqual( confirm[0], 'y', \
                msg="User said, he couldnt see the knitted piece" )
