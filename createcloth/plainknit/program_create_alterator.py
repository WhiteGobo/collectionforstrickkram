#!/bin/env python
from .create_example_strickgraphs import create_example_strickset
from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
from .create_example_strickgraphs import create_stitchnumber_to_examplestrick
from .create_example_strickgraphs import order_neighbouring
from ..verbesserer.class_side_alterator import sidealterator, multi_sidealterator
from collections import Counter
from . import state as st

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
        obj = pickle.load( myf )
    return obj
def savetofile( filename, obj ):
    logger.info( "Saving alterator to file" )
    with open( filename, "wb" ) as myf:
        pickle.dump( obj, myf )
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
    parser.add_argument( '--strickwidth', '-w', type=int, default=14,
                        help="Number of minimal number of stitches per line" )
    parser.add_argument( '--continue', action=argparse.BooleanOptionalAction,\
                        help="If used, load alterator from existing file and"
                        "build extra missing alterators", dest="cont" )
    parser.add_argument( '--skip-gen-exception', dest="skipexc", \
                        action=argparse.BooleanOptionalAction,\
                        help="Skips alteratorgeneration, when exception" )

    args = parser.parse_args()
    assert args.alteratortype in ( 'increase', 'decrease' ), \
            "alteratortype can only be 'increase' or 'decrease'"
    return {"filename": args.filename, \
            "alteratortype": args.alteratortype, \
            "min_row_length": args.strickwidth, \
            "strickgraphsize": args.stricklength, \
            "cont": args.cont, \
            "skip_exception": args.skipexc, \
            }

def main( filename, alteratortype, strickgraphsize = 8, min_row_length=14, cont=False, skip_exception=False ):
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

    increase_linetypes_collection: Iterable[ strickexample_alteration ] \
                = tuple( order_neighbouring( brubru ) )

    logger.info( "Starting creation of alterators" )

    extraoptions = { "skip_by_exception": skip_exception,\
            "pipe_for_interrupt": globalpipe,\
            }
    if cont:
        try:
            old_alterator = loadfromfile( filename )
            extraoptions["starttranslator_list"] =old_alterator.side_alterator_list
        except FileNotFoundError:
            pass

    if alteratortype == 'increase':
        increaser = multi_sidealterator.generate_from_linetypelist( \
                increase_linetypes_collection, **extraoptions )
        myalterator = increaser
    elif alteratortype == 'decrease':
        inc_to_dec = lambda lout, lin, upout, upin, lineid: (lin, lout, upin, upout, lineid)
        decrease_linetypes_collection \
                = [ inc_to_dec( *data ) \
                for data in increase_linetypes_collection ]
        decreaser = multi_sidealterator.generate_from_linetypelist( \
                decrease_linetypes_collection, **extraoptions )
        myalterator = decreaser
    else:
        raise KeyError( f"only alteratortype may be 'increase' or "\
                         f"'decrease', got '{alteratortype}'" )

    savetofile( filename, myalterator )



if __name__ == "__main__":
    signal( SIGINT, sigint_handler )
    args = get_args()
    logging.basicConfig( level=logging.INFO )
    main( **args )
