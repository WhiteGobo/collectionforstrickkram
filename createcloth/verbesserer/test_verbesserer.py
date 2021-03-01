import unittest
#from .manualtoverbesserung import main as manualtoverbesserung
#from .verbesserer_class import manualtoverbesserung, verbesserungtoxml, verbessererfromxml
from . import manualtoersetzer, verbesserungtoxml, verbessererfromxml
import pkg_resources
from ..strickgraph.strickgraph_fromgrid import create_strickgraph_from_gridgraph as fromgrid
from ..strickgraph.strickgraph_toknitmanual import tomanual
from ..strickgraph.strickgraph_base import strickgraph

import networkx as netx
from ..strickgraph.load_stitchinfo import myasd as stitchinfo
import extrasfornetworkx
from extrasfornetworkx import multiverbesserer

class test_manualtoverbesserung( unittest.TestCase ):
    def setUp( self ):
        pass

    def test_xmlverbesserung( self ):
        markedstitches_file = pkg_resources.resource_stream( __name__, \
                                        "resourcestest/markstitches.xml" )
        stitchinfo.add_additional_resources( markedstitches_file )
        markedstitches_file.close()

        old_manual_file = pkg_resources.resource_stream( __name__, \
                            "resourcestest/simplegrid_markstitch.knitmanual" )
        new_manual_file = pkg_resources.resource_stream( __name__, \
                            "resourcestest/better_markstitch.knitmanual" )

        old_manual = [x[:-1].decode("utf-8") for x in old_manual_file]
        new_manual = [x[:-1].decode("utf-8") for x in new_manual_file]
        asd = manualtoersetzer( old_manual, new_manual )

        old_manual_file.close()
        new_manual_file.close()

        qwe = asd.create_xml_string()
        #qwe = verbesserungtoxml( asd )
        remake = extrasfornetworkx.verbessererfromxml( qwe, \
                                                        graph_type=strickgraph )

        self.assertEqual( asd, remake )


    def test_tryingsimpleinsert( self ):
        print( "hier ist noch eine todo sache" )
        #markedstitches_file = pkg_resources.resource_stream( __name__, \
        #                                "resourcestest/markstitches.xml" )
        markedstitches_info = pkg_resources.resource_string( __name__, \
                                        "resourcestest/markstitches.xml" \
                                        ).decode("utf-8")
        stitchinfo.add_additional_resources( markedstitches_info )
        #markedstitches_file.close()
        new_manual_str = pkg_resources.resource_string( __name__, \
                            "resourcestest/better_markstitch.knitmanual" \
                            ).decode("utf-8")
        old_manual_str = pkg_resources.resource_string( __name__, \
                            "resourcestest/simplegrid_markstitch.knitmanual" \
                            ).decode("utf-8")

        asd = manualtoersetzer( old_manual_str, new_manual_str, stitchinfo, \
                                startside="right" )

        
        mygraph = netx.grid_2d_graph( 6, 5 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        mystrick = fromgrid( mygraph, firstrow )
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
        self.assertEqual(tomanual(mystrick), testoutput )


    def test_multiersetzer( self ):
        print( "hier ist noch eine todo sache" )
        markedstitches_file = pkg_resources.resource_stream( __name__, \
                                        "resourcestest/markstitches.xml" )
        stitchinfo.add_additional_resources( markedstitches_file )
        markedstitches_file.close()

        #old_manual_file = pkg_resources.resource_stream( __name__, \
        #                    "resourcestest/simplegrid_markstitch.knitmanual" )
        new_manual_str = pkg_resources.resource_string( __name__, \
                            "resourcestest/better_markstitch.knitmanual" \
                            ).decode("utf-8")
        old_manual_str = pkg_resources.resource_string( __name__, \
                            "resourcestest/simplegrid_markstitch.knitmanual" \
                            ).decode("utf-8")

        ersetzer1 = manualtoersetzer( old_manual_str, new_manual_str, \
                                    manual_type= "machine",\
                                    startside="left" )
        ersetzer2 = manualtoersetzer( old_manual_str, new_manual_str, \
                                    manual_type= "machine",\
                                    startside="right" )


        myersetzer = multiverbesserer([ ersetzer1, ersetzer2 ])


        for startside in ["left", "right"]:
            # create testgraph
            mygraph = netx.grid_2d_graph( 6, 5 )
            firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
            mystrick = fromgrid( mygraph, firstrow, startside=startside )

            # this is the work to be done, the replacement
            success = myersetzer.replace_in_graph( mystrick, (2,2) )

            # test results
            self.assertTrue( success )
            testoutput ="5yo\n5k\n2k 1yo 3k\n2k 1k2tog 2k\n5k\n5bo"
            self.assertEqual( tomanual(mystrick, manual_type="machine"), \
                                testoutput )
