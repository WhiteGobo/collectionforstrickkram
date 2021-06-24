from datagraph_factory import datagraph, factory_leaf, edgetype, conclusion_leaf
from .. import meshthings
from .. import strickgraph
from createcloth.meshhandler import prepare_gridcopy, gridrelaxator

def create_datagraphs():
    tmp = datagraph()
    #tmp.add_node( "mymesh", meshthings.ply_surface )
    tmp.add_node( "mysurf", meshthings.ply_2dmap )
    #tmp.add_edge( "mysurf", "mymesh", meshthings.map_to_mesh )
    tmp.add_node( "inputstrickgraph", strickgraph.strickgraph_container )
    tmp.add_edge( "mysurf", "inputstrickgraph", map_for_strickgraph )
    #tmp.add_edge( "inputstrickgraph", "mymesh", \
    #                meshthings.strickgraph_fit_to_mesh )
    prestatus = tmp.copy()
    tmp.add_node( "positiondata", strickgraph.strickgraph_spatialdata )
    tmp.add_edge( "inputstrickgraph", "positiondata", \
                    strickgraph.stitchposition)
    poststatus = tmp.copy()
    return prestatus, poststatus
def call_function( mysurf, inputstrickgraph ):
    mystrickgraph = inputstrickgraph.strickgraph
    surfacemap = mysurf.surfacemap
    border = mystrickgraph.get_borders()

    gridgraph = prepare_gridcopy( mystrickgraph )
    myrelaxator = gridrelaxator( gridgraph, surfacemap, border )
    myrelaxator.relax()
    returngraph = myrelaxator.get_positiongrid()

    return { "positiondata": strickgraph.strickgraph_spatialdata( returngraph )}
relax_strickgraph_on_surface \
                = factory_leaf( create_datagraphs, call_function, \
                name = __name__+"relax on strickgraph" )
del( create_datagraphs, call_function )


def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mymesh", meshthings.ply_surface )
    tmp.add_node( "mysurf", meshthings.ply_2dmap )
    tmp.add_edge( "mysurf", "mymesh", meshthings.map_to_mesh )
    tmp.add_node( "inputstrickgraph", strickgraph.strickgraph_container )
    tmp.add_edge( "inputstrickgraph", "mymesh", \
                    meshthings.strickgraph_fit_to_mesh )
    prestatus = tmp.copy()
    tmp.add_edge( "mysurf", "inputstrickgraph", map_for_strickgraph )
    poststatus = tmp.copy()
    return prestatus, poststatus
mesh_and_strickgraph_to_mapping_conclusion = conclusion_leaf(create_datagraphs)
del( create_datagraphs )


_valid_map_for_strickgraph = lambda : tuple(((meshthings.ply_2dmap, \
                                        strickgraph.strickgraph_container),))
map_for_strickgraph = edgetype( _valid_map_for_strickgraph, "maptostrick", "" )

