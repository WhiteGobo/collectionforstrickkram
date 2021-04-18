from datagraph_factory import datatype, edgetype

class mesh_pymesh2( datatype ):
    """
    :type mesh
    """
    def __init__( self, mesh, border ):
        self.mesh = mesh
        self.border = border
        #raise Exception() #include later to remove this class

_valid_generated_from = lambda: ((ply_surface,ply_2dmap),)
generated_from = edgetype( _valid_generated_from, \
                            "generated map from mesh", "")


from createcloth.meshhandler.surface_container import surface, surfacemap

class ply_surface( datatype ):
    """
    :type mesh
    """
    __slots__=( "surfacemesh", )
    def __init__( self, mesh ):
        self.surfacemesh = mesh

    def save_as( self, filepath ):
        self.surfacemesh.to_plyfile( filepath )

    @classmethod
    def load_from( cls, filepath ):
        mysurface = surface.from_plyfile( filepath )
        return cls( mysurface )


class ply_2dmap( datatype ):
    def __init__( self, surfacemap ):
        self.surfacemap = surfacemap

    @classmethod
    def load_from( cls, filepath ):
        surfmap = surfacemap.from_plyfile( filepath )
        return cls( surfmap )

    def save_as( self, filepath ):
        self.surfacemap.to_plyfile( filepath )


_valid_map_to_mesh = lambda : tuple(((ply_2dmap, ply_surface),))
map_to_mesh = edgetype( _valid_map_to_mesh, "maptomesh", "" )
