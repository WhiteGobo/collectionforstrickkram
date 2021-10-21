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

from ..verbesserer.class_side_alterator import sidealterator, multi_sidealterator

import logging
logger = logging.getLogger( __name__ )
logging.basicConfig( level = logging.WARNING )

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
        #print( "hier ist noch eine todo sache" )
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
        return
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

    @unittest.skip( "maybe i will not use this anymore" )
    def test_multiersetzer( self ):
        """obsolete"""
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

    def test_multisidealterator( self ):
        """Basic test of multisidealterator

        :todo: implement toxml
        """
        from ..plainknit.examplestates import start, plain, end, decrease, increase
        asdf = [\
                #((start, plain, plain, plain, plain, plain, end), (start, decrease, plain, plain, plain, plain, end), (12, 12, 12, 12, 12, 12), (14, 12, 12, 12, 12, 12), 0), 
                ((start, plain, plain, plain, plain, plain, end), (start, increase, decrease, plain, plain, plain, end), (12, 12, 12, 12, 12, 12), (12, 14, 12, 12, 12, 12), 1), 
                #((start, plain, plain, plain, plain, plain, end), (start, plain, increase, decrease, plain, plain, end), (12, 12, 12, 12, 12, 12), (12, 12, 14, 12, 12, 12), 2), 
                #((start, plain, plain, plain, plain, plain, end), (start, plain, plain, increase, decrease, plain, end), (12, 12, 12, 12, 12, 12), (12, 12, 12, 14, 12, 12), 3),\
                        ]
        myalt = multi_sidealterator.generate_from_linetypelist( asdf )
        for l1, l2, upedges1, upedges2, k in asdf:
            graph1 = create_graph_from_linetypes( l1, upedges1 )
            graph2 = create_graph_from_linetypes( l2, upedges2 )
            myalt.replace_in_graph( graph1, k )
            self.assertEqual( graph1, graph2 )

        return

        myxmlstring = myalt.to_xml()
        myalt_dupl = multi_sidealterator.from_xml( myxmlstring )
        graph1 = create_graph_from_linetypes( asdf[0][0], asdf[0][2] )
        for l1, l2, upedges1, upedges2, k in asdf:
            graph1 = create_graph_from_linetypes( l1, upedges1 )
            graph2 = create_graph_from_linetypes( l2, upedges2 )
            myalt_dupl.replace_in_graph( graph1, k )
            self.assertEqual( graph1, graph2 )

    @unittest.skip("temporary" )
    def test_sidealterator( self ):
        """currently in leftsideverbesserer is 7,4 as extra node but 
        no edge to it.
        """
        changedline_id = 4
        inman="16yo\n16k\n16k\n16k\n2k 1k2tog 8k 1k2tog 2k\n14bo"
        outman="16yo\n16k\n16k\n16k\n16k\n16bo"

        less_graph = strickgraph.from_manual( inman, stitchinfo )
        great_graph = strickgraph.from_manual( outman, stitchinfo )

        #print( less_graph.to_manual( glstinfo,manual_type="machine" ) )
        #            great_graph.to_manual(glstinfo, manual_type="machine"))
        #input("continue?")

        startnode = (0,0)

        qwe = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )

        try_graph = strickgraph.from_manual( inman, stitchinfo )
        qnodes = set(try_graph.nodes())
        self.assertNotEqual( try_graph, great_graph )
        self.assertEqual( try_graph, less_graph )

        print( "-"*75 )
        qwe.replace_in_graph( try_graph, changedline_id )
        newnodes = set(try_graph.nodes())
        print( try_graph.to_manual( glstinfo ))
        print( great_graph.to_manual( glstinfo ))

        self.assertEqual( try_graph, great_graph )
        del( try_graph )
        q = lambda: qwe.replace_in_graph( great_graph, changedline_id )
        self.assertRaises( Exception, q )
        #self.assertRaises( FindError, q )

        try_graph = strickgraph.from_manual( inman, stitchinfo )
        #self.further_test_save_sidealterator( qwe, try_graph, great_graph, \
        #                            changedline_id )


    def further_test_save_sidealterator( self, mysidealterator, graph1, graph2,\
                                    changedline_id):
        """Testing to(from)xml of sidealterator"""
        safe = mysidealterator.to_xml()

        qwe2 = sidealterator.from_xml( safe )
        self.assertNotEqual( graph1, graph2 )
        qwe2.replace_in_graph( graph1, changedline_id )
        self.assertEqual( graph1, graph2 )


from ..strickgraph import strickgraph
from ..strickgraph.load_stitchinfo import myasd as glstinfo
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
