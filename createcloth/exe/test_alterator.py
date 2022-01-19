#!/bin/env python

from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
from ..verbesserer import multi_sidealterator as multialt
import logging
logging.basicConfig( level=logging.DEBUG )

import argparse
def get_args():
    Programdescription = "Create Alterator for plainknit."
    parser = argparse.ArgumentParser( description = Programdescription )
    parser.add_argument( 'sidealterator', type=str, 
                        help="Filename of alterator" )
    parser.add_argument( 'strickgraph', type=str, 
                        help="strickgraph as manual" )
    parser.add_argument( 'row', type=int,
                        help="rownumber, where alteration is used. -1 "
                        "is last line" )
    parser.add_argument( '--startside', '-s', type=str, default='right',
                        help="Startside of alterator." )

    args = parser.parse_args()
    kwargs = { "alteratorfile": args.sidealterator, \
                "strickgraph_manual": args.strickgraph.replace( "\\n", "\n" ), \
                "rownumber": args.row, \
                "startside": args.startside, \
                }
    return kwargs


def main( alteratorfile, strickgraph_manual, rownumber, startside ):
    mystrick = strickgraph.from_manual( strickgraph_manual, glstinfo )
    rownumber = rownumber % len( mystrick.get_rows() )

    with open( alteratorfile, "rb" ) as myf:
        xmlstr = myf.read()
    myalt = multialt.fromxml( xmlstr )

    producedgraph = myalt.replace_graph( mystrick, rownumber )
    print( producedgraph.to_manual( glstinfo ) )


if __name__=="__main__":
    kwargs = get_args()
    main( **kwargs )
