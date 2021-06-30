from . import meshtypes
from datagraph_factory import datagraph, factory_leaf, edgetype
from .. import strickgraph
#from createcloth.strickgraph.load_stitchinfo import myasd as mythreadinfo
from createcloth.physicalhelper import standardthreadinfo as mythreadinfo
import networkx as netx
from createcloth.strickgraph import strickgraph_fromgrid as fromgrid 

from .. import strickgraph
tmpvalid = lambda: (\
            (strickgraph.strickgraph_stitchdata, meshtypes.ply_surface), \
            )
use_stitchdata_for_construction = edgetype( tmpvalid, \
                                        "for strickgraph construction", "" )
del( tmpvalid )

def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mymesh", meshtypes.ply_surface )
    tmp.add_node( "stitchdata", strickgraph.strickgraph_stitchdata )
    tmp.add_node( "mysurface", meshtypes.ply_2dmap )
    tmp.add_edge( "stitchdata", "mymesh", use_stitchdata_for_construction )
    tmp.add_edge( "mysurface", "mymesh", meshtypes.map_to_mesh )
    prestatus = tmp.copy()
    tmp.add_node( "roughstrickgraph", strickgraph.strickgraph_container )
    tmp.add_edge( "roughstrickgraph", "stitchdata", strickgraph.stitchdata_of_strick )
    tmp.add_edge( "roughstrickgraph", "mymesh", strickgraph_fit_to_mesh )
    poststatus = tmp
    return prestatus, poststatus
def call_function( stitchdata, mymesh, mysurface ):
    uplength = mysurface.uplength
    downlength = mysurface.downlength
    leftlength = mysurface.leftlength
    rightlength = mysurface.rightlength

    downstitchlength = mythreadinfo.plainknit_startstitchwidth
    upstitchlength = mythreadinfo.plainknit_endstitchwidth
    sidestitchlength = mythreadinfo.plainknit_stitchheight
    #mythreadinfo.plainknit_normalstitchwidth
    #length_dict = { stitch: 0.1 for stitch in stitchdata.stitchlist.types }
    #upstitchlength = length_dict[ stitchdata.plain_endrow ]
    #downstitchlength = length_dict[ stitchdata.plain_startrow ]
    #sidestitchlength = length_dict[ stitchdata.plain_stitch ]
    number_linelength = 1 + int((downlength + uplength) \
                        / (upstitchlength + downstitchlength))
    number_numberrows = 1 + int((rightlength + leftlength)  \
                        / (2 * sidestitchlength) )
    mygridgraph = netx.grid_2d_graph( number_numberrows, number_linelength )
    firstrow = [ x for x in mygridgraph.nodes() if x[0] == 0 ]
    mystrickgraph = fromgrid.create_strickgraph_from_gridgraph( \
                                                    mygridgraph, firstrow, \
                                                    stitchdata.stitchlist )

    lengthdict = {}
    for e in mystrickgraph.edges( keys=True ):
        lengthdict[ e ] = upstitchlength
    netx.set_edge_attributes( mystrickgraph, lengthdict, "length" )

    return { "roughstrickgraph": strickgraph.strickgraph_container( mystrickgraph ) }
strickgraph_dummy_from_rand= factory_leaf( create_datagraphs, call_function,\
                                        name=__name__+"strickgraph_from_rand")



tmpvalid = lambda: (
                (strickgraph.strickgraph_container, meshtypes.ply_surface), \
                )
strickgraph_fit_to_mesh = edgetype( tmpvalid, \
                                        "strickgraph fit for mesh", \
                                        "it originates, it doesnt need to be "\
                                        +"exactly fitted but the goal is to "\
                                        +"fit it" )
del( tmpvalid )
