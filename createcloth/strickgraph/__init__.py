"""
Base options for strickgraphs
"""
#from .strickgraph_toknitmanual import tomanual
from .strickgraph_base import strickgraph
#from . import load_stitchinfo as stitchinfo
from .strickgraph_replacesubgraph \
        import create_pathforhashing, follow_cached_path

from .constants import handknitting_terms, machine_terms
from .load_stitchinfo import stitchdatacontainer
