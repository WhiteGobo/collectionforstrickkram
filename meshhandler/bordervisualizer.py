import pymesh
def load_mesh( wavefront_name="curvedflat.obj", lengthfactor=0.1 ):
    """
    :return: return a mesh with edgelength is maximal the distance between
        the vertices in the loaded mesh
    """
    #edges =[ 125, 127, 142, 101 ]
    edges =[ 123, 130, 107, 104 ]
    mesh, dump, minimaldistance = None, None, None
    mesh_original = pymesh.load_mesh( wavefront_name )
    minimaldistance = findminimaldistance( mesh_original.vertices )
    max_length = lengthfactor * minimaldistance
    mesh, dump = pymesh.split_long_edges( mesh_original, max_length )
    new_edges = []
    verticelist = [tuple(a) for a in mesh.vertices]
    for i in edges:
        new_edges.append( verticelist.index( tuple(mesh_original.vertices[i])) )
    return mesh, new_edges
