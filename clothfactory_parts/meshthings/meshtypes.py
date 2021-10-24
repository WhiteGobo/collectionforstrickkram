"""Datatypes of mesh and all corresponding things"""
from datagraph_factory import datatype, edgetype

from createcloth.meshhandler import plysurfacehandler, surfacemap

class ply_surface( datatype ):
    """plysurface??
    type mesh

    :ivar surfacemesh: ( :py:class:`plysurfacehandler.plysurfacehandler` )\
            Container for meshdata. for access see type-description
    :todo: Only use plysurfacehandler to extract and save data to ply-file,
            else use python-primitives
    """
    __slots__=( "surfacemesh", )
    def __init__( self, mesh ):
        self.surfacemesh = mesh

    def save_as( self, filepath ):
        self.surfacemesh.save_to_file( filepath )#, use_ascii=True, use_bigendian=False )

    @classmethod
    def load_from( cls, filepath ):
        myobject = plysurfacehandler.load_from_file( filepath )
        return cls( myobject )


class ply_2dmap( datatype ):
    """Map of 2d points to ND-Space. 

    :ivar plycontainer: ( \
        :py:class:`surfacemap<plysurfacehandler.surfacemap_utils.surfacemap>`\
        ) One of the surfacedatas of the corresponding
    :ivar uplength: float
    :ivar downlength: float
    :ivar rightlength: float
    :ivar leftlength: float
    :todo: Only primitive data should be transferred here
    :todo: change raise exceptiontype
    :raises: Exception
    """
    def __init__( self, plycontainer:surfacemap ):
        plycontainer.complete_surfaces_with_map()
        try:
            surface = plycontainer.get_surface( 0 )
        except IndexError as err:
            raise Exception( "given plyobject has no inherent surfacedata" ) \
                                                                    from err

        surfmap = surface.get_surfacemap()
        self.surfacemap = surfmap
        self.uplength = surfmap.uplength[-1]
        self.downlength = surfmap.downlength[-1]
        self.leftlength = surfmap.leftlength[-1]
        self.rightlength = surfmap.rightlength[-1]




_valid_map_to_mesh = lambda : tuple(((ply_2dmap, ply_surface),))
map_to_mesh = edgetype( _valid_map_to_mesh, "maptomesh", "" )
"""edgetype thingy"""
