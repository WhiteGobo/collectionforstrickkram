#!/bin/env python
from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
from .create_example_strickgraphs import create_example_strickset
from .create_example_strickgraphs import create_stitchnumber_to_examplestrick
from .create_example_strickgraphs import order_neighbouring
from .create_example_strickgraphs import order_to_nearest_neighbours, normalise_upedges
from ..verbesserer import sidealterator, NoTranslationPossible
from ..verbesserer import multi_sidealterator as multialt
from collections import Counter
from . import state as st
import itertools as it
from typing import Iterable
from . import rowstates as est
from .class_identifier import create_graph_from_linetypes

import logging
logger = logging.getLogger( __name__ )

import argparse

from typing import Tuple, Iterable
strickproto = Tuple[ st.rowstate ]
strickexample_alteration = Tuple[ \
                                strickproto, \
                                strickproto, \
                                Tuple[int], \
                                Tuple[int], \
                                int \
                                ]

from signal import signal, SIGINT
from sys import exit
import pickle

globalpipe = []
filename_for_sigint = None

def sigint_handler( signal_received, frame ):
    global filename_for_sigint
    global globalpipe
    try:
        alteratorlist = globalpipe[0]
    except Exception:
        exit(0)
    if len(alteratorlist) > 0:
        myalt = multialt( alteratorlist )
        savetofile( filename_for_sigint, myalt )
    print( "Exiting gracefully" )
    exit( 0 )

def loadfromfile( filename ):
    with open( filename, "rb" ) as myf:
        xmlstr = myf.read()
        #obj = pickle.load( myf )
    obj = multialt.fromxml( xmlstr )
    alteratorlist = obj.side_alterator_list
    exclusioncriteria = obj.exclusion_criteria
    return alteratorlist, exclusioncriteria, obj
def savetofile( filename, obj ):
    logger.info( "Saving alterator to file" )
    xmlstr = obj.toxml()
    with open( filename, "wb" ) as myf:
        myf.write( xmlstr )

def get_args():
    Programdescription = "Create Alterator for plainknit."
    parser = argparse.ArgumentParser( description = Programdescription )
    parser.add_argument( 'filename', type=str, 
                        help="Filename to save the alterator" )
    parser.add_argument( '--alteratortype', '-a', type=str, default='increase',
                        help="Alterator if increase or decrease of a line. "
                        "Can be 'increase' or 'decrease'." )
    parser.add_argument( '--stricklength', '-l', type=int, default=6,
                        help="Number of lines of examplestrick" )
    parser.add_argument( '--strickwidth', '-w', type=int, default=20,
                        help="Number of minimal number of stitches per line" )
    parser.add_argument( '--continue', action=argparse.BooleanOptionalAction,\
                        help="If used, load alterator from existing file and"
                        "build extra missing alterators", dest="cont" )
    parser.add_argument( '--testold', action=argparse.BooleanOptionalAction,\
                        help="test old alterators", dest="testold" )
    parser.add_argument( '--maximumuncommonnodes', '-n', type=int, default=8,
                        help="number of maximum uncommon nodes of alterators" )
    parser.add_argument( '--limitstart', type=int, default=None,
                        help="for reducing checkingalterationnumber" )
    parser.add_argument( '--limitend', type=int, default=None,
                        help="for reducing checkingalterationnumber" )
    parser.add_argument( '--timelimit', '-t', type=int, default=300,
                        help="for reducing checkingalterationnumber" )
    parser.add_argument( '--softtimelimit', type=int, default=None,
                        help="for reducing checkingalterationnumber" )
    parser.add_argument( '--softmaximumuncommonnodes', type=int, default=8,
                        help="number of maximum uncommon nodes of alterators" )
    #parser.add_argument( '--skip-gen-exception', dest="skipexc", \
    #                    action=argparse.BooleanOptionalAction,\
    #                    help="Skips alteratorgeneration, when exception" )

    args = parser.parse_args()
    assert args.alteratortype in ( 'increase', 'decrease' ), \
            "alteratortype can only be 'increase' or 'decrease'"
    kwargs = {"filename": args.filename, \
            "alteratortype": args.alteratortype, \
            "min_row_length": args.strickwidth, \
            "strickgraphsize": args.stricklength, \
            "cont": args.cont, \
            "maximum_uncommon_nodes": args.maximumuncommonnodes, \
            "timelimit": args.timelimit, \
            "testoldalt": args.testold, \
            }
    if args.limitstart is not None or args.limitend is not None:
        kwargs["limit"] = [\
                args.limitstart if args.limitstart is not None else 0, \
                args.limitend if args.limitend is not None else -1, \
                ]
    if args.softtimelimit is not None and args.softmaximumuncommonnodes is not None:
        kwargs["soft_timelimit"] = args.softtimelimit
        kwargs["soft_maximum_uncommon_nodes"] = args.softmaximumuncommonnodes
    return kwargs

        

def main( filename, alteratortype, maximum_uncommon_nodes, timelimit, \
                strickgraphsize = 8, min_row_length=14, cont=False, limit=None, 
                soft_timelimit=None, soft_maximum_uncommon_nodes=None, \
                testoldalt=False, only_print_info=False ):
    """

    :param alteratortype: defines, what alterator is created. possible is
        'increase' and 'decrease'
    """
    global filename_for_sigint
    global globalpipe
    filename_for_sigint = filename

    #raise Exception( filename, alteratortype, strickgraphsize, min_row_length )
    logger.info( f"create strickset for alteratortype {alteratortype}. " \
                    f"Stricksize: {strickgraphsize}, " \
                    f"Minimalrowlength: {min_row_length}" )
    q_r = create_example_strickset( strickgraphsize, startright=True, \
                                        min_row_length=min_row_length )
    q_r = list(q_r)
    logger.debug( f"number strickgraphen: {len(q_r)}" )
    brubru_r = create_stitchnumber_to_examplestrick( q_r, startside="right"  )

    q_l = create_example_strickset( strickgraphsize, startright=False, \
                                        min_row_length=min_row_length )
    q_l = list(q_l)
    logger.debug( f"number strickgraphen: {len(q_l)}" )
    brubru_l = create_stitchnumber_to_examplestrick( q_l, startside="left" )

    increase_linetypes_collection:Iterable[multialt.linetypepair] = []
    #qq = [ (clid, *b ) for clid, b in brubru_l.items() ]

    only_stitchnumbers_right = [ tuple(stitches_per_line) \
                                for _, _, stitches_per_line in q_r ]
    map_right_inandline_to_out = order_to_nearest_neighbours( 
                                only_stitchnumbers_right, \
                                increase= (alteratortype == 'increase') )
    only_stitchnumbers_left = [ tuple(stitches_per_line) \
                                for _, _, stitches_per_line in q_l ]
    map_left_inandline_to_out = order_to_nearest_neighbours( \
                                only_stitchnumbers_left, \
                                increase= (alteratortype == 'increase') )
    for left, right in zip(map_left_inandline_to_out.items(), \
                                    map_right_inandline_to_out.items() ):
        for pairinfo, startside in zip(( left, right ), ("left", "right")):
            sourceinfo, targetindices = pairinfo
            sourceindex, changed_line = sourceinfo
            q = q_r if startside=="right" else q_l
            targetindex = targetindices[0]
            linetype_in, upedges_in, stitchnumber_in = q[ sourceindex ]
            linetype_out, upedges_out, stitchnumber_out = q[ targetindex ]
            upedges_out_normed = normalise_upedges( stitchnumber_in, stitchnumber_out, \
                                    upedges_out )
            newneighbourtuple = multialt.linetypepair(
                                        linetype_in, 
                                        linetype_out,
                                        upedges_in, 
                                        upedges_out_normed, 
                                        changed_line, startside
                                        )
            newneighbourtuple.stitchnumber_in = stitchnumber_in
            newneighbourtuple.stitchnumber_out = stitchnumber_out
            increase_linetypes_collection.append( newneighbourtuple )
    #for a, b in it.zip_longest( order_neighbouring( brubru_l, "left" ), \
    #                            order_neighbouring( brubru_r, "right" ) ):
    #    if a is not None:
    #        increase_linetypes_collection.append( a )
    #    if b is not None:
    #        increase_linetypes_collection.append( b )

    def mysort( tmp_linetypepair: multialt.linetypepair ):
        linetypes_in = tmp_linetypepair.input_linetypelist
        linetypes_out = tmp_linetypepair.output_linetypelist
        upedges_in = tmp_linetypepair.input_upedges
        upedges_out = tmp_linetypepair.output_upedges
        stitchnumber_in = newneighbourtuple.stitchnumber_in
        stitchnumber_out = newneighbourtuple.stitchnumber_out
        weight = {est.start:0, est.end:0, est.plain:1, est.increase:2, est.decrease:2 }
        a = sum( weight.get( line, 3 ) for line in linetypes_in )
        b = sum( weight.get( line, 3 ) for line in linetypes_out )
        #c = sum( 1 for a,b in zip( linetypes_in, linetypes_out ) if a!=b )
        #d = sum( abs(a-b) for a,b in zip(upedges_in, upedges_out) )
        c = sum( 1 for a,b in zip(stitchnumber_in, stitchnumber_out) if a!=b )
        d = sum( abs(a-b) for a,b in zip(stitchnumber_in, stitchnumber_out) )
        return (c, d, a + b)
    increase_linetypes_collection.sort( key = mysort )
    #for a in  increase_linetypes_collection:
    #    print( a )
    #raise Exception()
    logger.info( f"found {len(increase_linetypes_collection)} of possible alterations" )


    #all_linetypes = { linetypes for linetypes, upedges, stitchnumbers in q }
    #all_linetypes_with_inc_line = list(it.chain.from_iterable( \
            #                            ( (i, lt ) for i in range(len(lt))) \
            #                            for lt in all_linetypes ))
    #for linetypes_in, m1,m2,m3,k in decrease_linetypes_collection:
    #    try:
    #        all_linetypes_with_inc_line.remove( ( k, linetypes_in ) )
    #    except ValueError as err:
    #        print( k, linetypes_in )
    #for i in all_linetypes_with_inc_line:
    #    print( i )
    #raise Exception()
    #raise Exception( all_linetypes_with_inc_line )

    if limit is not None:
        increase_linetypes_collection = increase_linetypes_collection[ limit[0]:limit[1] ]
    for i, a in enumerate( increase_linetypes_collection ):
        logger.debug( f"{i}: {a}" )
    if only_print_info:
        return
    #increase_linetypes_collection = _filterincrease_linetypes( increase_linetypes_collection )

    logger.info( "Starting creation of alterators" )

    extraoptions = { #"pipe_for_interrupt": globalpipe,\
            }
    if cont:
        try:
            with open( filename, "rb" ) as myf:
                xmlstr = myf.read()
                #obj = pickle.load( myf )
            myalt = multialt.fromxml( xmlstr )
        except FileNotFoundError:
            myalt = multialt( [] )
    else:
        myalt = multialt( [] )

    if False:
        qarray = []
        import time
        t0 = time.time()
        i = 0
        for input_linetypelist, output_linetypelist, input_upedges, output_upedges, changed_line, startside in increase_linetypes_collection:
            print( f"\ntestnext {i}: ", time.time()-t0 )
            print( input_linetypelist, output_linetypelist, input_upedges, output_upedges, changed_line, startside )
            i += 1
            source_graph = create_graph_from_linetypes( input_linetypelist, input_upedges, startside )
            target_graph = create_graph_from_linetypes( output_linetypelist, output_upedges, startside )
            try:
                q = myalt.test_replace( target_graph, source_graph, changed_line )
            except myalt.MultireplacementProducesWrongAlteration as err:
                brubru = myalt.replace_graph( source_graph, changed_line )
                raise Exception( brubru.to_manual( glstinfo), target_graph.to_manual(glstinfo) ) from err
                produces_wrong = err.produces_wrong
                produces_correct = list( err.produces_correct )
                print( produces_wrong, produces_correct )

            #raise Exception( input_linetypelist, output_linetypelist, input_upedges, output_upedges, changed_line, startside, q )
            qarray.append( q )
        raise Exception( qarray )

    if cont or testoldalt:
        old_alterator = None
        try:
            old_alteratorlist, old_exclusioncriteria,old_alterator = loadfromfile( filename )
            extraoptions["starting_side_alterator_list"] = old_alteratorlist
            extraoptions["exclusion_criteria"] = old_exclusioncriteria
        except FileNotFoundError:
            pass

        if testoldalt:
            test_old_alterator( old_alterator, increase_linetypes_collection )
            return

    extraoptions[ "timelimit" ] = timelimit
    if soft_timelimit is not None and soft_maximum_uncommon_nodes is not None:
        extraoptions[ "soft_timelimit" ] = soft_timelimit
        extraoptions[ "soft_maximum_uncommon_nodes"] = soft_maximum_uncommon_nodes
    extraoptions[ "maximum_uncommon_nodes" ] = maximum_uncommon_nodes

    increaser = multialt.generate_from_linetypelist( \
                increase_linetypes_collection, **extraoptions )
    myalterator = increaser
    savetofile( filename, myalterator )
    return
    if alteratortype == 'increase':
        inc_to_dec = lambda lout, lin, upout, upin, lineid, side: \
                            multialt.linetypepair(lin, lout, upin, upout, lineid, side)
        decrease_linetypes_collection \
                = [ inc_to_dec( *data ) \
                for data in increase_linetypes_collection ]
        decreaser = multialt.generate_from_linetypelist( \
                decrease_linetypes_collection, **extraoptions )
        myalterator = decreaser
    elif alteratortype == 'decrease':
        increaser = multialt.generate_from_linetypelist( \
                increase_linetypes_collection, **extraoptions )
        myalterator = increaser
    else:
        raise KeyError( f"only alteratortype may be 'increase' or "\
                         f"'decrease', got '{alteratortype}'" )

    savetofile( filename, myalterator )

def _filterincrease_linetypes( increase_linetypes_collection ):
    from .examplestates import start, end, leftplane, rightplane, \
                                    lefteaves, righteaves, \
                                    enddecrease, plain, increase, decrease
    #increase_linetypes_collection = [ (a,b,c,d,e)\
    #        for a,b,c,d,e in increase_linetypes_collection \
    #        if tuple(a[0:4]) == (start, leftplane, rightplane, decrease) \
    #        and tuple(b[0:4]) == (start, leftplane, rightplane, plain) \
    #        and e==3]
    increase_linetypes_collection = [ (a,b,c,d,e)\
            for a,b,c,d,e in increase_linetypes_collection \
            if (a[3] == increase and a[2] in (rightplane, leftplane, lefteaves, righteaves))\
            or (b[3] == increase and b[2] in (rightplane, leftplane, lefteaves, righteaves)) ]
    raise Exception( increase_linetypes_collection )
    return increase_linetypes_collection


from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
def test_old_alterator( old_alterator, linetypepairlist ):
    for i, ltpair in enumerate( linetypepairlist ):
        testline = ltpair.changed_line
        inputgraph = _create_graph_from_linetypes( ltpair.input_linetypelist, ltpair.input_upedges )
        outputgraph = _create_graph_from_linetypes( ltpair.output_linetypelist, ltpair.output_upedges )
        try:
            repl_graph = old_alterator.replace_graph( inputgraph, testline )
            raise Exception( inputgraph.to_manual(glstinfo), outputgraph.to_manual(glstinfo), ltpair.changed_line, repl_graph.to_manual(glstinfo) )
        except NoTranslationPossible as err:
            raise Exception( inputgraph.to_manual(glstinfo), outputgraph.to_manual(glstinfo), ltpair.changed_line ) from err
            print( "failed", i )

    raise Exception()

def _create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    sides = ("right", "left") if startside=="right" else ("left", "right")
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    iline = range(len(downedges))
    allinfo = zip( linetypes, downedges, upedges, iline )
    try:
        graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                for s, down, up, i in allinfo ]
    except Exception as err:
        raise Exception( [str(a) for a in linetypes], downedges, upedges, iline, startside ) from err
        raise err
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph


if __name__ == "__main__":
    #signal( SIGINT, sigint_handler )
    args = get_args()
    logging.basicConfig( level=logging.DEBUG )
    from extrasfornetworkx import verbesserer_tools 
    #verbesserer_tools.logger.setLevel( logging.DEBUG )

    main( **args )
