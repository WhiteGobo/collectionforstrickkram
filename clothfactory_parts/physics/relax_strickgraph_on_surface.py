from datagraph_factory import datagraph, factory_leaf, edgetype, conclusion_leaf
from .. import meshthings
from .. import strickgraph
from createcloth.meshhandler import relax_gridgraph
from createcloth.physicalhelper import standardthreadinfo as mythreadinfo

from typing import Dict, Union

_valid_map_for_strickgraph = lambda : tuple(((meshthings.ply_2dmap, \
                                        strickgraph.strickgraph_container),))
map_for_strickgraph: edgetype = edgetype( _valid_map_for_strickgraph, "maptostrick", __name__ )
"""Positon of Strickgraph may be mapped with that 2dmap"""


class relax_strickgraph_on_surface( factory_leaf ):
    #def _rsos_create_datagraphs():
    def generate_datagraphs( self ):
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
    def call_function( self, mysurf: meshthings.ply_2dmap, \
                        inputstrickgraph: strickgraph.strickgraph_container )\
                        -> Dict[ str, strickgraph.strickgraph_spatialdata ]:
        mystrickgraph = inputstrickgraph.strickgraph
        #mystrickgraph.set_calmlength( mythreadinfo )
        surfacemap = mysurf.surfacemap
        border = mystrickgraph.get_borders()
        myedges = [ e[:2] for e in mystrickgraph.get_edges_with_labels() ]
        upstitchlength = mythreadinfo.plainknit_endstitchwidth
        calm_edgelength = [ upstitchlength ] * len( myedges )


        positiondictionary = relax_gridgraph( mystrickgraph, surfacemap )

        xpos = { n: data['x'] for n, data in positiondictionary.items() }
        ypos = { n: data['y'] for n, data in positiondictionary.items() }
        zpos = { n: data['z'] for n, data in positiondictionary.items() }
        spatdata = strickgraph.strickgraph_spatialdata( xpos, ypos, zpos, myedges,calm_edgelength )
        return { "positiondata": spatdata }
#relax_strickgraph_on_surface : factory_leaf\
#                = factory_leaf( _rsos_create_datagraphs, _rsos_call_function, \
#                name = __name__+"relax on strickgraph" )
"""relax strickgraph on surface creating positiondata

.. autofunction:: _rsos_call_function
.. autofunction:: _rsos_create_datagraphs
"""


def _mfs_create_datagraphs():
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
mesh_and_strickgraph_to_mapping_conclusion: conclusion_leaf \
                        = conclusion_leaf(_mfs_create_datagraphs)
"""Conclusionleaf that strickgraphs corresponding to a mesh correspond 
also to surfacemaps of the mesh
"""


