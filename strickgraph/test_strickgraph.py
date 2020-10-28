#/bin/env python

import unittest
import networkx as netx
import strickgraph_fromgrid as fromgrid 

class TestStringMethods( unittest.TestCase ):
    def setUp( self ):
        self.mygraph = netx.grid_2d_graph( 4,4 )
        self.firstrow = [ x for x in self.mygraph.nodes() if x[0] == 0 ]

    def test_createfromgrid( self ):
        asd = fromgrid.create_strickgraph_from_gridgraph( self.mygraph, \
                                                            self.firstrow )
        mynodes = {(0, 1), (0, 0), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), \
                    (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), \
                    (3, 2), (3, 3), 'start', 'end'}
        myedges = {((0, 0), (0, 1)), ((0, 0), (1, 0)), ((0, 1), (0, 2)), \
                ((0, 1), (1, 1)), ((0, 2), (0, 3)), ((0, 2), (1, 2)), ((0, 3),\
                (1, 3)), ((0, 3), (1, 3)), ((1, 0), (2, 0)), ((1, 0), (2, 0)),\
                ((1, 1), (2, 1)), ((1, 1), (1, 0)), ((1, 2), (2, 2)), ((1, 2),\
                (1, 1)), ((1, 3), (2, 3)), ((1, 3), (1, 2)), ((2, 0), (3, 0)),\
                ((2, 0), (2, 1)), ((2, 1), (3, 1)), ((2, 1), (2, 2)), ((2, 2),\
                (3, 2)), ((2, 2), (2, 3)), ((2, 3), (3, 3)), ((2, 3), (3, 3)),\
                ((3, 0), 'end'), ((3, 1), (3, 0)), ((3, 2), (3, 1)), ((3, 3),\
                (3, 2)), ('start', (0, 0))}
        myedges_edgetype = {((0, 0), (0, 1), 0): 'next', \
                ((0, 0), (1, 0), 0): 'up', ((0, 1), (0, 2), 0): 'next', \
                ((0, 1), (1, 1), 0): 'up', ((0, 2), (0, 3), 0): 'next', \
                ((0, 2), (1, 2), 0): 'up', ((0, 3), (1, 3), 0): 'next', \
                ((0, 3), (1, 3), 1): 'up', ((1, 0), (2, 0), 0): 'up', \
                ((1, 0), (2, 0), 1): 'next', ((1, 1), (2, 1), 0): 'up', \
                ((1, 1), (1, 0), 0): 'next', ((1, 2), (2, 2), 0): 'up', \
                ((1, 2), (1, 1), 0): 'next', ((1, 3), (2, 3), 0): 'up', \
                ((1, 3), (1, 2), 0): 'next', ((2, 0), (3, 0), 0): 'up', \
                ((2, 0), (2, 1), 0): 'next', ((2, 1), (3, 1), 0): 'up', \
                ((2, 1), (2, 2), 0): 'next', ((2, 2), (3, 2), 0): 'up', \
                ((2, 2), (2, 3), 0): 'next', ((2, 3), (3, 3), 0): 'up', \
                ((2, 3), (3, 3), 1): 'next', ((3, 0), 'end', 0): 'next', \
                ((3, 1), (3, 0), 0): 'next', ((3, 2), (3, 1), 0): 'next', \
                ((3, 3), (3, 2), 0): 'next', ('start', (0, 0), 0): 'next' }
        myedges_breakline = {((0, 3), (1, 3), 0): 1, ((1, 0), (2, 0), 1): 1, \
                ((2, 3), (3, 3), 1): 1}
        mynodes_stitchtype = {(0, 0): 'firstrow', (0, 1): 'firstrow', \
                (0, 2): 'firstrow', (0, 3): 'firstrow', (1, 0): 'knit', \
                (1, 1): 'knit', (1, 2): 'knit', (1, 3): 'knit', (2, 0): 'knit',\
                (2, 1): 'knit', (2, 2): 'knit', (2, 3): 'knit', \
                (3, 0): 'lastrow', (3, 1): 'lastrow', \
                (3, 2): 'lastrow', (3, 3): 'lastrow'}
        self.assertEqual( mynodes, set(asd.nodes()) )
        self.assertEqual( myedges, set(asd.edges()) )
        asdedgetype = netx.get_edge_attributes( asd, "edgetype" )
        asdbreakline = netx.get_edge_attributes( asd, "breakline" )
        self.assertEqual( asdedgetype, myedges_edgetype )
        self.assertEqual( asdbreakline, myedges_breakline )
        asdstitchtype = netx.get_node_attributes( asd, "stitchtype" )
        self.assertEqual( asdstitchtype, mynodes_stitchtype )

if __name__=="__main__":
    unittest.main()
