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
    return { "mysurfacemaps": meshtypes.ply_2dmap( mysurface ) }
mesh_to_surfacemap = factory_leaf( create_datagraphs, call_function, \
                                    name=__name__+"mesh to surfacemap" )

#def create_datagraphs():
#    tmp = datagraph()
#    tmp.add_node( "mymesh", meshtypes.mesh_pymesh2 )
#    tmp.add_node( "myborder", plystanford.mesh_rectangleborder )
#    tmp.add_edge( "myborder", "mymesh", plystanford.rand_to_mesh )
#    prestatus = tmp.copy()
#    tmp.add_node( "mysurfacemaps", plystanford.mesh_2dmap )
#    tmp.add_edge( "mysurfacemaps", "mymesh", plystanford.map_to_mesh )
#    poststatus = tmp
#    return prestatus, poststatus
#def call_function( mymesh, myborder ):
#    """
#    This creates createcloth.meshhandler.surfacemap for the given 
#    mesh 'mymesh'. The surfacemap is framed by the border 'myborder'.
#    """
#    mesh_border = myborder.rand
#    mesh = mymesh.mesh
#    som = train_kohonenmap( mesh, mesh_border )
#    xyshape, pos_array, data_x, data_y, data_z= create_surfacemap_data( som)
#    returnsurfacemap = surfacemap( xyshape, pos_array, \
#                                    data_x, data_y, data_z )
#    return { "mysurfacemaps": plystanford.mesh_2dmap( returnsurfacemap ) }
#mesh_to_surfacemap = factory_leaf( create_datagraphs, call_function, \
#                                    name=__name__+"mesh to surfacemap" )

