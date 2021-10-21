from .examplestates import start, \
                    end, \
                    leftplane, \
                    rightplane, \
                    lefteaves, \
                    righteaves, \
                    enddecrease, \
                    plain, \
                    increase, \
                    decrease

from .method_isplain import isplain

import pickle as _pickle
from ..verbesserer import class_side_alterator as csa
import pkg_resources
plainknit_increaser_file = "build/plainknit_increaser.pickle"
"""file to load increaser from"""
plainknit_increaser: csa.multi_sidealterator
"""increaser from file as in plainknit_increaser_file"""
try:
    _filename = pkg_resources.resource_filename( __name__, plainknit_increaser_file )
    with open( _filename, "rb" ) as increaser_file:
        plainknit_increaser = _pickle.load( increaser_file )
except Exception as err:
    plainknit_increaser = None

plainknit_decreaser_file = "build/plainknit_decreaser.pickle"
"""file to load decreaser from"""
plainknit_decreaser: csa.multi_sidealterator
"""decreaser from file as described in plainknit_decreaser_file"""
try:
    _filename = pkg_resources.resource_filename( __name__, plainknit_decreaser_file )
    with open( _filename, "rb" ) as decreaser_file:
        plainknit_decreaser = _pickle.load( decreaser_file )
except Exception as err:
    plainknit_decreaser = None
