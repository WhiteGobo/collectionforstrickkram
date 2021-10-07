#/bin/env python
"""
:todo: complete test_findsubgraph
"""

import tempfile
import unittest
import importlib.resources
import networkx as netx
from .load_stitchinfo import myasd as stinfo
from .fromknitmanual import BrokenManual

from extrasfornetworkx import create_pathforhashing
from extrasfornetworkx import follow_cached_path
from . import strickgraph_base as strickgraph

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

    def test_minimalstitchtypes( self ):
        """
        testing if minimal stitchtype collection is supported
        """
        stitchinfo = self.stitchinfo
        for stitchtype in ["knit", "yarnover", "bindoff", "k2tog"]:
            self.assertEqual( True, stitchtype in stitchinfo.types )

        strdat = stitchinfo.strickdata["plainknit"]
        self.assertEqual( strdat["stitch"], "knit" )
        self.assertEqual( strdat["startrow"], "yarnover" )
        self.assertEqual( strdat["endrow"], "bindoff" )

        for stitchtype, symbol, up, down, extrainfo in [\
                            ("knit", "k", 1,1,{}), \
                            ("yarnover", "yo",1,0,{}), \
                            ("bindoff", "bo", 0,1,{}), \
                            ("k2tog","k2tog",1,2,{}) ]:
            self.assertEqual( symbol, stitchinfo.symbol[ stitchtype ] )
            self.assertEqual( up, stitchinfo.upedges[ stitchtype ] )
            self.assertEqual( down, stitchinfo.downedges[ stitchtype ] )
            self.assertEqual( extrainfo, stitchinfo.extrainfo[stitchtype])


    def test_saveload_stitchdata( self ):
        from . import stitchdata
        from .load_stitchinfo import stitchdatacontainer
        import os.path
        stitchinfo = self.stitchinfo
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "tmpfile.xml" )
            stitchinfo.to_xmlfile( myfilepath )
            loadedstinfo = stitchdatacontainer.from_xmlfile( myfilepath )

        self.assertEqual( self.stitchinfo.symbol, loadedstinfo.symbol )
        self.assertEqual( self.stitchinfo.upedges, loadedstinfo.upedges )
        self.assertEqual( self.stitchinfo.downedges, loadedstinfo.downedges )
        self.assertEqual( self.stitchinfo.extrainfo, loadedstinfo.extrainfo )


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

    def test_extrastitchtypes( self ):
        """
        test if i can add succesfully new stitchtypes via xml-file
        :todo: write this method
        """
        myman = "6yo\n1k 1kmark 1k2tog 2k\n1k 1k2tog 2k\n4bo"
        from copy import deepcopy
        stitchinfo = deepcopy( self.stitchinfo )
        from . import stitchdata
        from importlib.resources import read_text
        xml_string = read_text( stitchdata, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )

        asd = strickgraph.strickgraph.from_manual( myman, stitchinfo )
        self.assertEqual( asd.get_alternative_stitchtypes(), {(1, 1): 'knit'} )
        newmanual = asd.copy_with_alternative_stitchtype()\
                        .to_manual( self.stitchinfo)
        brubru = "6yo\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo".splitlines()
        self.assertEqual( newmanual.splitlines(), brubru )

    def test_insertcolumn( self ):
        raise Exception( "insertcolumn not in use" )
        asd = strickgraph.strickgraph.from_gridgraph( self.insertgraph, \
                                                        self.insertfirstrow, \
                                                        self.stitchinfo )
        oldnodes = { *asd.nodes() }
        action.insert_column_onlyknits( asd, (4,1), 3)
        newnodes = { *asd.nodes() } - oldnodes
        self.assertEqual( 2, len(newnodes) )
        for x in newnodes:
            mustbeedges = {"next", "up"}
            for y in asd.edges( x ):
                mustbeedges = mustbeedges.difference( \
                        {netx.get_edge_attributes( asd, "edgetype" )[(*y,0)]} )
            self.assertEqual( 0, len(mustbeedges) )

            self.assertTrue( ((3,2), x) in asd.in_edges(x) \
                            or ((2,1),x) in asd.in_edges(x) )
            self.assertTrue( (x, (3,1)) in asd.edges(x) \
                            or (x, (2,2)) in asd.edges(x) )

    def test_insertcolumn( self ):
        raise Exception( "insertcolumn not in use" )
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        subasd = netx.subgraph( asd, [(0,0),(1,0),(0,2),(0,1),(2,0)] )
        path, nodes, qwe = create_pathforhashing( subasd, (0,0))

        self.assertEqual(set(path), set([(0, 'out', 'next', 1), (0, 'out', 'up', 2), (2, 'out', 'up', 3), (1, 'out', 'next', 4)]))
        self.assertEqual( nodes, [('yarnover','right'), ('yarnover','right'), ('knit','left'), ('knit','right'), ('yarnover','right')])


    def test_findsubgraph( self ):
        asd = strickgraph.strickgraph.from_gridgraph( self.mygraph, \
                                                            self.firstrow, \
                                                            self.stitchinfo )
        path = [(0, 'out', 'next', 1), (0, 'out', 'up', 2), (2, 'out', 'up', 3), (1, 'out', 'next', 4)]
        nodeattr = ['yarnover', 'yarnover', 'knit', 'knit', 'yarnover']
        foundthingis = follow_cached_path( asd, (0,0), path,\
                                                            nodeattr)
        #for x in foundthingis:
        #    print(x.edges())

    def test_strickgraphhash( self ):
        asd1 = strickgraph.strickgraph.from_gridgraph( self.minigraph, \
                                                            self.minifirstrow, \
                                                            self.stitchinfo )
        asd2 = strickgraph.strickgraph.from_gridgraph( self.minigraph, \
                                                            self.minifirstrow, \
                                                            self.stitchinfo )
        self.assertEqual( asd1.__hash__(), asd2.__hash__() )

    def test_refindsubgraph( self ):
        asd1 = strickgraph.strickgraph.from_gridgraph( self.biggraph, \
                                                            self.bigrow, \
                                                            self.stitchinfo )
        asd2 = strickgraph.strickgraph.from_gridgraph( self.biggraph, \
                                                            self.bigrow, \
                                                            self.stitchinfo )
        subgraph1 = asd1.subgraph([(1,1), (2,1), (3,1), (2,2), \
                                    (1,2), (1,3), (2,3)])
        path, nodes, qwe = create_pathforhashing( subgraph1, (1,1) )
        thingis, extrainfo = follow_cached_path( asd2, (1,1), path, nodes)
        foundpaths = list(thingis)
        self.assertEqual( len(foundpaths), 1 )
        if len(foundpaths) > 1:
            self.assertEqual( set(foundpaths[0]), set(subgraph1.nodes()) )
        thingis, extrainfo = follow_cached_path( asd2, (2,2), path, nodes)
        foundpaths = list(thingis)
        self.assertEqual( len(foundpaths), 0 )
        if len(foundpaths) > 0:
            self.assertFalse( set(foundpaths[0]) == set(subgraph1.nodes()) )

    def test_graphml( self ):
        raise Exception( "graphml not supported yet" )
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
        attr = netx.get_node_attributes( asd, "stitchtype" )
        self.assertEqual( attr[(1,0)], attr[(2,0)] )

        asd2 = strickgraph.strickgraph.from_manual( testmanual, self.stitchinfo, manual_type="thread" )
        attr = netx.get_node_attributes( asd2, "stitchtype" )
        self.assertEqual( attr[(1,0)], attr[(2,1)] )

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
