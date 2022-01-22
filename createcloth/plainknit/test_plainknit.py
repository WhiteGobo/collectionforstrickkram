import unittest
#from . import state
#from . import examplestates as st
import logging
#import itertools as it
logger = logging.getLogger( __name__ )
#import time
from ..verbesserer import multi_sidealterator
from ..stitchinfo import basic_stitchdata as glstinfo

from . import create_example_strickgraphs as ces
from .. import plainknit
from .rowstates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_idclass( self ):
        linetype_list = (start, plain, increase, end)
        upedges = (12, 12, 14)
        startside = "right"

        genstrick = plainknit.create_graph_from_linetypes(
                                linetype_list, upedges, startside=startside )
        self.assertEqual( genstrick.to_manual( glstinfo ), \
                        "12yo\n12k\n2k 1yo 8k 1yo 2k\n14bo" )
        attributes = plainknit.plainknit_strickgraph_identifier( genstrick )
        self.assertEqual( attributes[ "startside" ], startside )
        self.assertEqual( tuple(attributes[ "upedges" ]), upedges )
        self.assertEqual( tuple(attributes[ "linetypes" ]), linetype_list )


    def test_identifier( self ):
        """Test inner methods. This method is helper method to create
        a full strickgraph from plainknit attributes
        """
        pl_rowstates = plainknit.rowstates
        for q, side in ( ( pl_rowstates.start, "right" ), \
                    ( pl_rowstates.end, "right"), \
                    ( pl_rowstates.leftplane, "left"), \
                    ( pl_rowstates.rightplane, "right"), \
                    ( pl_rowstates.lefteaves, "left"), \
                    ( pl_rowstates.righteaves, "right"), \
                    ( pl_rowstates.enddecrease, "right"), \
                    ( pl_rowstates.plain, "right"), \
                    ( pl_rowstates.increase, "right"), \
                    ( pl_rowstates.decrease, "right")):
            simplediff = iter(q.get_updowndifference_examples()).__next__()
            down = 10
            up = down + simplediff
            #print( str(q), f"down{down}, up{up}", side)
            bru = q.create_example_row( down, up, side=side )
            logger.debug( f"{q}, {bru}, {simplediff}" )
            self.assertIsInstance( bru, list, \
                            msg="unexpected returntype of create_example_row" )
            self.assertIsInstance( bru[0], str, \
                            msg="unexpected returntype of create_example_row" )
            self.assertTrue( q.identify( bru ), \
                            msg="Couldnt identify example linetype correctly" )

    def test_if_strickgraph_isplainknit( self ):
        #mip.isplain_strickgraph( strickgraph )
        pass

    def test_create_examplestrickset( self ):
        """Test for creation of example sets of a certain strickmuster.
        Default structure of sets is Iterable[ list[linetypes], 
        list[upedges(int)], list[stitchnumber(int)]]

        """
        q = plainknit.create_example_strickset( 4, \
                                        min_row_length=12 )
        from .rowstates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
        testq = [(start, leftplane, rightplane, end), \
                (start, leftplane, rightplane, end), \
                (start, leftplane, rightplane, end), \
                (start, lefteaves, righteaves, end), \
                (start, lefteaves, righteaves, end), \
                (start, lefteaves, righteaves, end), \
                (start, plain, plain, end), \
                (start, plain, plain, enddecrease), \
                (start, plain, increase, end), \
                (start, plain, increase, enddecrease), \
                (start, plain, decrease, end), \
                (start, plain, decrease, enddecrease), \
                (start, increase, plain, end), \
                (start, increase, plain, enddecrease), \
                (start, increase, increase, end), \
                (start, increase, increase, enddecrease), \
                (start, increase, decrease, end), \
                (start, increase, decrease, enddecrease), \
                (start, decrease, plain, end), \
                (start, decrease, plain, enddecrease), \
                (start, decrease, increase, end), \
                (start, decrease, increase, enddecrease), \
                (start, decrease, decrease, end), \
                (start, decrease, decrease, enddecrease)]
        self.assertEqual( testq, list( a[0] for a in q ) )

        q = plainknit.create_example_strickset( 4, \
                                        min_row_length=12 )
        detailtest = [ ((start, plain, increase, end), (12, 12, 14), [12, 12, 14, 14]) ]
        for linetypes, upedges, stitchnumber in detailtest:
            testrow = [ a for a in q if a[0] == linetypes ][0]
            self.assertEqual( testrow[1], upedges )
            self.assertEqual( testrow[2], stitchnumber )

    def test_order_neighbouring( self ):
        """Tests inner method for ordering different possible plainknit
        strickgraphs with the nearest linelength attribute. This method 
        is used for finding alterations for increasing or decreasing linelength

        :todo: rework because ordering neighbouring has changed
        """
        rs = plainknit.rowstates
        testq = [((rs.start, rs.plain, rs.increase, rs.end), (12, 12, 14), [12, 12, 14, 14]), 
                ((rs.start, rs.increase, rs.increase, rs.end), (12, 14, 16), [12, 14, 16, 16]),\
                        ]

        brubru = ces.create_stitchnumber_to_examplestrick( testq )
        for linetypes, upedges, stitchnumber in testq:
            myid = ces.class_idarray( stitchnumber )
            tmp_linelength = tuple( q-stitchnumber[0] for q in stitchnumber )
            self.assertTrue( myid, tmp_linelength )
            self.assertTrue( (linetypes,upedges) in brubru[ myid ] )
            myid_tuple = tuple( q-stitchnumber[0] for q in stitchnumber )
            self.assertTrue( (linetypes,upedges) in brubru[ myid_tuple ] )
        asdf = ces.order_neighbouring( brubru, "right" )

        test_pairs = [ ((start, plain, increase, end), (start, increase, increase, end), (12, 12, 14), (10, 12, 14), 0, "right"), ]
        """test_pairs is dependent on testq"""

        for pair in asdf:
            self.assertTrue( tuple(pair) in test_pairs )
        for linetypes_in, linetypes_out, upedges_in, upedges_out, \
                                            deviant_index, startside in asdf:
            self.assertTrue( 0 <= sum( upedges_in )- sum( upedges_out ) <= 3 )

    def test_createverbesserer( self ):
        rs = plainknit.rowstates
        linetypes_in = (rs.start, rs.plain, rs.increase, rs.end)
        linetypes_out = (rs.start, rs.increase, rs.increase, rs.end)
        test_pairs = [ multi_sidealterator.linetypepair(linetypes_in, linetypes_out, (12, 12, 14), (10, 12, 14), 0, "right"), \
                multi_sidealterator.linetypepair(linetypes_in, linetypes_out, (12, 12, 14), (10, 12, 14), 0, "left"), ]

        decreaser = multi_sidealterator.generate_from_linetypelist( test_pairs )

        for linetypes_in, linetypes_out, upedges_in, upedges_out, \
                                    deviant_line, startside in test_pairs:
            brubrugraph = plainknit.create_graph_from_linetypes( \
                                            linetypes_in, \
                                            upedges_in, startside=startside )
            outgraph = decreaser.replace_graph( brubrugraph, deviant_line )
            testgraph = plainknit.create_graph_from_linetypes( \
                                            linetypes_out, \
                                            upedges_out, startside=startside )
            self.assertEqual( outgraph, testgraph )


if __name__ == "__main__":
    logging.basicConfig( level=logging.WARNING )
    #logging.basicConfig( level=logging.DEBUG )
    unittest.main()
