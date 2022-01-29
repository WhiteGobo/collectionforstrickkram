#/bin/env python
import unittest

from .. import chasm_identifier
from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo

import logging
logger = logging.getLogger( __name__ )

class TestChasmidentifier( unittest.TestCase ):
    def test_classifychasm( self ):
        return
        mystrick = create_testgraph_with_chasm()
        raise Exception( mystrick.to_manual( glstinfo ) )
        #print( mystrick.to_manual(glstinfo) )
        chasm_identifier.classify( mystrick )



def create_testgraph_with_chasm():
    #create strickgraph 7yo;7k;3k 1bo 3k;3k skip 3k;3k skip 3k;
    nodeattr = {}
    edges = []
    rowlength, number_rows = 7, 5
    endofline=((0,6), (1,0), (2,6), (3,0), (3,4) )
    skip_stitches = [(3,3), (4,3)]
    bindoff_stitches = [ (2,3), (4,0),(4,1),(4,2),(4,4),(4,5),(4,6) ]
    for i in range(number_rows):
        for j in range( rowlength ):
            if (i,j) in skip_stitches:
                continue
            if (i,j) in bindoff_stitches:
                st_type = "bindoff"
            else:
                st_type = {0:"yarnover", number_rows-1:"bindoff"}.get(i,"knit")
            
            side = { 1:"left", 0:"right" }[ i%2 ]
            nodeattr[ (i,j) ] = { "stitchtype":st_type, "side":side }

            if (i,j) not in endofline:
                next_stitch = (i, j+1) if i%2==0 else (i, j-1)
            else:
                next_stitch = (i+1, j)
            edges.append( ((i,j), next_stitch, "next"))
            edges.append( ((i,j), (i+1,j), "up") )
    edges = [(v1,v2,label) for v1, v2, label in edges \
            if all(v in nodeattr for v in (v1,v2))]
    return strickgraph( nodeattr, edges )

if __name__ == "__main__":
    logging.basicConfig( level=logging.WARNING )
    #logging.basicConfig( level=logging.DEBUG )
    unittest.main()
