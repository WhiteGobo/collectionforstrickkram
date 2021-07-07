import unittest
from . import state
import logging
logging.basicConfig( level=logging.WARNING )
logger = logging.getLogger( __name__ )

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_identifier( self ):
        for q in ( state.start, \
                    state.end, \
                    state.leftplane, \
                    state.rightplane, \
                    state.lefteaves, \
                    state.righteaves, \
                    state.enddecrease, \
                    state.plain, \
                    state.increase, \
                    state.decrease):
            bru = q.create_example_row( 10 )
            logger.debug( bru )
            self.assertIsInstance( bru, list )
            self.assertIsInstance( bru[0], str )
            self.assertTrue( q.identify( bru ) )
            self.assertIsInstance( q, state.rowstate )


    def test_createverbesserer( self ):
        from .create_example_strickgraphs import create_example_strickset
        strickgraphsize = 5
        create_example_strickset( [], strickgraphsize )

if __name__ == "__main__":
    unittest.main()
