import createcloth
import datagraph_factory
import networkx as netx
from createcloth.strickgraph import strickgraph_fromgrid as fromgrid
from datagraph_factory.datagraph import datatype, edgetype, datagraph
from datagraph_factory.processes import DATATYPE, EDGETYPE
from datagraph_factory.processes import factory_leaf
from createcloth.meshhandler.create_surfacemap import get_surfacemap, \
                                                load_mesh, train_kohonenmap

from createcloth.meshhandler.create_surfacemap import create_surfacemap_data,\
                                                surfacemap
from createcloth.meshhandler.randrectangle import randrectangle_points
from .strickgraph_datatypes import strickgraph_stitchdata, strickgraph_spatialdata, strickgraph_container, stitchdata_of_strick

from createcloth.meshhandler.gridrelaxator import gridrelaxator
from createcloth.meshhandler.main import prepare_gridcopy


class mesh_pymesh2( datatype ):
    """
    :type mesh
    """
    def __init__( self, mesh, border ):
        self.mesh = mesh
        self.border = border

class filepath( datatype ):
    """
    :type filepath: str
    """
    def __init__( self, filepath ):
        self.filepath = filepath

class mesh_rectangleborder( datatype ):
    def __init__( self, rand ):
        self.rand = rand

class mesh_2dmap( datatype ):
    def __init__( self, surfacemap ):
        self.surfacemap = surfacemap

map_to_mesh = edgetype( mesh_2dmap, mesh_pymesh2, "maptomesh", "" )
rand_to_mesh = edgetype( mesh_rectangleborder, mesh_pymesh2, "randtomesh", "" )
generated_from = edgetype( mesh_pymesh2, filepath, \
                            "generated mesh from file", "")


tmp = datagraph()
tmp.add_node( "meshfilepath", filepath )
prestatus = tmp.copy()
tmp.add_node( "loaded_mesh", mesh_pymesh2 )
tmp.add_edge( "loaded_mesh", "meshfilepath", generated_from )
poststatus = tmp.copy()
del( tmp )
def call_function( meshfilepath ):
    file_name = meshfilepath.filepath
    mesh, edges = load_mesh( file_name )
    return { "loaded_mesh": mesh_pymesh2( mesh, edges ) }
load_mesh_from_plyford = factory_leaf( prestatus, poststatus, call_function, \
                                            name = __name__+"load mesh")
del( prestatus, poststatus, call_function )


tmp = datagraph()
tmp.add_node( "mymesh", mesh_pymesh2 )
prestatus = tmp.copy()
tmp.add_node( "myborder", mesh_rectangleborder )
tmp.add_edge( "myborder", "mymesh", rand_to_mesh )
poststatus = tmp.copy()
del( tmp )
def call_function( mymesh ):
    edges = mymesh.border
    mesh = mymesh.mesh
    mesh_border = randrectangle_points( edges[0], edges[1], \
                                        edges[2], edges[3], mesh, None )
    return {"myborder": mesh_rectangleborder( mesh_border )}
randrectangle_from_mesh_with_border \
                        = factory_leaf( prestatus, poststatus, call_function,\
                                            name = __name__+"create rand")
del( prestatus, poststatus, call_function )



use_stitchdata_for_construction = edgetype( \
                                        strickgraph_stitchdata, mesh_pymesh2, \
                                        "for strickgraph construction", "" )
strickgraph_fit_to_mesh = edgetype( strickgraph_container, \
                                        mesh_pymesh2, \
                                        "strickgraph fit for mesh", \
                                        "it originates, it doesnt need to be "\
                                        +"exactly fitted but the goal is to "\
                                        +"fit it" )
stitchposition = edgetype( strickgraph_container, strickgraph_spatialdata, \
                            "stitch position", "" )

tmp = datagraph()
tmp.add_node( "myrand", mesh_rectangleborder )
tmp.add_node( "stitchdata", strickgraph_stitchdata )
tmp.add_node( "mymesh", mesh_pymesh2 )
tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
tmp.add_edge( "stitchdata", "mymesh", use_stitchdata_for_construction )
prestatus = tmp.copy()
tmp.add_node( "roughstrickgraph", strickgraph_container )
tmp.add_edge( "roughstrickgraph", "stitchdata", stitchdata_of_strick )
tmp.add_edge( "roughstrickgraph", "mymesh", strickgraph_fit_to_mesh )
poststatus = tmp.copy()
del( tmp )
def call_function( myrand, stitchdata, mymesh ):
    uplength = abs( myrand.rand.updist[0] - myrand.rand.updist[-1] )
    downlength = abs( myrand.rand.downdist[0] - myrand.rand.downdist[-1] )
    rightlength = abs( myrand.rand.rightdist[0] - myrand.rand.rightdist[-1])
    leftlength = abs( myrand.rand.leftdist[0] - myrand.rand.leftdist[-1] )
    length_dict = { stitch: 0.1 for stitch in stitchdata.stitchlist.types }
    upstitchlength = length_dict[ stitchdata.plain_endrow ]
    downstitchlength = length_dict[ stitchdata.plain_startrow ]
    sidestitchlength = length_dict[ stitchdata.plain_stitch ]
    number_linelength = int((downlength + uplength) \
                        / (upstitchlength + downstitchlength))+1
    number_numberrows = int((rightlength + leftlength)  \
                        / (2 * sidestitchlength) ) + 1
    mygridgraph = netx.grid_2d_graph( number_numberrows, number_linelength )
    firstrow = [ x for x in mygridgraph.nodes() if x[0] == 0 ]
    mystrickgraph = fromgrid.create_strickgraph_from_gridgraph( \
                                                    mygridgraph, firstrow, \
                                                    stitchdata.stitchlist )

    return { "roughstrickgraph": strickgraph_container( mystrickgraph ) }
strickgraph_dummy_from_rand= factory_leaf( prestatus, poststatus,call_function,\
                                        name=__name__+"strickgraph_from_rand")


tmp = datagraph()
tmp.add_node( "mymesh", mesh_pymesh2 )
tmp.add_node( "mysurf", mesh_2dmap )
tmp.add_edge( "mysurf", "mymesh", map_to_mesh )
tmp.add_node( "inputstrickgraph", strickgraph_container )
#tmp.add_node( "myborder", mesh_rectangleborder )
#tmp.add_edge( "myborder", "mymesh", rand_to_mesh )
tmp.add_edge( "inputstrickgraph", "mymesh", strickgraph_fit_to_mesh )
prestatus = tmp.copy()
tmp.add_node( "positiondata", strickgraph_spatialdata )
tmp.add_edge( "inputstrickgraph", "positiondata", stitchposition )
poststatus = tmp.copy()
del( tmp )
def call_function( mymesh, mysurf, inputstrickgraph ):
    print("\n\nbrubru\n\n")
    strickgraph = inputstrickgraph.strickgraph
    surfacemap = mysurf.surfacemap
    border = strickgraph.get_borders()

    gridgraph = prepare_gridcopy( strickgraph )
    myrelaxator = gridrelaxator( gridgraph, surfacemap, border )
    myrelaxator.relax()
    returngraph = myrelaxator.get_positiongrid()
    print( returngraph.nodes() )

    return { "positiondata": strickgraph_spatialdata( returngraph ) }
relax_strickgraph_on_surface \
                = factory_leaf( prestatus, poststatus, call_function, \
                name = __name__+"relax on strickgraph" )


tmp = datagraph()
tmp.add_node( "mymesh", mesh_pymesh2 )
tmp.add_node( "myborder", mesh_rectangleborder )
tmp.add_edge( "myborder", "mymesh", rand_to_mesh )
prestatus = tmp.copy()
tmp.add_node( "mysurfacemaps", mesh_2dmap )
tmp.add_edge( "mysurfacemaps", "mymesh", map_to_mesh )
poststatus = tmp.copy()
del( tmp )
def call_function( mymesh, myborder ):
    """
    This creates createcloth.meshhandler.surfacemap for the given 
    mesh 'mymesh'. The surfacemap is framed by the border 'myborder'.
    """
    mesh_border = myborder.rand
    mesh = mymesh.mesh
    som = train_kohonenmap( mesh, mesh_border )
    xyshape, pos_array, data_x, data_y, data_z= create_surfacemap_data( som)
    returnsurfacemap = surfacemap( xyshape, pos_array, \
                                    data_x, data_y, data_z )
    return { "mysurfacemaps": mesh_2dmap( returnsurfacemap ) }
mesh_to_surfacemap = factory_leaf( prestatus, poststatus, call_function, \
                                    name=__name__+"mesh to surfacemap" )


all_datatypes = [ mesh_pymesh2, filepath, mesh_rectangleborder, mesh_2dmap ]
all_edgetypes = [ map_to_mesh, rand_to_mesh, generated_from]
all_factoryleafs = [ \
        load_mesh_from_plyford, \
        randrectangle_from_mesh_with_border, \
        mesh_to_surfacemap, \
        strickgraph_dummy_from_rand, \
        relax_strickgraph_on_surface, \
        ]
