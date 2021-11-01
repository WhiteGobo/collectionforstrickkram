#/bin/env python
"""

:todo: complete test_findsubgraph
:todo: complete test_insertcolumn double??
:todo: complete test_graphml
"""

import tempfile
import unittest
import importlib.resources
import networkx as netx
from ..stitchinfo import basic_stitchdata as stinfo
from .strickgraph_toknitmanual import BrokenManual

from . import strickgraph_base as strickgraph
import time

class TestStringMethods( unittest.TestCase ):
    def setUp( self ):
        self.mygraph = netx.grid_2d_graph( 4,4 )
        self.firstrow = [ x for x in self.mygraph.nodes() if x[0] == 0 ]
        self.insertgraph = netx.grid_2d_graph( 6,3 )
        self.insertfirstrow = [ x for x in self.insertgraph.nodes() if x[0]== 0]
        self.minigraph = netx.grid_2d_graph( 2,2 )
        self.minifirstrow = [ x for x in self.minigraph.nodes() if x[0] == 0 ]
        self.biggraph = netx.grid_2d_graph( 8,8 )
        self.bigrow = [ x for x in self.biggraph.nodes() if x[0] == 0 ]

        self.stitchinfo = stinfo

    def test_createfromgrid( self ):
        asd = strickgraph.strickgraph.from_gridgraph(self.mygraph, \
                                                        self.firstrow, \
                                                        self.stitchinfo )
        myedges_edgelabels = (((0, 0), (1, 0), 'up'), ((0, 0), (0, 1),'next'),\
                ((0, 1), (1, 1), 'up'), ((0, 1), (0, 2), 'next'), \
                ((0, 2), (1, 2), 'up'), ((0, 2), (0, 3), 'next'), \
                ((0, 3), (1, 3), 'up'), ((1, 3), (1, 2), 'next'), \
                ((1, 3), (2, 3), 'up'), ((1, 2), (1, 1), 'next'), \
                ((1, 2), (2, 2), 'up'), ((1, 1), (1, 0), 'next'), \
                ((1, 1), (2, 1), 'up'), ((1, 0), (2, 0), 'up'), \
                ((2, 0), (3, 0), 'up'), ((2, 0), (2, 1), 'next'), \
                ((2, 1), (3, 1), 'up'), ((2, 1), (2, 2), 'next'), \
                ((2, 2), (3, 2), 'up'), ((2, 2), (2, 3), 'next'), \
                ((2, 3), (3, 3), 'up'), ((3, 3), (3, 2), 'next'), \
                ((3, 2), (3, 1), 'next'), ((3, 1), (3, 0), 'next'), \
                ((0, 3),(1,3), 'next'), ((1, 0),(2,0), 'next'), \
                ((2, 3),(3,3), 'next'))
        mynodes_stitchtype = {(0, 0): 'yarnover', (0, 1): 'yarnover', \
                (0, 2): 'yarnover', (0, 3): 'yarnover', (1, 0): 'knit', \
                (1, 1): 'knit', (1, 2): 'knit', (1, 3): 'knit', (2, 0): 'knit',\
                (2, 1): 'knit', (2, 2): 'knit', (2, 3): 'knit', \
                (3, 0): 'bindoff', (3, 1): 'bindoff', \
                (3, 2): 'bindoff', (3, 3): 'bindoff'}
        asdedgetype = asd.get_edges_with_labels()
        from collections import Counter
        a, b = Counter(asdedgetype), Counter(myedges_edgelabels)
        import itertools as it
        self.assertEqual( a, b,\
                msg = "(edge, found, expected): %s"%([ (e,a[e], b[e]) \
                for e in set(it.chain(a,b)) if a[e]!=b[e] ]))
        #self.assertEqual( asdbreakline, myedges_breakline )
        asdstitchtype = asd.get_nodeattr_stitchtype()
        self.assertEqual( asdstitchtype, mynodes_stitchtype )
        #self.assertEqual( asdside, mynodes_side )

    def test_tomanual( self ):
        """
        test if outputmanual is equal to testmanual
        equal means that in every line everything is equal, when you dont look
        at the spaces and tabs
        """
        asd = strickgraph.strickgraph.from_gridgraph(self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        testmessage = [ x.split() for x in "4yo\n4k\n4k\n4bo\n".splitlines() ]
        manual = asd.to_manual( self.stitchinfo )
        manual = [ x.split() for x in manual.splitlines() ]
        #this removes the spaces and tabs
        for i in range(len(testmessage)):
            self.assertEqual( "".join(manual[i]), "".join(testmessage[i]),\
                                msg="Couldnt get the predicted manual: predicted: %s\nreal: %s" %(testmessage, manual))


    def test_compare_different_subgraphs( self ):
        graph1 = strickgraph.strickgraph.from_manual( "5yo\n5k\n5k\n5bo", self.stitchinfo)
        graph2 = strickgraph.strickgraph.from_manual( "6yo\n2k 1k2tog 2k\n5k\n5bo", self.stitchinfo )
        common_nodes1 = ((0,0), (0,1), (1,0), (1,1), (2,0), (2,1), (2,2), \
                        (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), \
                        (1,3), (1,4), (0,3), (0,4) )
        common_nodes2 = ((0,0), (0,1), (1,0), (1,1), (2,0), (2,1), (2,2), \
                        (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), \
                        (1,3), (1,4), (0,4), (0,5) )
        self.assertEqual( graph1.subgraph( common_nodes1 ), \
                            graph2.subgraph( common_nodes2) )


    @unittest.skip( "Just a collection of methods, that need testing" )
    def test_not_testmethods( self ):
        strickgraph.get_connected_nodes( nodelist )
        strickgraph.get_nodes_near_nodes()
        strickgraph.isvalid()

    def test_strickgraphhash( self ):
        asd1 = strickgraph.strickgraph.from_gridgraph( self.minigraph, \
                                                            self.minifirstrow, \
                                                            self.stitchinfo )
        asd2 = strickgraph.strickgraph.from_gridgraph( self.minigraph, \
                                                            self.minifirstrow, \
                                                            self.stitchinfo )
        self.assertEqual( asd1.__hash__(), asd2.__hash__() )


    @unittest.skip( "graphml not suported" )
    def test_graphml( self ):
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        asdxml = netx.generate_graphml( asd )
        mygraphml = ""
        for line in asdxml:
            mygraphml = mygraphml + line

        qwe = strickgraph.strickgraph(netx.parse_graphml( mygraphml ))
        self.assertEqual( asd, qwe )

    def test_strickgraph_findborder( self ):
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        testrows = tuple([[(0, 0), (0, 1), (0, 2), (0, 3)], \
                        [(3, 0), (3, 1), (3, 2), (3, 3)], \
                        [(0, 0), (1, 0), (2, 0), (3, 0)], \
                        [(0, 3), (1, 3), (2, 3), (3, 3)]])
        self.assertEqual( tuple(asd.get_borders()), testrows )

    def test_frommanual( self ):
        testmanual = "3yo\n2k yo 1k\n2k, 1k2tog\n3bo\n"
        testmanual_uni = "3yo\n2k 1yo 1k\n2k 1k2tog\n3bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        manual = asd.to_manual( self.stitchinfo )
        manual = tuple( "".join( x.split() ) for x in manual.splitlines() )
        testmanual_uni = tuple("".join( x.split() ) for x \
                        in testmanual_uni.splitlines())
        #this removes the spaces and tabs
        import networkx as netx
        self.assertEqual( manual, testmanual_uni )

        def testbrokenmanual():
            testmanual = "4yo\n2k 1yo 1k\n2k, 1k2tog, 1k\n4bo\n"
            strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        self.assertRaises( BrokenManual, testbrokenmanual )

        testmanual = [x.split() for x in \
                            "4yo\n2k yo 2k\n2k 1k2tog 1k\n4bo\n".splitlines()]
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        manual = asd.to_manual( self.stitchinfo )
        manual = [ x.split() for x in manual.splitlines() ]
        testmanual = [x.split() for x \
                        in "4yo\n2k 1yo 2k\n2k 1k2tog 1k\n4bo\n".splitlines()]
        #this removes the spaces and tabs
        for i in range(len(testmanual)):
            self.assertEqual( "".join(manual[i]), "".join(testmanual[i]) )


        testmanual = "2yo\n k p\n k p\n 2bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        manual = asd.to_manual( self.stitchinfo )
        manual = [ x.split() for x in manual.splitlines() ]
        testmanual = [x.split() for x \
                        in "2yo\n 1k 1p\n 1k 1p\n 2bo\n".splitlines()]
        #this removes the spaces and tabs
        for i in range(len(testmanual)):
            self.assertEqual( "".join(manual[i]), "".join(testmanual[i]) )

    def test_manualtype_machine_and_thread( self ):
        testmanual = "2yo\n k p\n k p\n 2bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine" )
        attr = asd.get_nodeattr_stitchtype()
        self.assertEqual( attr[(1,0)], attr[(2,0)] )

        asd2 = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="thread" )
        attr = asd2.get_nodeattr_stitchtype()
        self.assertEqual( attr[(1,0)], attr[(2,1)] )

    @unittest.skip( "This method needs a rehaul" )
    def test_manual_withstartside( self ):
        testmanual = "2yo\n k p\n k p\n 2bo\n"
        #test if upedge differs from nextedge
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine", startside="right" )
        self.assertEqual( set(asd.neighbors((1,1))), {(1,0),(2,1)} )
        #test if upedge equals nextedge
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine", startside="left" )
        self.assertEqual( set(asd.neighbors((1,1))), {(2,1)} )



if __name__=="__main__":
    unittest.main()
