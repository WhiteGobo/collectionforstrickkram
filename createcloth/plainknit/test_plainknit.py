import unittest
from . import state
from . import examplestates as st
import logging
import itertools as it
logging.basicConfig( level=logging.WARNING )
#logging.basicConfig( level=logging.DEBUG )
logger = logging.getLogger( __name__ )
import time
from ..verbesserer.verbesserer_class import FindError
from ..strickgraph.load_stitchinfo import myasd as glstinfo

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
        strickgraphsize = 7
        q = create_example_strickset( [], strickgraphsize, min_row_length=14 )
        #q2 = create_example_strickset( [], strickgraphsize, min_row_length=15 )
        bru = dict()
        createdgraphs = dict()
        starttime = time.time()
        brubru = {}
        #for linetypes, original_upedges in it.chain( q,q2 ):
        from numpy import array as arr
        from .examplestates import start, end, enddecrease,  lefteaves, righteaves, leftplane, rightplane, plain, increase, decrease
        def mysort( q ):
            linetypes, original_upedges = q
            return sum( {start:0, end:0, plain:1, increase:2, decrease:2 }\
                        .get( line, 3 ) for line in linetypes )
        q = sorted( q, key=mysort )
        for linetypes, original_upedges in q:
            downedges = [ None, *original_upedges ]
            upedges = [ *original_upedges, None ]
            allinfo = zip( linetypes, downedges, upedges )
            #print( linetypes, original_upedges )
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
                        extrabedingung = sum( i[-1] == enddecrease \
                                        for i in [linetype_out, linetype_in])
                        if maxdiff < 2 and not extrabedingung == 1:
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

        from ..verbesserer.class_side_alterator import sidealterator
        q = []
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id \
                                                                in myergebnis:
            if len(q) == 50:
                print( "current number of verbesserer: ", len(q))
                input( "continue?" )
            print( "-"*50 )
            mytime = time.time()
            #a = helper.myfoo( linetype_out, linetype_in, upedges_out, \
            #                        upedges_in, changedline_id )
            less_graph = create_graph_from_linetypes( linetype_out, upedges_out )
            great_graph = create_graph_from_linetypes( linetype_in, upedges_in )
            lever = False
            print( less_graph.to_manual(glstinfo).replace('\n','\\n') )
            print( great_graph.to_manual(glstinfo).replace('\n','\\n') )
            for i in q:
                try:
                    i.replace_in_graph( less_graph, changedline_id )
                    if less_graph == great_graph:
                        less_graph = create_graph_from_linetypes( linetype_out, upedges_out )
                        lever = True
                        print("skip to next")
                        break
                    raise Exception( "This should never trigger" )
                except FindError:
                    continue
                except Exception:
                    #print("Why=")
                    continue
            if lever:
                continue

            if linetype_out[0] == linetype_in[1]:
                startnode = (0,0)
            else:
                startnode = (len( linetype_out )-1, 0)

            print("create next verbesserer" )
            try:
                a = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )
                q.append( a )
            except Exception:
                print("failed")
            print( "needed time: ", mytime-time.time() )

        return

from ..strickgraph import strickgraph
from ..strickgraph.load_stitchinfo import myasd as glstinfo
def create_graph_from_linetypes( linetypes, upedges ):
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    allinfo = zip( linetypes, downedges, upedges )
    graph_man = [ s.create_example_row( down, up ) \
                                for s, down, up in allinfo ]
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph


if __name__ == "__main__":
    unittest.main()
