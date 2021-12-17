#!/bin/env python
from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
from .create_example_strickgraphs import create_example_strickset
from .create_example_strickgraphs import create_stitchnumber_to_examplestrick
from .create_example_strickgraphs import order_neighbouring
from ..verbesserer.class_side_alterator import sidealterator, multi_sidealterator
from collections import Counter
from . import state as st
import itertools as it

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
        myalt = multi_sidealterator( alteratorlist )
        savetofile( filename_for_sigint, myalt )
    print( "Exiting gracefully" )
    exit( 0 )

def loadfromfile( filename ):
    with open( filename, "rb" ) as myf:
        xmlstr = myf.read()
        #obj = pickle.load( myf )
    obj = multi_sidealterator.fromxml( xmlstr )
    alteratorlist = obj.side_alterator_list
    return alteratorlist
def savetofile( filename, obj ):
    logger.info( "Saving alterator to file" )
    xmlstr = obj.toxml()
    with open( filename, "wb" ) as myf:
        myf.write( xmlstr )
        #pickle.dump( obj, myf )
    #with open( filename, 'w' ) as myfile:
    #    if alteratortype == 'increase':
    #        xmlstring = increaser.to_xml()
    #    elif alteratortype == 'decrease':
    #        xmlstring = decreaser.to_xml()
    #    myfile.write( xmlstring )

def get_args():
    Programdescription = "Create Alterator for plainknit."
    parser = argparse.ArgumentParser( description = Programdescription )
    parser.add_argument( 'filename', type=str, 
                        help="Filename to save the alterator" )
    parser.add_argument( '--alteratortype', '-a', type=str, default='increase',
                        help="Alterator if increase or decrease of a line. "
                        "Can be 'increase' or 'decrease'." )
    parser.add_argument( '--stricklength', '-l', type=int, default=8,
                        help="Number of lines of examplestrick" )
    parser.add_argument( '--strickwidth', '-w', type=int, default=18,
                        help="Number of minimal number of stitches per line" )
    parser.add_argument( '--continue', action=argparse.BooleanOptionalAction,\
                        help="If used, load alterator from existing file and"
                        "build extra missing alterators", dest="cont" )
    #parser.add_argument( '--skip-gen-exception', dest="skipexc", \
    #                    action=argparse.BooleanOptionalAction,\
    #                    help="Skips alteratorgeneration, when exception" )

    args = parser.parse_args()
    assert args.alteratortype in ( 'increase', 'decrease' ), \
            "alteratortype can only be 'increase' or 'decrease'"
    return {"filename": args.filename, \
            "alteratortype": args.alteratortype, \
            "min_row_length": args.strickwidth, \
            "strickgraphsize": args.stricklength, \
            "cont": args.cont, \
            }

def main( filename, alteratortype, strickgraphsize = 8, min_row_length=14, cont=False ):
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
    q = create_example_strickset( [], strickgraphsize, \
                                        min_row_length=min_row_length )
    q = list(q)
    logger.debug( f"number strickgraphen: {len(q)}" )
    brubru = create_stitchnumber_to_examplestrick( q )

    decrease_linetypes_collection: Iterable[ strickexample_alteration ] \
                = tuple( order_neighbouring( brubru ) )

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

    decrease_linetypes_collection = decrease_linetypes_collection[ :2000 ]

    #increase_linetypes_collection = _filterincrease_linetypes( increase_linetypes_collection )

    logger.info( "Starting creation of alterators" )

    extraoptions = { #"pipe_for_interrupt": globalpipe,\
            }
    if cont:
        try:
            old_alteratorlist = loadfromfile( filename )
            extraoptions["starting_side_alterator_list"] = old_alteratorlist
        except FileNotFoundError:
            pass

    if alteratortype == 'increase':
        extraoptions[ "maximum_uncommon_nodes" ] = 33
        dec_to_inc = lambda lout, lin, upout, upin, lineid: \
                            (lin, lout, upin, upout, lineid)
        increase_linetypes_collection \
                = [ dec_to_inc( *data ) \
                for data in decrease_linetypes_collection ]
        increaser = multi_sidealterator.generate_from_linetypelist( \
                decrease_linetypes_collection, **extraoptions )
        myalterator = increaser
    elif alteratortype == 'decrease':
        extraoptions[ "maximum_uncommon_nodes" ] = 30
        decreaser = multi_sidealterator.generate_from_linetypelist( \
                decrease_linetypes_collection, **extraoptions )
        myalterator = decreaser
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



if __name__ == "__main__":
    signal( SIGINT, sigint_handler )
    args = get_args()
    logging.basicConfig( level=logging.DEBUG )
    from extrasfornetworkx import verbesserer_tools 
    #verbesserer_tools.logger.setLevel( logging.DEBUG )

    main( **args )
