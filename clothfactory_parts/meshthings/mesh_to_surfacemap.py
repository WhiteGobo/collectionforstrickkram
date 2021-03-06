"""Transformer from simple mesh to surfacemap
"""

from datagraph_factory.processes import factory_leaf
from datagraph_factory import datagraph
from . import meshtypes
#from .. import plystanford
from typing import Dict, Union

def _create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mymesh", meshtypes.ply_surface )
    prestatus = tmp.copy()
    tmp.add_node( "mysurfacemaps", meshtypes.ply_2dmap )
    tmp.add_edge( "mysurfacemaps", "mymesh", meshtypes.map_to_mesh )
    poststatus = tmp
    return prestatus, poststatus
def _call_function( mymesh: meshtypes.ply_surface)\
                            -> Dict[ str, meshtypes.ply_2dmap]:
    """
    This creates createcloth.meshhandler.surfacemap for the given 
    mesh 'mymesh'. The surfacemap is framed by the border 'myborder'.
    """
    mysurface = mymesh.surfacemesh
    mymap_container = meshtypes.ply_2dmap( mysurface )
    return { "mysurfacemaps": mymap_container }
mesh_to_surfacemap:factory_leaf = factory_leaf( _create_datagraphs, \
                                    _call_function, \
                                    name=__name__+"mesh to surfacemap" )
"""Create mesh from surfacemap

.. autofunction:: _create_datagraphs
.. autofunction:: _call_function
"""
