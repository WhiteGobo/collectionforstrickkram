import unittest
from . import state
from . import examplestates as st
import logging
import itertools as it
logging.basicConfig( level=logging.WARNING )
#logging.basicConfig( level=logging.DEBUG )
logger = logging.getLogger( __name__ )

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_identifier( self ):
        for q in ( st.start, \
                    st.end, \
                    st.leftplane, \
                    st.rightplane, \
                    st.lefteaves, \
                    st.righteaves, \
                    st.enddecrease, \
                    st.plain, \
                    st.increase, \
                    st.decrease):
            simplediff = iter(q.get_downupdifference_examples()).__next__()
            bru = q.create_example_row( 10, 10 + simplediff )
            logger.debug( f"{q}, {bru}, {simplediff}" )
            self.assertIsInstance( bru, list )
            self.assertIsInstance( bru[0], str )
            self.assertTrue( q.identify( bru ) )
            self.assertIsInstance( q, state.rowstate )


    def test_createverbesserer( self ):
        from .create_example_strickgraphs import create_example_strickset
        from ..strickgraph import strickgraph
        from ..strickgraph.load_stitchinfo import myasd as glstinfo
        import numpy as np
        strickgraphsize = 6
        q = create_example_strickset( [], strickgraphsize, min_row_length=14 )
        q2 = create_example_strickset( [], strickgraphsize, min_row_length=16 )
        bru = dict()
        createdgraphs = dict()
        for linetypes, original_upedges in it.chain( q,q2 ):
            downedges = [ None, *original_upedges ]
            upedges = [ *original_upedges, None ]
            allinfo = zip( linetypes, downedges, upedges )
            m = [ s.create_example_row( down, up ) \
                                        for s, down, up in allinfo ]
            linelength = tuple( len(line) for line in m )
            manual = "\n".join( " ".join(line) for line in m )
            #check if anything gone wrong, while creating strickmanuals
            mystrick = strickgraph.from_manual( manual, glstinfo, \
                                                    manual_type="machine" )
            bru[manual] = linelength
            createdgraphs[manual] = mystrick

        #find difference is 2
        edges_manuals = set()
        for first, second in it.product( bru.keys(), repeat=2 ):
            difference_array = np.subtract( bru[ first ], bru[ second ] )
            tmp = np.equal( difference_array, 0 )
            axis_different = sum( 0 if single else 1 for single in tmp )
            del(tmp)
            if axis_different == 1:
                if sum(difference_array) == 2:
                    edges_manuals.add( ( first, second ) )
                #This would create doubles
                #elif difference == -2:
        


            



if __name__ == "__main__":
    unittest.main()
