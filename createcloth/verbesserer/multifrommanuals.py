"""

:todo: stitchdata is directly imported to this, that may not be good
"""

import pkg_resources
import copy
from extrasfornetworkx import multiverbesserer

from .verbesserer_class import strickalterator
from .multiverbesserer import strick_multiverbesserer
from .manualtoverbesserung import _start_at_marked

from ..stitchinfo import basic_stitchdata as stitchinfo
from ..strickgraph.strickgraph_base import stricksubgraph as mygraphtype
from ..strickgraph.fromknitmanual import frommanual

def tryoldtranslator( translatorlist, startside, oldmanstr, newmanstr, \
                                        stitchinfo, reverse=False ):
    trystrick = frommanual( oldmanstr, stitchinfo, manual_type="machine", \
                                startside = startside, reversed=reverse )
    startpoint = _start_at_marked( trystrick )
    targetstrick = frommanual( newmanstr, stitchinfo, manual_type="machine", \
                                startside = startside, reversed=reverse )
    _start_at_marked( targetstrick ) #just to replace marked stitches
    for trans in translatorlist:
        asd = copy.deepcopy( trystrick )
        succ, info = trans.replace_in_graph_withinfo( asd, startpoint )
        if succ:
            if asd == targetstrick:
                return trans
    return None

def main( pairlist, reverse=False, side="both", oldtranslatorlist=[] ):
    if side == "both":
        usedsides = ("left", "right")
    elif side == "right":
        usedsides = ("right", )
    elif side == "left":
        usedsides = ("left", )
    else:
        raise KeyError( "'side' must be 'both', 'right' or 'left'." )

    markedstitches = pkg_resources.resource_string( __name__, \
                            "markstitches.xml" ).decode("utf-8")
    stitchinfo.add_additional_resources( markedstitches )
    ersetzerlist = []
    for old_manual_str, new_manual_str in pairlist:
        for myside in usedsides:
            try:
                if oldtranslatorlist:
                    foundtranslator = tryoldtranslator( oldtranslatorlist, \
                                                myside,\
                                                old_manual_str, new_manual_str,\
                                                stitchinfo, reverse=reverse )
                else:
                    foundtranslator = None
                if foundtranslator:
                    ersetzerlist.append( foundtranslator )
                else:
                    ersetzerlist.append(\
                            strickalterator.from_manuals( \
                            old_manual_str, new_manual_str, \
                            stitchinfo, \
                            startside=myside, reversed = reverse )
                            )
            except Exception as err:
                print( err.args )
                raise Exception("happend at %s" %( repr((old_manual_str, \
                                    new_manual_str)) ) ) from err

    myersetzer = strick_multiverbesserer( ersetzerlist )
    return myersetzer
