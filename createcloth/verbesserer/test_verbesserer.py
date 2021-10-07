import unittest
#import pkg_resources
import importlib
from ..strickgraph import strickgraph

import networkx as netx
from ..strickgraph.load_stitchinfo import myasd as stitchinfo
import extrasfornetworkx
from extrasfornetworkx import multiverbesserer
from .multiverbesserer import strick_multiverbesserer
from . import resourcestest as test_src
from .verbesserer_class import strickalterator, FindError

import logging
logger = logging.getLogger( __name__ )
logging.basicConfig( level = logging.WARNING )
#logging.basicConfig( level = logging.DEBUG )

class test_manualtoverbesserung( unittest.TestCase ):
    def setUp( self ):
        pass

    def test_xmlverbesserung( self ):
        from importlib.resources import read_text

        xml_string = read_text( test_src, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )
        old_manual = read_text( test_src, \
                            "simplegrid_markstitch.knitmanual").splitlines()
        new_manual = read_text( test_src, \
                            "better_markstitch.knitmanual").splitlines()

        asd = strickalterator.from_manuals( old_manual, new_manual, stitchinfo)

        qwe = asd.to_xml()
        remake = strickalterator.from_xmlstr( qwe )

        self.assertEqual( asd, remake )


    def test_tryingsimpleinsert( self ):
        print( "hier ist noch eine todo sache" )
        from importlib.resources import read_text
        xml_string = read_text( test_src, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )
        old_manual = read_text( test_src, \
                            "simplegrid_markstitch.knitmanual").splitlines()
        new_manual = read_text( test_src, \
                            "better_markstitch.knitmanual").splitlines()

        asd = strickalterator.from_manuals( old_manual, new_manual, \
                                stitchinfo, startside="right" )

        
        mygraph = netx.grid_2d_graph( 6, 5 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        mystrick = strickgraph.from_gridgraph( mygraph, firstrow, stitchinfo )
        # todo try with (1,2) and verbessere fehlerausgabe bis der Fehler
        # dadurch entdeckt werden kann.
        # uer komplizierte graphen reicht eine einfache ausgabe der 
        # nodenames wie es derzeit ist nicht mehr aus
        #self.assertTrue( asd.replace_in_graph( mystrick, (2,2) ) )
        success = asd.replace_in_graph( mystrick, (2,2) )

        self.assertTrue( success )

        testoutput ="5yo\n5k\n2k 1yo 3k\n2k 1k2tog 2k\n5k\n5bo"
        self.assertEqual( mystrick.to_manual( stitchinfo), testoutput )

    def test_multifrommanuals( self ):
        raise Exception( "no multimanuals yet" )
        pairlist = (( \
                "7yo\n2k 1kmark 1k2tog 2k\n2k 1k2tog 2k\n5bo", \
                "7yo\n2k 1kmark 2k 2bo\n5k\n5bo" \
                ), )
        myersetzer = strick_multiverbesserer.from_manuals( pairlist, \
                                                            side="right" )
        single = myersetzer.verbessererlist[0]
        #print( single.oldgraph.nodes(data=True), single.oldgraph_nodes )
        #raise Exception()
        mygraph = strickgraph.from_manual( pairlist[0][0], stitchinfo, \
                                        #manual_type = manual_type,\
                                        #startside=startside, \
                                        reverse=False \
                                        )
        mygraph = mygraph.copy_with_alternative_stitchtype()
        mygraph2 = strickgraph.from_manual( pairlist[0][1], stitchinfo )
        mygraph2 = mygraph2.copy_with_alternative_stitchtype()

        success,info = myersetzer.replace_in_graph_withinfo( mygraph, (1,3) )
        if not success:
            myersetzer.print_compare_to_graph_at_position( mygraph, (1,3) )
        self.assertTrue( success )
        self.assertEqual( mygraph, mygraph2 )

    def test_multiersetzer( self ):
        from importlib.resources import read_text
        xml_string = read_text( test_src, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )

        old_manual = read_text( test_src, \
                            "simplegrid_markstitch.knitmanual").splitlines()
        new_manual = read_text( test_src, \
                            "better_markstitch.knitmanual").splitlines()

        ersetzer1 = strickalterator.from_manuals( old_manual, new_manual, \
                                    stitchinfo, \
                                    manual_type= "machine",\
                                    startside="left" )
        ersetzer2 = strickalterator.from_manuals( old_manual, new_manual, \
                                    stitchinfo, \
                                    manual_type= "machine",\
                                    startside="right" )

        myersetzer = multiverbesserer([ ersetzer1, ersetzer2 ])


        for startside in ["left", "right"]:
            # create testgraph
            mygraph = netx.grid_2d_graph( 6, 5 )
            firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
            mystrick = strickgraph.from_gridgraph( mygraph, firstrow, \
                                    stitchinfo, startside=startside )

            # this is the work to be done, the replacement
            success = myersetzer.replace_in_graph( mystrick, (2,2) )

            # test results
            self.assertTrue( success )
            testoutput ="5yo\n5k\n2k 1yo 3k\n2k 1k2tog 2k\n5k\n5bo"
            controloutput = mystrick.to_manual( stitchinfo,manual_type="machine")
            #self.assertEqual( controloutput, testoutput )

    def test_sidealterator( self ):
        """currently in leftsideverbesserer is 7,4 as extra node but 
        no edge to it.
        """
        changedline_id = 4
        inman="16yo\n16k\n16k\n16k\n2k 1k2tog 8k 1k2tog 2k\n2k 1yo 10k 1yo 2k\n16bo"
        outman="16yo\n16k\n16k\n16k\n16k\n16k\n16bo"

        changedline_id = 4
        #inman ="14yo\n14k\n14k\n2k 1yo 10k 1yo 2k\n2k 1yo 12k 1yo 2k\n18k\n18bo"
        #outman="14yo\n14k\n14k\n14k 2yo\n4yo 16k\n2k 1k2tog 12k 1k2tog 2k\n18bo"
        inman='14yo\n14k\n14k\n2yo 14k\n16k 4yo\n2k 1k2tog 12k 1k2tog 2k\n18bo'
        outman='14yo\n14k\n14k\n14k 2yo\n4yo 16k\n2k 1k2tog 12k 1k2tog 2k\n18bo'
        #print( "inman: ", inman )
        #print( "outman: ", outman )
        less_graph = strickgraph.from_manual( inman, stitchinfo )
        great_graph = strickgraph.from_manual( outman, stitchinfo )

        from ..verbesserer.class_side_alterator import sidealterator
        #print( less_graph.to_manual( glstinfo,manual_type="machine" ), \
        #            great_graph.to_manual(glstinfo, manual_type="machine"))
        #input("continue?")

        startnode = (0,0)

        qwe = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )
        #print( qwe.alterator_left.newgraph_nodeattributes )
        #print( qwe.alterator_left.newgraph_edges_with_label )
        #print(inman)
        #print(outman)

        try_graph = strickgraph.from_manual( inman, stitchinfo )
        qnodes = set(try_graph.nodes())
        self.assertNotEqual( try_graph, great_graph )
        self.assertEqual( try_graph, less_graph )
        #print("edges1:", [e for e in try_graph.edges(data=True) if (5,2) in e])
        qwe.replace_in_graph( try_graph, changedline_id )
        newnodes = set(try_graph.nodes())
        #print( "removed: ", sorted(set(qnodes).difference(newnodes)) )
        #print( "added: ", sorted(set(newnodes).difference(qnodes)) )
        #print( newnodes )
        #print( qnodes )
        #print( try_graph.to_manual( stitchinfo ))

        self.assertEqual( try_graph, great_graph )
        del( try_graph )
        q = lambda: qwe.replace_in_graph( great_graph, changedline_id )
        self.assertRaises( Exception, q )
        #self.assertRaises( FindError, q )

        safe = qwe.to_xml()
        return

        qwe2 = sidealterator.from_xml( safe )
        try_graph = strickgraph.from_manual( inman, stitchinfo )
        self.assertNotEqual( try_graph, great_graph )
        qwe2.replace_in_graph( try_graph, changedline_id )
        self.assertEqual( try_graph, great_graph )


