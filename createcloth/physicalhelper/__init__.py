"""This module should provide all dataclasses and standdata for 
physical-simulations
"""

from .edgelength_helper import singleedge_length, \
                                relaxedgelength_to_strickgraph, \
                                threadinfo

standardthreadinfo = threadinfo( 0.03, 1.0 )
"""Use this as standard

:todo: make this more a real thing. its only starting point
:meta public:
"""
