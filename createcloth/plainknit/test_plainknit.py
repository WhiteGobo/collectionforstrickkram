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
from ..verbesserer.class_side_alterator import sidealterator, multi_sidealterator
from ..strickgraph.load_stitchinfo import myasd as glstinfo
from typing import Iterable
import numpy as np

from . import method_isplain as mip

import os
import signal
import psutil
import multiprocessing as mp


def asdf( less_graph, great_graph, startnode, changedline_id, myqueue ):
    try:
        a = sidealterator.from_graphdifference( less_graph, great_graph, startnode, changedline_id )
        myqueue.put( a )
    except Exception as err:
        pass

class TestMeshhandlerMethods( unittest.TestCase ):
    def test_identifier( self ):
        for q, side in ( (st.start,"right"), \
                    (st.end,"right"), \
                    (st.leftplane,"left"), \
                    (st.rightplane,"right"), \
                    (st.lefteaves,"left"), \
                    (st.righteaves,"right"), \
                    (st.enddecrease,"right"), \
                    (st.plain,"right"), \
                    (st.increase,"right"), \
                    (st.decrease,"right")):
            simplediff = iter(q.get_updowndifference_examples()).__next__()
            down = 10
            up = down + simplediff
            #print( str(q), f"down{down}, up{up}", side)
            bru = q.create_example_row( down, up, side=side )
            logger.debug( f"{q}, {bru}, {simplediff}" )
            self.assertIsInstance( bru, list )
            self.assertIsInstance( bru[0], str )
            self.assertTrue( q.identify( bru ) )
            self.assertIsInstance( q, state.rowstate )

    def test_if_strickgraph_isplainknit( self ):
        #mip.isplain_strickgraph( strickgraph )
        pass


    def test_createverbesserer( self ):
        from .create_example_strickgraphs import create_example_strickset
        from ..strickgraph import strickgraph
        from ..strickgraph.load_stitchinfo import myasd as glstinfo
        strickgraphsize = 7
        q = create_example_strickset( [], strickgraphsize, min_row_length=12 )
        q = list(q)
        #q2 = create_example_strickset( [], strickgraphsize, min_row_length=15 )
        bru = dict()
        createdgraphs = dict()
        starttime = time.time()
        #for linetypes, original_upedges in it.chain( q,q2 ):
        from .create_example_strickgraphs import create_stitchnumber_to_examplestrick
        brubru = create_stitchnumber_to_examplestrick( q )

        from .create_example_strickgraphs import order_neighbouring
        myergebnis = order_neighbouring( brubru )

        from ..verbesserer.class_side_alterator import sidealterator
        from collections import Counter

        #temporary for testing please delete
        mumu = {}
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id\
                                                                in myergebnis:
            tmplist = mumu.setdefault( (linetype_out, upedges_out, changedline_id ), list() )
            tmplist.append( (linetype_in, upedges_in) )
        for a,b in mumu.items():
            if len(b) > 1:
                linetype_out, upedges_out, changedline_id = a
                q1 = b[0]
                q2 = b[1]
                raise Exception(f"""
                linetype1: {linetype_out}, upedges_out: {upedges_out}, changed_lineid: {changedline_id}
                ex1:
                {q1}
                ex2:
                {q2}
                """)

        #endtesting

        asd= Counter( (linetype_out, upedges_out, changedline_id )
                            for linetype_out, linetype_in, upedges_out, \
                                    upedges_in, changedline_id in myergebnis)
        self.assertEqual( max( asd.values()), 1,msg="There are somelineconfigs"\
                            ", that have multiple possible extend-variants: %s"\
                            %([(a,b) for a,b in asd.items() if b > 1]))
        asd = set( linetype_out for linetype_out, linetype_in, upedges_out, \
                                    upedges_in, changedline_id in myergebnis)
        qasdf = set( a[0] for a in q )
        self.assertEqual( len( asd ), len( qasdf ), msg="There are some "
                            "thingies, that wont be extended, %s, %i, %i" \
                            %( qasdf.difference(asd), len(asd), len(q)))

        #increase_linetypes_collection = list(myergebnis)[:10]
        #inc_to_dec = lambda lout, lin, upout, upin, lineid: \
        #                    lin, lout, upin, upout, lineid
        #decrease_linetypes_collection \
        #        = [ inc_to_dec(data) for data in increase_linetypes_collection ]
        #increaser = multi_sidealterator.generate_from_linetypelist( \
        #                                    increase_linetypes_collection )
        #decreaser = multi_sidealterator.generate_from_linetypelist( \
        #                                    decrease_linetypes_collection )

        #ltypes, upedges =[ increase_linetypes_collection[4][i] for i in (0,2) ]



        #myalt = multi_sidealterator.generate_from_linetypelist( myergebnis )
        mp.set_start_method( 'spawn' )
        myqueue = mp.Queue()

        verbesserer_list = []
        myergebnis = myergebnis[:5]
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id\
                                                                in myergebnis:

            #print( "-"*50 )
            #print( len(verbesserer_list) )
            mytime = time.time()
            #asd = sidealterator.from_linetypes( linetype_out, linetype_in, \
            #                    upedges_out, upedges_in, changedline_id )
            #print( "needed time: ", mytime-time.time() )
            #continue


            great_graph = create_graph_from_linetypes( linetype_in, upedges_in )
            lever = False
            tmp_graph = create_graph_from_linetypes( linetype_out, upedges_out)
            for i in verbesserer_list:
                try:
                    #i.replace_in_graph( tmp_graph, changedline_id, dontreplace=True)
                    i.replace_in_graph( tmp_graph, changedline_id )
                    if tmp_graph == great_graph:
                        lever = True
                        #print("skip to next")
                        break
                    tmp_graph = create_graph_from_linetypes( linetype_out, upedges_out)
                    raise Exception( "This should never trigger" )
                except FindError:
                    continue
                except Exception as err:
                    #print("Why=")
                    continue
            if lever:
                continue
            less_graph = create_graph_from_linetypes( linetype_out, upedges_out)
            #print( less_graph.to_manual(glstinfo).replace('\n','\\n') )
            #print( great_graph.to_manual(glstinfo).replace('\n','\\n') )
            #print( linetype_out, upedges_out )

            if linetype_out[0] == linetype_in[1]:
                startnode = (0,0)
            else:
                startnode = (len( linetype_out )-1, 0)

            #print("create next verbesserer" )
            #print( time.ctime() )
            try:
                mpid = mp.Process(target=asdf, args=( less_graph, great_graph, startnode, changedline_id, myqueue ))
                mpid.start()
                for i in range(300):
                    if myqueue.empty() and mpid.is_alive():
                        time.sleep(1)
                    elif not myqueue.empty():
                        verbesserer_list.append( myqueue.get() )
                        break
                    else:
                        break
                    #os.waitpid( pid, os.WNOHANG )
                if mpid.is_alive():
                    mpid.terminate()
                    #print("failed - needed too much time")
                mpid.join()

            except Exception as err:
                raise err
                #raise Exception( less_graph.to_manual(glstinfo), great_graph.to_manual(glstinfo), startnode, changedline_id) from err
                #print("failed")
            #print( "needed time: ", mytime-time.time() )

        return


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


if __name__ == "__main__":
    unittest.main()
