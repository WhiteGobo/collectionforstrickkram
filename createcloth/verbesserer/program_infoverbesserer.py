#!/bin/env python
from .class_multi_sidealterator import multi_sidealterator

import logging
logger = logging.getLogger( __name__ )
import argparse

def get_args():
    Programdescription = "Show information about targetted alterator."
    parser = argparse.ArgumentParser( description = Programdescription )
    parser.add_argument( 'filename', type=str, 
                        help="Filename to save the alterator" )
    args = parser.parse_args()
    return { "filename": args.filename }

def main( filename ):
    with open( filename, "rb" ) as myf:
        xmlstr = myf.read()
    obj = multi_sidealterator.fromxml( xmlstr )
    alteratorlist = obj.side_alterator_list
    exclusioncriteria = obj.exclusion_criteria
    for i, alt in enumerate( alteratorlist ):
        print( "\n", i )
        print( "exclusion: ", [ alteratorlist.index(exc_alt)  \
                    for exc_alt in exclusioncriteria.get( alt, [] ) ] )
        print( alt.notes )
        print( alt.leftstartindex )
        print( alt.rightstartindex )
        print( alt.alterator_left.spanning_tree_nodes )
        nattr = alt.alterator_left.nodeattributes_input
        print( { n:nattr[n] for n in alt.alterator_left.spanning_tree_nodes })
        print( alt.alterator_right.spanning_tree_nodes )
        nattr = alt.alterator_right.nodeattributes_input
        print( { n:nattr[n] for n in alt.alterator_right.spanning_tree_nodes })


if __name__ == "__main__":
    args = get_args()
    main( **args )
