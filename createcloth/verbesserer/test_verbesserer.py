import unittest
#import pkg_resources
import importlib
from ..strickgraph import strickgraph

import networkx as netx
from ..strickgraph.load_stitchinfo import myasd as stitchinfo
import extrasfornetworkx
from extrasfornetworkx import multiverbesserer, verbesserer
from .multiverbesserer import strick_multiverbesserer
from . import resourcestest as test_src
from .verbesserer_class import strickalterator

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
        remake = verbesserer.from_xmlstr( qwe, graph_type=strickgraph )

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
        success, extrainfo = asd.replace_in_graph_withinfo( mystrick, (2,2) )
        if not success:
            print( extrainfo )

        self.assertTrue( success )

        testoutput ="5yo\n5k\n2k 1yo 3k\n2k 1k2tog 2k\n5k\n5bo"
        #self.assertEqual( mystrick.to_manual( stitchinfo), testoutput )

    def test_multifrommanuals( self ):
        pairlist = (( \
                "6yo\n1k 1kmark 1k2tog 2k\n1k 1k2tog 2k\n4bo", \
                "6yo\n1k 1kmark 2k 2bo\n4k\n4bo" \
                ), )
        myersetzer = strick_multiverbesserer.from_manuals( \
                                pairlist, reverse=reversed, side="left", \
                                oldtranslatorlist = [] )
        mygraph = strickgraph.from_manual( pairlist[0][0] )
        mygraph2 = strickgraph.from_manual( pairlist[0][1] )
        success = myersetzer.replace_in_graph( mygraph, (1,1) )
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
