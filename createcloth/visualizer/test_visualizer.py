import unittest
import os

TEST_VISUALIZE = os.getenv( "INTERACTIVE" )

class TestVisualizer( unittest.TestCase ):
    @unittest.skipIf( TEST_VISUALIZE is None, "only test if human interaction" )
    def test_visualizer( self ):
        print( "test" )
