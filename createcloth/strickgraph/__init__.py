"""Base options for strickgraphs

:todo: remove replaceimport
"""

from .strickgraph_base import strickgraph
#from .strickgraph_replacesubgraph \
#        import create_pathforhashing, follow_cached_path
#from .fromknitmanual import BrokenManual

#standard should be machine
handknitting_terms = ["thread", "handknit", "handknitting"]
"""List of all avilable terms for handknitting"""

machine_terms=["machine", "matrix"]
"""List of all available terms for machineknitting"""

class WrongTermError( Exception ):
    """Exception, when using the wrong term for machine- of handknitting"""
    pass
