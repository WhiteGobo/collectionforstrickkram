"""
Base options for strickgraphs
"""
from .strickgraph_fromgrid import create_strickgraph_from_gridgraph
from .strickgraph_toknitmanual import tomanual
from .strickgraph_base import strickgraph
#from . import load_stitchinfo as stitchinfo
from .strickgraph_replacesubgraph \
        import create_pathforhashing, follow_cached_path

from .constants import handknitting_terms, machine_terms
