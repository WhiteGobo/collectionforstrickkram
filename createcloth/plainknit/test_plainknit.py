import unittest
from . import state
from . import examplestates as st
import logging
import itertools as it
logging.basicConfig( level=logging.WARNING )
#logging.basicConfig( level=logging.DEBUG )
logger = logging.getLogger( __name__ )
import time

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_identifier( self ):
        for q in ( st.start, \
                    st.end, \
                    st.leftplane, \
                    st.rightplane, \
                    st.lefteaves, \
                    st.righteaves, \
                    st.enddecrease, \
                    st.plain, \
                    st.increase, \
                    st.decrease):
            simplediff = iter(q.get_downupdifference_examples()).__next__()
            bru = q.create_example_row( 10, 10 + simplediff )
            logger.debug( f"{q}, {bru}, {simplediff}" )
            self.assertIsInstance( bru, list )
            self.assertIsInstance( bru[0], str )
            self.assertTrue( q.identify( bru ) )
            self.assertIsInstance( q, state.rowstate )


    def test_createverbesserer( self ):
        from .create_example_strickgraphs import create_example_strickset
        from ..strickgraph import strickgraph
        from ..strickgraph.load_stitchinfo import myasd as glstinfo
        import numpy as np
        strickgraphsize = 8
        q = create_example_strickset( [], strickgraphsize, min_row_length=14 )
        #q2 = create_example_strickset( [], strickgraphsize, min_row_length=15 )
        bru = dict()
        createdgraphs = dict()
        starttime = time.time()
        brubru = {}
        #for linetypes, original_upedges in it.chain( q,q2 ):
        from numpy import array as arr
        from .examplestates import start, end, decrease,  lefteaves, righteaves, leftplane, rightplane, plain, increase, decrease
        def mysort( q ):
            linetypes, original_upedges = q
            return sum( {start:0, end:0, plain:1, increase:2, decrease:2 }\
                        .get( line, 3 ) for line in linetypes )
        q = sorted( q, key=mysort )
        for linetypes, original_upedges in q:
            downedges = [ None, *original_upedges ]
            upedges = [ *original_upedges, None ]
            allinfo = zip( linetypes, downedges, upedges )
            print( linetypes, original_upedges )
            idarray = tuple( arr(original_upedges[1:]) \
                            - arr(original_upedges[:-1]) )
            tmplist = brubru.setdefault( idarray, list() )
            tmplist.append( (linetypes, original_upedges) )

        import numpy as np
        myergebnis = []
        for idarray, qpartial in brubru.items():
            #adding rowlength
            for k in range( len(idarray)+1 ):
                adder = {k-1:2, k:-2}
                newidarray = tuple( x + adder.get( i, 0 ) \
                                    for i, x in enumerate(idarray) )
                for linetype_out, upedges in qpartial:
                    for linetype_in, upe2 in brubru.get( newidarray, list() ):
                        unsimilarity_vector = tuple( i!=j \
                                    for i,j in zip(linetype_out,linetype_in ))
                        from itertools import compress
                        reduce_to_differencelines = lambda vector: tuple( \
                                    compress( range(len(vector)), vector ))
                        q = reduce_to_differencelines( unsimilarity_vector )
                        try:
                            maxdiff = max( abs(i-k) for i in q )
                        except ValueError: #q is empty
                            maxdiff = 0
                        if maxdiff < 2:
                            adder2 = {k:2}
                            #print( maxdiff, unsimilarity_vector, tuple(abs(i-k) for i in q) )
                            #print( "graphs:\n%s\n%s" \
                            #        % ( " ".join(str(i) for i in linetype_out),\
                            #        " ".join(str(i) for i in linetype_in) ))
                            #print(
                            #        upedges, 
                            #        tuple( x + adder2.get( i, 0 ) \
                            #                for i, x in enumerate( upedges ) ),
                            #        )
                            #print( "\n" )
                            myergebnis.append((\
                                    linetype_out,
                                    linetype_in, 
                                    upedges, 
                                    tuple( x + adder2.get( i, 0 ) \
                                            for i, x in enumerate( upedges ) ),
                                    k, 
                                    ))

        from . import create_verbesserer as helper
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id \
                                                                in myergebnis:
            helper.myfoo( linetype_out, linetype_in, upedges_out, \
                                    upedges_in, changedline_id )

        return
        for man1, man2 in edges_manuals:
            starttime = time.time()
            graph1 = strickgraph.from_manual( man1, glstinfo )
            graph2 = strickgraph.from_manual( man2, glstinfo )
            #print( graph1.to_manual( glstinfo ) )
            #print( graph2.to_manual( glstinfo ) )
            return
            #print()
            #print( man1.splitlines()[0], man2.splitlines()[0] )
            #print( man1.splitlines()[0] == man2.splitlines()[0] )
            if man1.splitlines()[0] == man2.splitlines()[0]:
                startnode = (0,0)
            else:
                startnode = (len( man1.splitlines() )-1, 0)
            from extrasfornetworkx import generate_replacement_from_graphs
            nodelabels1 = graph1.get_nodeattributelabel()
            edgelabels1 = graph1.get_edgeattributelabels()
            nodelabels2 = graph2.get_nodeattributelabel()
            edgelabels2 = graph2.get_edgeattributelabels()
            nodetrans1 = { n:i for i, n in enumerate( nodelabels1.keys() )}
            nodetrans2 = { n:i for i, n in enumerate( nodelabels2.keys() )}
            nodelabels1 = { nodetrans1[ node ]: label \
                                for node, label in nodelabels1.items() }
            edgelabels1 = [ (nodetrans1[v1], nodetrans1[v2], label) \
                                for v1, v2, label in edgelabels1 ]
            nodelabels2 = { nodetrans2[ node ]: label \
                                for node, label in nodelabels2.items() }
            edgelabels2 = [ (nodetrans2[v1], nodetrans2[v2], label) \
                                for v1, v2, label in edgelabels2 ]

            repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                                nodelabels1, edgelabels1,\
                                                nodelabels2, edgelabels2, \
                                                startnode, startnode )
            print("\n\n")
            print( "repl1:", repl1, "\n", "repl2: ", repl2, "\n\n", common_nodes)
            print( "needed time: %.3f" %( time.time() - starttime ))

            #difference = somesomething( graph1, graph2 )

            break



if __name__ == "__main__":
    unittest.main()
