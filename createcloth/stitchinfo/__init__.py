import importlib
from .load_stitchinfo import stitchdatacontainer

basic_stitchdata: stitchdatacontainer
"""Normal stitchdata"""
with importlib.resources.path( __name__, "stitches.xml" ) as filepath:
    basic_stitchdata = stitchdatacontainer.from_xmlfile( filepath )
