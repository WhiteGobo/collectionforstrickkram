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
from typing import Iterable
import numpy as np

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
            linetypes, original_upedges, stitches_per_line = q
            return sum( {start:0, end:0, plain:1, increase:2, decrease:2 }\
                        .get( line, 3 ) for line in linetypes )
        q = sorted( q, key=mysort )
        for linetypes, original_upedges, stitches_per_line in q:
            #print(stitches_per_line, original_upedges )
            downedges = [ None, *original_upedges ]
            upedges = [ *original_upedges, None ]
            allinfo = zip( linetypes, downedges, upedges )
            #print( linetypes, original_upedges )
            idarray = class_idarray( stitches_per_line )
            #idarray = tuple( arr(original_upedges[1:]) \
            #                - arr(original_upedges[:-1]) )
            tmplist = brubru.setdefault( idarray, list() )
            tmplist.append( (linetypes, original_upedges) )


        import numpy as np
        myergebnis = []
        for idarray, qpartial in brubru.items():
            #adding rowlength
            from . import examplestates as es
            for k in range( len(idarray) ):
                for adder in [{k:2}, {k:2,k-1:1}, {k:2,k+1:1}]:
                    newidarray = idarray + [ adder.get(i, 0) \
                                            for i in range(len(idarray)) ]
                    for linetype_out, upedges in qpartial:
                        for linetype_in, upe2 in brubru.get( newidarray, list() ):
                            unsimilarity_vector = tuple( i!=j \
                                        for i,j in zip(linetype_out,linetype_in ))
                            from itertools import compress
                            reduce_to_differencelines = lambda vector: tuple( \
                                        compress( range(-k,len(vector)-k), vector ))
                            q = reduce_to_differencelines( unsimilarity_vector )
                            try:
                                maxdiff = max( abs(i) for i in q )
                            except ValueError: #q is empty
                                maxdiff = 0
                            if maxdiff < 2:
                                myergebnis.append((\
                                        linetype_out,
                                        linetype_in, 
                                        upedges, 
                                        tuple( x + {k:2}.get( i, 0 ) \
                                                for i, x in enumerate( upedges ) ),
                                        k, 
                                        ))
                                if linetype_out[k] == es.righteaves:
                                #if all( i==j for i,j in zip(linetype_out,[es.start, es.plain, es.plain, es.decrease, es.plain, es.decrease, end])):
                                    print(idarray.stitches_per_line, newidarray.stitches_per_line)
                                    print(maxdiff, q, k)
                                    print( [str(i) for i in linetype_out] )
                                    print( [str(i) for i in linetype_in] )
                                    print("ok")

        #return
        from ..verbesserer.class_side_alterator import sidealterator
        q = []
        lever = True
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id\
                                                                in myergebnis:
            if len(q) == 50:
                print( "current number of verbesserer: ", len(q))
                input( "continue?" )
            if lever:
                lever = False
                continue
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
                except Exception as err:
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
            except Exception as err:
                raise err
                print("failed")
            print( "needed time: ", mytime-time.time() )

        return

class class_idarray():
    def __init__( self, stitches_per_line ):
        self.stitches_per_line = tuple( i - stitches_per_line[0] \
                                    for i in stitches_per_line)
    def __hash__( self ):
        return self.stitches_per_line.__hash__()
    def __len__( self ):
        return len(self.stitches_per_line)
    def __add__( self, addtuple:Iterable[ int ] ):
        """
        :raises: TypeError
        """
        asdf = np.add( self.stitches_per_line, addtuple )
        return type(self)( asdf )

    def __eq__(self, other):
        return self.stitches_per_line == other.stitches_per_line


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
