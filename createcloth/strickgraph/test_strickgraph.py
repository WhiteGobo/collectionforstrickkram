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

    def test_getrows( self ):
        """Test if method get_rows and _get_topologicalsort_of_stitches return
        right output
        """
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                            self.firstrow, self.stitchinfo, startside="right" )
        
        myedges = [(a,b) for a,b,c in asd.get_edges_with_labels() if c=="next"]
        testedges = [((0, 0), (0, 1)), ((0, 1), (0, 2)), ((0, 2), (0, 3)), \
                ((0, 3), (1, 3)), ((1, 3), (1, 2)), ((1, 2), (1, 1)), \
                ((1, 1), (1, 0)), ((1, 0), (2, 0)), ((2, 0), (2, 1)), \
                ((2, 1), (2, 2)), ((2, 2), (2, 3)), ((2, 3), (3, 3)), \
                ((3, 3), (3, 2)), ((3, 2), (3, 1)), ((3, 1), (3, 0))]
        self.assertEqual( myedges, testedges, msg="prerequisite failed. "
                        "edges are unexpected" )

        testtopsort = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2), \
                        (1, 1), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), \
                        (3, 3), (3, 2), (3, 1), (3, 0)]
        self.assertEqual( asd._get_topologicalsort_of_stitches(), \
                        testtopsort, msg="simple topological sort failed" )
        testrow_same = [[(0, 0), (0, 1), (0, 2), (0, 3)], \
                        [(1, 0), (1, 1), (1, 2), (1, 3)], \
                        [(2, 0), (2, 1), (2, 2), (2, 3)], \
                        [(3, 0), (3, 1), (3, 2), (3, 3)]]
        testrow_diff = [[(0, 3), (0, 2), (0, 1), (0, 0)], \
                        [(1, 3), (1, 2), (1, 1), (1, 0)], \
                        [(2, 3), (2, 2), (2, 1), (2, 0)], \
                        [(3, 3), (3, 2), (3, 1), (3, 0)]]
        self.assertEqual( asd.get_rows( lefttoright_side="left"), testrow_diff, msg="simple get_rows failed" )
        self.assertEqual( asd.get_rows( lefttoright_side="right"), testrow_same, msg="simple get_rows failed" )

        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                            self.firstrow, self.stitchinfo, startside="left" )
        myedges = [(a,b) for a,b,c in asd.get_edges_with_labels() if c=="next"]
        self.assertEqual( myedges, testedges, msg="prerequisite failed. "
                        "edges are unexpected" )
        self.assertEqual( asd.get_rows( lefttoright_side="left"), testrow_same, msg="simple get_rows failed" )
        self.assertEqual( asd.get_rows( lefttoright_side="right"), testrow_diff, msg="simple get_rows failed" )
    
        #create strickgraph 7yo;7k;3k 1bo 3k;3k skip 3k;3k skip 3k;
        nodeattr = {}
        edges = []
        rowlength, number_rows = 7, 5
        endofline=((0,6), (1,0), (2,6), (3,0), (3,4) )
        skip_stitches = [(3,3), (4,3)]
        bindoff_stitches = [ (2,3), (4,0),(4,1),(4,2),(4,4),(4,5),(4,6) ]
        for i in range(number_rows):
            for j in range( rowlength ):
                if (i,j) in skip_stitches:
                    continue
                if (i,j) in bindoff_stitches:
                    st_type = "bindoff"
                else:
                    st_type = {0:"yarnover", number_rows-1:"bindoff"}.get(i,"knit")
                
                side = { 1:"left", 0:"right" }[ i%2 ]
                nodeattr[ (i,j) ] = { "stitchtype":st_type, "side":side }

                if (i,j) not in endofline:
                    next_stitch = (i, j+1) if i%2==0 else (i, j-1)
                else:
                    next_stitch = (i+1, j)
                edges.append( ((i,j), next_stitch, "next"))
                edges.append( ((i,j), (i+1,j), "up") )
        edges = [(v1,v2,label) for v1, v2, label in edges \
                if all(v in nodeattr for v in (v1,v2))]
        asd = strickgraph.strickgraph( nodeattr, edges )

        test_rows = [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)], 
                [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)], 
                [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6)], 
                [(3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6)], 
                [(4, 0), (4, 1), (4, 2), (4, 4), (4, 5), (4, 6)]]
        self.assertEqual( asd.get_rows(), test_rows, msg="""
        Fails to test, if rows are correctly assigned if, a single row isnt 
        connected. It is instead cut in a certain height(3)
        """ )
        test_rows_hand = [ list(row) for row in test_rows ]
        for i, row in enumerate( test_rows_hand ):
            if i%2==1:
                row.reverse()
        self.assertEqual( asd.get_rows( presentation_type="thread"), \
                test_rows_hand, msg="happend, when get_rows with "\
                "presen.type thread" )
        for row in test_rows:
            row.reverse()
        self.assertEqual( asd.get_rows( lefttoright_side="left"), test_rows,\
                msg="wrong output, when get_rows with left as frontside" )

        testgraph = strickgraph.strickgraph.from_manual( "5yo\n5k\n5k\n5bo", self.stitchinfo, manual_type="machine", startside="left" )
        #print( testgraph.get_rows() )
        tmp = [['4', '3', '2', '1', '0'], ['5', '6', '7', '8', '9'],\
                ['14', '13', '12', '11', '10'], ['15', '16', '17', '18', '19']]

        self.assertEqual( testgraph.get_rows(), tmp, \
                        msg="small test with get rows startside left failed" )

        testgraph = strickgraph.strickgraph.from_manual( "5yo\n5k\n5k\n5bo", self.stitchinfo, manual_type="machine", startside="right" )
        #tmp = [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)], [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)], [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)]]
        tmp = [['0', '1', '2', '3', '4'], ['9', '8', '7', '6', '5'],\
                ['10', '11', '12', '13', '14'], ['19', '18', '17', '16', '15']]

        self.assertEqual( testgraph.get_rows(), tmp, msg="small test with get rows startside right failed" )

    #@unittest.skip( "get_border isnt complete" )
    def test_strickgraph_findborder( self ):
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        testrows = tuple([[(0, 0), (0, 1), (0, 2), (0, 3)], \
                        [(3, 0), (3, 1), (3, 2), (3, 3)], \
                        [(0, 0), (1, 0), (2, 0), (3, 0)], \
                        [(0, 3), (1, 3), (2, 3), (3, 3)]])
        self.assertEqual( tuple(asd.get_borders()), testrows )

        testmanual = "5yo\n5k\n5k\n3k 2bo\n3bo"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        borderlist = tuple( asd.get_borders() )
        rows = asd.get_rows()
        rightborder = [ rows[i][j] for i,j in [(0,-1), (1,-1), (2,-1), (3,-1), (3,-2), (3,-3), (4,-1)]]
        testborder = (rows[0], rows[-1], [ r[0] for r in rows ], rightborder)
        self.assertEqual( borderlist, testborder )

    def test_frommanual( self ):
        testmanual = "3yo\n2k yo 1k\n2k, 1k2tog\n3bo\n"
        testmanual_uni = "3yo\n2k yo k\n2k k2tog\n3bo\n"
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
        testmanual = "4yo\n2k yo 2k\n2k k2tog k\n4bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        manual = asd.to_manual( self.stitchinfo )
        manual = [ x.split() for x in manual.splitlines() ]
        testmanual = [x.split() for x \
                        in "4yo\n2k yo 2k\n2k k2tog k\n4bo\n".splitlines()]
        #this removes the spaces and tabs
        for i in range(len(testmanual)):
            self.assertEqual( "".join(manual[i]), "".join(testmanual[i]) )


        testmanual = "2yo\n 1k 1p\n k p\n 2bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo )
        manual = asd.to_manual( self.stitchinfo )
        manual = [ x.split() for x in manual.splitlines() ]
        testmanual = [x.split() for x \
                        in "2yo\n k p\n k p\n 2bo\n".splitlines()]
        #this removes the spaces and tabs
        for i in range(len(testmanual)):
            self.assertEqual( "".join(manual[i]), "".join(testmanual[i]) )

        asd = create_testgraph_with_chasm()
        manual = asd.to_manual( self.stitchinfo )
        qwe = strickgraph.strickgraph.from_manual( manual, self.stitchinfo )
        testmanual = qwe.to_manual( self.stitchinfo )
        self.assertEqual( manual, testmanual )

    def test_manualtype_machine_and_thread( self ):
        testmanual = "2yo\n k p\n k p\n 2bo\n"
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine" )
        attr = asd.get_nodeattr_stitchtype()
        a = asd.get_rows()[1][0]
        b = asd.get_rows()[2][0]
        self.assertEqual( attr[a], attr[b] )

        asd2 = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="thread" )
        attr = asd2.get_nodeattr_stitchtype()
        a = asd.get_rows()[1][0]
        b = asd.get_rows()[2][1]
        self.assertEqual( attr[a], attr[b] )

    @unittest.skip( "This method needs a rehaul" )
    def test_manual_withstartside( self ):
        testmanual = "2yo\n k p\n k p\n 2bo\n"
        #test if upedge differs from nextedge
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine", startside="right" )
        self.assertEqual( set(asd.neighbors((1,1))), {(1,0),(2,1)} )
        #test if upedge equals nextedge
        asd = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="machine", startside="left" )
        self.assertEqual( set(asd.neighbors((1,1))), {(2,1)} )



def create_testgraph_with_chasm():
    #create strickgraph 7yo;7k;3k 1bo 3k;3k skip 3k;3k skip 3k;
    nodeattr = {}
    edges = []
    rowlength, number_rows = 7, 5
    endofline=((0,6), (1,0), (2,6), (3,0), (3,4) )
    skip_stitches = [(3,3), (4,3)]
    bindoff_stitches = [ (2,3), (4,0),(4,1),(4,2),(4,4),(4,5),(4,6) ]
    for i in range(number_rows):
        for j in range( rowlength ):
            if (i,j) in skip_stitches:
                continue
            if (i,j) in bindoff_stitches:
                st_type = "bindoff"
            else:
                st_type = {0:"yarnover", number_rows-1:"bindoff"}.get(i,"knit")
            
            side = { 1:"left", 0:"right" }[ i%2 ]
            nodeattr[ (i,j) ] = { "stitchtype":st_type, "side":side }

            if (i,j) not in endofline:
                next_stitch = (i, j+1) if i%2==0 else (i, j-1)
            else:
                next_stitch = (i+1, j)
            edges.append( ((i,j), next_stitch, "next"))
            edges.append( ((i,j), (i+1,j), "up") )
    edges = [(v1,v2,label) for v1, v2, label in edges \
            if all(v in nodeattr for v in (v1,v2))]
    return strickgraph.strickgraph( nodeattr, edges )


if __name__=="__main__":
    unittest.main()
