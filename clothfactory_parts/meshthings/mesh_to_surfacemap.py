from datagraph_factory.processes import factory_leaf
from datagraph_factory import datagraph
from . import meshtypes
#from .. import plystanford
from createcloth.meshhandler.surface_container import surfacemap

def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mymesh", meshtypes.ply_surface )
    prestatus = tmp.copy()
    tmp.add_node( "mysurfacemaps", meshtypes.ply_2dmap )
    tmp.add_edge( "mysurfacemaps", "mymesh", meshtypes.map_to_mesh )
    poststatus = tmp
    return prestatus, poststatus
def call_function( mymesh ):
    """
    This creates createcloth.meshhandler.surfacemap for the given 
    mesh 'mymesh'. The surfacemap is framed by the border 'myborder'.
    """
    mysurface = mymesh.surfacemesh
    mymap = surfacemap.from_surface( mysurface )
    return { "mysurfacemaps": meshtypes.ply_2dmap( mymap ) }
mesh_to_surfacemap = factory_leaf( create_datagraphs, call_function, \
                                    name=__name__+"mesh to surfacemap" )
