import unittest
#import pkg_resources
import importlib
from ..strickgraph import strickgraph

import networkx as netx
from ..stitchinfo import basic_stitchdata as glstinfo
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

    @unittest.skip( "have to build this test" )
    def test_strickalterator( self ):
        raise Exception()

    def test_multisidealterator( self ):
        """Basic test of multisidealterator

        :todo: implement toxml
        """
        from ..plainknit.examplestates import start, plain, end, decrease, increase, enddecrease
        asdf = [\
                #((start, plain, plain, plain, plain, plain, end), (start, decrease, plain, plain, plain, plain, end), (12, 12, 12, 12, 12, 12), (14, 12, 12, 12, 12, 12), 0), 
                ((start, plain, end), (start, increase, enddecrease), (10, 10), (10, 12), 1), 
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

        less_graph = strickgraph.from_manual( inman, glstinfo )
        great_graph = strickgraph.from_manual( outman, glstinfo )

        #print( less_graph.to_manual( glstinfo,manual_type="machine" ) )
        #            great_graph.to_manual(glstinfo, manual_type="machine"))
        #input("continue?")

        startnode = (0,0)

        qwe = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )

        try_graph = strickgraph.from_manual( inman, glstinfo )
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

        try_graph = strickgraph.from_manual( inman, glstinfo )
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
