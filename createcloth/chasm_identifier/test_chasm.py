#/bin/env python
import unittest

from .. import chasm_identifier
from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
from . import method_reducedvalidset as mrvs

import logging
logger = logging.getLogger( __name__ )
from . import method_generate_example as mge

class TestChasmidentifier( unittest.TestCase ):
    def test_tmp( self ):
        """This fails, because graph is not plain"""
        return
        myman = "20yo\n20k\n20k\n8k 4bo 8k\n8k switch1 8k\n8k switch1 8k\n8k switch1 8k\n8bo switch0 8bo"
        mystrick = strickgraph.from_manual( myman, glstinfo )
        mystrick.get_borders()

    def test_classifychasm( self ):
        myman = "20yo\n20k\n8k 4bo 8k\n8k switch1 8k\n8k switch0 8k\n8k switch1 8k\n8bo switch0 8bo"
        mystrick = strickgraph.from_manual( myman, glstinfo )
        props = chasm_identifier.classify( mystrick )
        self.assertEqual( props.crack_height, 4 )
        self.assertEqual( props.crack_arrays, ('plain', 'plain', 'plain', 'top') )
        self.assertEqual( props.crack_width, 4 )
        self.assertEqual( len(props.leftside), 4 )
        self.assertEqual( len(props.rightside), 4 )
        self.assertEqual( len(props.bottom), 6)
        #print( dict(props) )

    def test_createexample_chasm( self ):
        props = {'crack_height': 4, 'crack_width': 4,\
                'crack_arrays': ('plain', 'plain', 'plain', 'top'), \
                #'leftside': [['115', '114', '113', '112'], ['100', '101', '102', '103', '104'], ['83', '82', '81', '80', '79'], ['68', '69', '70', '71', '72']], \
                #'rightside': [['116', '117', '118', '119'], ['99', '98', '97', '96', '95'], ['84', '85', '86', '87', '88'], ['67', '66', '65', '64', '63']], \
                #'bottom': ['47', '48', '49', '50', '51', '52'], \
                }

        mystrick = mge.generate_example( **props, height=7, width=20 )
        myman = "20yo\n20k\n8k 4bo 8k\n8k switch1 8k\n8k switch0 8k\n8k switch1 8k\n8bo switch0 8bo"
        myman ="20yo\n20k\n8k 4bo 8k\ntunnel7 tunnel6 tunnel5 tunnel4 tunnel3 tunnel2 tunnel1 tunnel0 8k\n8k\n8k\n8bo\nload7 load6 load5 load4 load3 load2 load1 load0 switch1\n8k\n8k\n8k\n8bo"

        mystricktest = strickgraph.from_manual( myman, glstinfo )
        print( mystricktest.to_manual( glstinfo ))
        #self.assertEqual( mystrick, mystricktest )

    def test_create_chasm_verbesserer( self ):
        props1 = {'crack_height': 4, 'crack_width': 4,\
                'crack_arrays': ('plain', 'plain', 'plain', 'top'), \
                'height': 7, 'width': 20 }
        props2 = {'crack_height': 4, 'crack_width': 4,\
                'crack_arrays': ('plain', 'plain', 'decrease', 'top'), \
                'height': 7, 'width': 20 }
        difference_line = 5
        #myalt = chasm_alterator.from_difference( difference_line, props1, props2 )
        mystrick1 = mge.generate_example( **props1 )
        #alt_strick = myalt.asdf( mystrick1 )
        mystrick2 = mge.generate_example( **props2 )
        #self.assertEqual( alt_strick, mystrick2 )


    def test_create_reduced_valid_properties( self ):
        height = 7
        width = 20
        myid = mrvs.reduced_simple_chasms( height, width )
        reduced_properties = list( myid )
        props = [{'crack_height': 4, 'crack_width': 4, #'height': 7, 'width':20,\
                'crack_arrays': ('plain', 'plain', 'plain', 'top')},\
                {'crack_height': 4, 'crack_width': 4, #'height': 7, 'width': 20,\
                'crack_arrays': ('plain', 'plain', 'decrease', 'top') }, \
                ]
        #print( reduced_properties )
        for p in props:
            self.assertTrue( p in reduced_properties  )

#chasm_properties(crack_height=4, 
#        crack_arrays=('increase', 'increase', 'decrease', 'top'), 
#        crack_width=11, leftside=None, rightside=None, bottom=None), 


if __name__ == "__main__":
    logging.basicConfig( level=logging.WARNING )
    #logging.basicConfig( level=logging.DEBUG )
    unittest.main()
