import unittest
from . import state
from . import examplestates as st
import logging
import itertools as it
logger = logging.getLogger( __name__ )
import time
from ..verbesserer.verbesserer_class import FindError
from ..verbesserer.class_side_alterator import sidealterator, multi_sidealterator
from ..stitchinfo import basic_stitchdata as glstinfo
from typing import Iterable
import numpy as np

from . import method_isplain as mip

import os
import signal
import psutil
import multiprocessing as mp

from . import create_example_strickgraphs as ces


def asdf( less_graph, great_graph, startnode, changedline_id, myqueue ):
    try:
        a = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )
        myqueue.put( a )
    except Exception as err:
        pass

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_identifier( self ):
        for q, side in ( (st.start,"right"), \
                    (st.end,"right"), \
                    (st.leftplane,"left"), \
                    (st.rightplane,"right"), \
                    (st.lefteaves,"left"), \
                    (st.righteaves,"right"), \
                    (st.enddecrease,"right"), \
                    (st.plain,"right"), \
                    (st.increase,"right"), \
                    (st.decrease,"right")):
            simplediff = iter(q.get_updowndifference_examples()).__next__()
            down = 10
            up = down + simplediff
            #print( str(q), f"down{down}, up{up}", side)
            bru = q.create_example_row( down, up, side=side )
            logger.debug( f"{q}, {bru}, {simplediff}" )
            self.assertIsInstance( bru, list )
            self.assertIsInstance( bru[0], str )
            self.assertTrue( q.identify( bru ) )
            self.assertIsInstance( q, state.rowstate )

    def test_if_strickgraph_isplainknit( self ):
        #mip.isplain_strickgraph( strickgraph )
        pass

    def test_create_examplestrickset( self ):
        """Test for creation of example sets of a certain strickmuster.
        Default structure of sets is Iterable[ list[linetypes], 
        list[upedges(int)], list[stitchnumber(int)]]

        """
        q = ces.create_example_strickset( [], 4, \
                                        min_row_length=12 )
        from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
        testq = [(start, leftplane, rightplane, end), (start, leftplane, rightplane, end), (start, leftplane, rightplane, end), (start, lefteaves, righteaves, end), (start, lefteaves, righteaves, end), (start, lefteaves, righteaves, end), (start, plain, plain, end), (start, plain, plain, enddecrease), (start, plain, increase, end), (start, plain, increase, enddecrease), (start, plain, decrease, end), (start, plain, decrease, enddecrease), (start, increase, plain, end), (start, increase, plain, enddecrease), (start, increase, increase, end), (start, increase, increase, enddecrease), (start, increase, decrease, end), (start, increase, decrease, enddecrease), (start, decrease, plain, end), (start, decrease, plain, enddecrease), (start, decrease, increase, end), (start, decrease, increase, enddecrease), (start, decrease, decrease, end), (start, decrease, decrease, enddecrease)]
        self.assertEqual( testq, list( a[0] for a in q ) )

        q = ces.create_example_strickset( [], 4, \
                                        min_row_length=12 )
        detailtest = [ ((start, plain, increase, end), (12, 12, 14), [12, 12, 14, 14]) ]
        for linetypes, upedges, stitchnumber in detailtest:
            testrow = [ a for a in q if a[0] == linetypes ][0]
            self.assertEqual( testrow[1], upedges )
            self.assertEqual( testrow[2], stitchnumber )

    def test_order_neighbouring( self ):
        from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
        #testq = [((start, leftplane, rightplane, end), (18, 15, 12), [18, 18, 15, 12]), ((start, leftplane, rightplane, end), (20, 16, 12), [20, 20, 16, 12]), ((start, leftplane, rightplane, end), (22, 17, 12), [22, 22, 17, 12]), ((start, lefteaves, righteaves, end), (12, 15, 18), [12, 15, 18, 18]), ((start, lefteaves, righteaves, end), (12, 16, 20), [12, 16, 20, 20]), ((start, lefteaves, righteaves, end), (12, 17, 22), [12, 17, 22, 22]), ((start, plain, plain, end), (12, 12, 12), [12, 12, 12, 12]), ((start, plain, plain, enddecrease), (12, 12, 12), [12, 12, 12, 10]), ((start, plain, increase, end), (12, 12, 14), [12, 12, 14, 14]), ((start, plain, increase, enddecrease), (12, 12, 14), [12, 12, 14, 12]), ((start, plain, decrease, end), (14, 14, 12), [14, 14, 12, 12]), ((start, plain, decrease, enddecrease), (14, 14, 12), [14, 14, 12, 10]), ((start, increase, plain, end), (12, 14, 14), [12, 14, 14, 14]), ((start, increase, plain, enddecrease), (12, 14, 14), [12, 14, 14, 12]), ((start, increase, increase, end), (12, 14, 16), [12, 14, 16, 16]), ((start, increase, increase, enddecrease), (12, 14, 16), [12, 14, 16, 14]), ((start, increase, decrease, end), (12, 14, 12), [12, 14, 12, 12]), ((start, increase, decrease, enddecrease), (12, 14, 12), [12, 14, 12, 10]), ((start, decrease, plain, end), (14, 12, 12), [14, 12, 12, 12]), ((start, decrease, plain, enddecrease), (14, 12, 12), [14, 12, 12, 10]), ((start, decrease, increase, end), (14, 12, 14), [14, 12, 14, 14]), ((start, decrease, increase, enddecrease), (14, 12, 14), [14, 12, 14, 12]), ((start, decrease, decrease, end), (16, 14, 12), [16, 14, 12, 12]), ((start, decrease, decrease, enddecrease), (16, 14, 12), [16, 14, 12, 10])]
        testq = [((start, plain, increase, end), (12, 12, 14), [12, 12, 14, 14]), 
                ((start, increase, increase, end), (12, 14, 16), [12, 14, 16, 16]),\
                        ]

        brubru = ces.create_stitchnumber_to_examplestrick( testq )
        for linetypes, upedges, stitchnumber in testq:
            myid = ces.class_idarray( stitchnumber )
            self.assertTrue( myid, tuple( q-stitchnumber[0] for q in stitchnumber ) )
            self.assertTrue( (linetypes,upedges) in brubru[ myid ] )
            myid_tuple = tuple( q-stitchnumber[0] for q in stitchnumber )
            self.assertTrue( (linetypes,upedges) in brubru[ myid_tuple ] )
        asdf = ces.order_neighbouring( brubru )

        test_pairs = [ ((start, plain, increase, end), (start, increase, increase, end), (12, 12, 14), (10, 12, 14), 0), ]
        """test_pairs is dependent on testq"""

        for pair in test_pairs:
            self.assertTrue( pair in asdf)
        for linetypes_in, linetypes_out, upedges_in, upedges_out, deviant_index\
                                                                    in asdf:
            #print(  linetypes_in, linetypes_out, upedges_in, upedges_out, deviant_index )
            self.assertTrue( 0 <= sum( upedges_in )- sum( upedges_out ) <= 3 )

    def test_createverbesserer( self ):
        from ..strickgraph import strickgraph
        from ..stitchinfo import basic_stitchdata as glstinfo
        def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
            sides = ("right", "left") if startside=="right" else ("left", "right")
            downedges = [ None, *upedges ]
            upedges = [ *upedges, None ]
            iline = range(len(downedges))
            allinfo = zip( linetypes, downedges, upedges, iline )
            try:
                graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                        for s, down, up, i in allinfo ]
            except Exception as err:
                raise Exception( [str(a) for a in linetypes], downedges, upedges, iline ) from err
                raise err
            graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
            return graph


        from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
        test_pairs = [ ((start, plain, increase, end), (start, increase, increase, end), (12, 12, 14), (10, 12, 14), 0), ]
        """See for test of test_pairs `test_order_neighbouring`"""

        from ..verbesserer.class_side_alterator import multi_sidealterator
        decreaser = multi_sidealterator.generate_from_linetypelist( test_pairs )

        for linetypes_in, linetypes_out, upedges_in, upedges_out, deviant_line \
                                                                in test_pairs:
            for side in ( "right", "left" ):
                brubrugraph = create_graph_from_linetypes( linetypes_in, \
                                                upedges_in, startside=side )
                outgraph = decreaser.replace_graph( brubrugraph, deviant_line )
                testgraph = create_graph_from_linetypes( linetypes_out, \
                                                upedges_out, startside=side )
                self.assertEqual( outgraph, testgraph )


from ..strickgraph import strickgraph
def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    sides = ("right", "left") if startside=="right" else ("left", "right")
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    iline = range(len(downedges))
    allinfo = zip( linetypes, downedges, upedges, iline )
    try:
        graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                for s, down, up, i in allinfo ]
    except Exception as err:
        raise Exception( [str(a) for a in linetypes], downedges, upedges, iline ) from err
        raise err
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph


if __name__ == "__main__":
    logging.basicConfig( level=logging.WARNING )
    #logging.basicConfig( level=logging.DEBUG )
    unittest.main()
