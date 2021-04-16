from scipy.spatial import Delaunay
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
import numpy as np
import itertools
from scipy.sparse import lil_matrix, csc_matrix
from numpy.linalg import norm
from scipy.sparse.linalg import spsolve
from . import numpyrelaxator as myrel
from .. import ply_handler as _ply


def create_surfacemap( surfinter, ulength, vlength ):
    umin, umax = 0, ulength
    vmin, vmax = 0, vlength

    nu, nv = ulength+1, vlength+1
    xyzmatrix = []
    #u_array = np.linspace(umin, umax, nu)
    #v_array = np.linspace(vmin, vmax, nv)
    u_array = np.linspace(0,1, ulength)
    v_array = np.linspace(0,1,vlength )
    for u in u_array:
        current_line = []
        xyzmatrix.append( current_line )
        for v in v_array:
            current_line.append( surfinter( u, v ) )
    xyzmatrix = np.stack( xyzmatrix )
    xyzmatrix = xyzmatrix

    asd = surfacemap( xyzmatrix, u_array, v_array )
    #for i, u in enumerate( u_array ):
    #    for j, v in enumerate( v_array ):
    #        print( i,j, np.array( asd.pos( u,v ) )- np.array(xyzmatrix[i][j]) )

    return asd



class surfacemap():
    def __init__( self, xyzmatrix, u_array, v_array ):
        #u_m, v_m = np.meshgrid( u_array, v_array )
        #uv = np.ndarray( (len(u_array), len(v_array),2) )
        self.xyzmatrix = xyzmatrix

        xyz = np.array( xyzmatrix )
        x = xyz[:,:,0]
        y = xyz[:,:,1]
        z = xyz[:,:,2]
        self.mapx = create_mapping_device_fromgrid( u_array, v_array, x )
        self.mapy = create_mapping_device_fromgrid( u_array, v_array, y )
        self.mapz = create_mapping_device_fromgrid( u_array, v_array, z )
        self.umin, self.umax = min(u_array), max(u_array)
        self.vmin, self.vmax = min(v_array), max(v_array)

        urange = self.umax - self.umin
        vrange = self.vmax - self.vmin
        dxdu, dxdv, dydu, dydv, dzdu, dzdv = self._calc_grads( xyz, \
                                                    urange, vrange)
                                                    #len(u_array), len(v_array))
        self.mapdxdu = create_mapping_device_fromgrid( u_array, v_array, dxdu )
        self.mapdxdv = create_mapping_device_fromgrid( u_array, v_array, dxdv )
        self.mapdydu = create_mapping_device_fromgrid( u_array, v_array, dydu )
        self.mapdydv = create_mapping_device_fromgrid( u_array, v_array, dydv )
        self.mapdzdu = create_mapping_device_fromgrid( u_array, v_array, dzdu )
        self.mapdzdv = create_mapping_device_fromgrid( u_array, v_array, dzdv )
        self.maxdistance = self.calc_max_distance_with_grad( x, y, z, u_array,\
                                                    v_array )

    @classmethod
    def from_surface( cls, mysurface ):
        faces = mysurface.faces
        vertexpositions = mysurface.vertices
        up, right  = mysurface.up, mysurface.right
        down, left = mysurface.down, mysurface.left

        st_coordinates = calculate_uv_position_distanceoptimised( \
                                                    faces, vertexpositions, \
                                                    up, right, down, left )
        uv_to_xyz = generate_surfaceinterpolator( vertexpositions, \
                                                        st_coordinates )
        ulength, vlength = 2**5, 2**5
        u_array = np.linspace( 0, 1, ulength)
        v_array = np.linspace( 0, 1, vlength)
        u, v, x,y,z = myrel.relax_with_numpy( uv_to_xyz, u_array, v_array )
        u, v = x.shape
        xyz_matrix = np.ndarray( (u, v, 3) )
        xyz_matrix[:,:,0] = x
        xyz_matrix[:,:,1] = y
        xyz_matrix[:,:,2] = z
        u_array = np.linspace( 0,1,u )
        v_array = np.linspace( 0,1,v )
        return cls( xyz_matrix, u_array, v_array )


    @classmethod
    def from_plyfile( cls, filepath ):
        myobj = _ply.load_ply_obj_from_filename( filepath )
        vertex_positions = myobj[ "matrix" ].get_filtered_data( "x","y","z")[0]
        u_length, v_length = myobj[ "matrix" ].get_filtered_data( "u", "v" )[0]
        xyz_matrix = np.ndarray( (u_length* v_length, 3) )
        xyz_matrix[:,0] = vertex_positions[0]
        xyz_matrix[:,1] = vertex_positions[1]
        xyz_matrix[:,2] = vertex_positions[2]
        xyz_matrix = xyz_matrix.reshape( u_length, v_length, 3 )
        u_array = np.linspace( 0,1, u_length )
        v_array = np.linspace( 0,1, v_length )
        return cls( xyz_matrix, u_array, v_array )


    def to_plyfile( self, filepath ):
        ulength, vlength = self.xyzmatrix.shape[0:2]
        x = self.xyzmatrix[:,:,0]
        y = self.xyzmatrix[:,:,1]
        z = self.xyzmatrix[:,:,2]
        xyzmatrix = [ (ulength,), (vlength,), (x.reshape(x.size),), \
                            (y.reshape(y.size),), (z.reshape(z.size),)]
        matrixpipeline = ( \
                            (b"uint", b"u"), (b"uint", b"v"), \
                            (b"list", b"uchar", b"float", b"x"), \
                            (b"list", b"uchar", b"float", b"y"), \
                            (b"list", b"uchar", b"float", b"z"), \
                            )

        myobj = _ply.ObjectSpec.from_arrays([ \
                            ("matrix", matrixpipeline, xyzmatrix), \
                            ])
        _ply.export_plyfile( filepath , myobj, "ascii" )

    def __call__( self, u, v ):
        x = self.mapx( u, v )
        y = self.mapy( u, v )
        z = self.mapz( u, v )
        return x, y, z

    def singularmaps( self ):
        return self.mapx, self.mapy, self.mapz

    def grad_realtomap( self ):
        surf_gradhvtoxyz_tuple = self.mapdxdu, self.mapdxdv, self.mapdydu, \
                                self.mapdydv, self.mapdzdu, self.mapdzdv
        return surf_gradhvtoxyz_tuple


    def calc_max_distance_with_grad( self, data_x, data_y, data_z, \
                                                    u_array, v_array ):
        deltau = min( abs(u_array[i]-u_array[i+1]) \
                        for i in range(len(u_array)-1))
        deltav = min( abs(v_array[i]-v_array[i+1]) \
                        for i in range(len(v_array)-1))
        mydelta = min( deltau, deltav )
        maximal_error = 0.1

        max_divgrad_hv = 0
        for data in ( data_x, data_y, data_z ):
            grad1, grad2 = np.gradient( data )
            for grad in (grad2, grad2):
                divgrad1, divgrad2 = np.gradient( grad )
                for i in itertools.chain( *divgrad1, *divgrad2 ):
                    max_divgrad_hv = max( max_divgrad_hv, np.abs( i ) )

        return np.sqrt( maximal_error/max_divgrad_hv )*mydelta

        
    def grad_maxdistance( self ):
        return self.maxdistance


    def pos( self, u, v ):
        x = self.mapx( u, v )
        y = self.mapy( u, v )
        z = self.mapz( u, v )
        return x, y, z
    def pos_array( self, u, v ):
        return np.array( self.pos(u,v) )

    def grad( self, u, v ):
        dxdu = self.mapdxdu( u, v )
        dxdv = self.mapdxdv( u, v )
        dydu = self.mapdydu( u, v )
        dydv = self.mapdydv( u, v )
        dzdu = self.mapdzdu( u, v )
        dzdv = self.mapdzdv( u, v )
        return dxdu, dxdv, dydu, dydv, dzdu, dzdv
    def grad_array( self, u, v ):
        dxdu, dxdv, dydu, dydv, dzdu, dzdv = self.grad_array( u, v )
        return np.array(((dxdu, dxdv),(dydu, dydv),(dzdu,dzdv)))

    def _calc_grads( self, xyz, ulength, vlength ):
        x = xyz[:,:,0]
        y = xyz[:,:,1]
        z = xyz[:,:,2]
        ulength = ulength * -0.01
        vlength = vlength * -0.01

        Dx = np.gradient( x )
        Dy = np.gradient( y )
        Dz = np.gradient( z )
        dxdu, dxdv = Dx[0]*ulength, Dx[1]*vlength
        dydu, dydv = Dy[0]*ulength, Dy[1]*vlength
        dzdu, dzdv = Dz[0]*ulength, Dz[1]*vlength
        return dxdu, dxdv, dydu, dydv, dzdu, dzdv


def generate_surfaceinterpolator( vertexpositions, st_coordinates ):
    delaunay_triang = Delaunay( st_coordinates )
    xyz_as_uvmap = LinearNDInterpolator( delaunay_triang, vertexpositions)
    return xyz_as_uvmap



def create_mapping_device_fromgrid( u_array, v_array, curveddata_z ):
    if any( u_array[i] > u_array[i+1] for i in range(len(u_array)-1) ) \
            and any( v_array[i] > v_array[i+1] for i in range(len(v_array)-1)):
        raise Exception( "metrix-array u and v must be increasing monotonously")
    umin, umax = u_array[0], u_array[-1]
    vmin, vmax = v_array[0], v_array[-1]
    ulength = len( u_array )
    vlength = len( v_array )
    urange, vrange = umax-umin, vmax-vmin
    delta_per_row = vrange+1

    zused = extend_matrix_right( curveddata_z )
    zused = extend_matrix_down( zused )
    metrix_uv = np.array( v_array)
    metrix_uv.resize((1,len(v_array)+1))
    metrix_uv[0][-1] = metrix_uv[0][-2] + 0.9
    metrix_uv = metrix_uv * np.ones((len(u_array)+1,1))
    for i in range( len(metrix_uv)):
        metrix_uv[i] += i*delta_per_row

    ss = metrix_uv.size
    metrix_uv = np.array( metrix_uv ).reshape( ss )
    zused = np.array( zused ).reshape( ss )

    
    def griddata_z( posu, posv ):
        posu = np.interp( posu, u_array, np.arange( ulength ))
        factor = np.remainder( posu, 1 )
        s_lower = posv + delta_per_row*(posu - factor)
        s_higher = s_lower + delta_per_row

        z1 = np.interp( s_lower, metrix_uv, zused )
        z2 = np.interp( s_higher, metrix_uv, zused )
        z = factor * (z2 - z1) + z1
        return z
    return griddata_z
        
def extend_matrix_down( mymatrix ):
    mymatrix = np.append( mymatrix, mymatrix[:,-1:], 1 )
    return mymatrix

def extend_matrix_right( mymatrix ):
    mymatrix = np.append( mymatrix, mymatrix[-1:,:], 0 )
    return mymatrix


def calculate_uv_position_distanceoptimised( faces, coordinates ,\
                                                up, right, down, left ):
    number_vertices = len( coordinates )
    allrandnodes = set(( *up, *right, *down, *left ))
    notrandnodes = set(range(number_vertices)).difference( allrandnodes )
    #interaction_matrix = lil_matrix((number_vertices + len(notrandnodes), \
    #                                number_vertices + len(notrandnodes)))
    #startpositions_u = lil_matrix((number_vertices + len(notrandnodes),1))
    #startpositions_v = lil_matrix((number_vertices + len(notrandnodes),1))
    interaction_matrix = lil_matrix((number_vertices, \
                                    number_vertices))
    startpositions_u = lil_matrix((number_vertices,1))
    startpositions_v = lil_matrix((number_vertices,1))
    for i, u in enumerate( np.linspace(0,1,len(up)) ):
        index = up[i]
        startpositions_u[index] = u
        startpositions_v[index] = 1.0
    for i, v in enumerate( np.linspace(1,0,len(right))):
        index = right[i]
        startpositions_u[index] = 1.0
        startpositions_v[index] = v
    for i, u in enumerate( np.linspace(1,0,len(down))):
        index = down[i]
        startpositions_u[index] = u
        startpositions_v[index] = 0.0
    for i, v in enumerate( np.linspace(0,1,len(left))):
        index = left[i]
        startpositions_u[index] = 0.0
        startpositions_v[index] = v

    tmp = ( face_to_edges(single) for single in faces )
    alledges = itertools.chain( *tmp )
    alledges = set([ frozenset(edge) for edge in alledges ])

    distance = lambda i,j: norm( np.array( coordinates[i]) \
                                            - np.array(coordinates[j]) )
    map_dist_dict = dict()
    for jkl in range(3):
        interaction_matrix = generate_interaction_matrix( number_vertices, \
                                            distance, alledges, map_dist_dict,\
                                            up, right, down, left)
        u_positions = spsolve( interaction_matrix, startpositions_u )
        v_positions = spsolve( interaction_matrix, startpositions_v )

        for i,j in alledges:
            map_dist_dict[ frozenset((i,j)) ] \
                    = norm((u_positions[i]-u_positions[j], \
                            v_positions[i]-v_positions[j]))

        uv_positions = list( itertools.zip_longest( u_positions, v_positions ))

        uv_to_xyz = generate_surfaceinterpolator( coordinates, uv_positions )
        ulength, vlength = 2**5, 2**5
        xyzuv_matrix = generate_surfacemap( uv_to_xyz, ulength, vlength )
        direction = generate_gradient_of_surfacemap( xyzuv_matrix )

    return uv_positions

def face_to_edges( face ):
    tmp = list( face )
    tmp.append(tmp[0])
    edges = list( itertools.zip_longest( tmp[0:-1], tmp[1:] ) )
    return edges


def generate_interaction_matrix( number_vertices, distance, \
                                                alledges, map_dist_dict,\
                                                up, right, down, left ):
    interaction_matrix = lil_matrix((number_vertices, number_vertices))
    for i, j in alledges:
        d = distance( i, j )
        mapdistance = map_dist_dict.get( frozenset((i,j)), 1 )
        interaction_matrix[i,i] -= d*mapdistance
        interaction_matrix[j,j] -= d*mapdistance
        interaction_matrix[i,j] += d*mapdistance
        interaction_matrix[j,i] += d*mapdistance
    for i in itertools.chain( up, right, down, left ):
        interaction_matrix[i,:] = 0
        interaction_matrix[i,i] = 1
    return csc_matrix( interaction_matrix )


def generate_surfacemap( uv_to_xyz, ulength, vlength ):
    xyzuv_matrix = []
    for i, u in enumerate(np.linspace( 0, 1, ulength )):
        nextline = list()
        xyzuv_matrix.append( nextline )
        for j, v in enumerate( np.linspace( 0, 1, vlength )):
            nextline.append( [ *uv_to_xyz( u,v ), i, j ] )
    return xyzuv_matrix


def generate_gradient_of_surfacemap( xyzuv_matrix ):
    mymatrix = np.array( xyzuv_matrix )
    x = mymatrix[:,:,0]
    y = mymatrix[:,:,1]
    z = mymatrix[:,:,2]
    x_uv_grad = np.gradient( x )
    y_uv_grad = np.gradient( y )
    z_uv_grad = np.gradient( z )
    
    x_u_uv_laplace = np.gradient( x_uv_grad[0] )
    x_v_uv_laplace = np.gradient( x_uv_grad[1] )
    y_u_uv_laplace = np.gradient( y_uv_grad[0] )
    y_v_uv_laplace = np.gradient( y_uv_grad[1] )
    z_u_uv_laplace = np.gradient( z_uv_grad[0] )
    z_v_uv_laplace = np.gradient( z_uv_grad[1] )

    x_u_u_uv_grad3 = np.gradient( x_u_uv_laplace[0] )
    x_u_v_uv_grad3 = np.gradient( x_u_uv_laplace[1] )
    x_v_u_uv_grad3 = np.gradient( x_v_uv_laplace[0] )
    x_v_v_uv_grad3 = np.gradient( x_v_uv_laplace[1] )
    y_u_u_uv_grad3 = np.gradient( y_u_uv_laplace[0] )
    y_u_v_uv_grad3 = np.gradient( y_u_uv_laplace[1] )
    y_v_u_uv_grad3 = np.gradient( y_v_uv_laplace[0] )
    y_v_v_uv_grad3 = np.gradient( y_v_uv_laplace[1] )
    z_u_u_uv_grad3 = np.gradient( z_u_uv_laplace[0] )
    z_u_v_uv_grad3 = np.gradient( z_u_uv_laplace[1] )
    z_v_u_uv_grad3 = np.gradient( z_v_uv_laplace[0] )
    z_v_v_uv_grad3 = np.gradient( z_v_uv_laplace[1] )

    direction = get_relax_direction( [ \
                            *x_u_v_uv_grad3, *x_v_u_uv_grad3, \
                            *y_u_v_uv_grad3, *y_v_u_uv_grad3, \
                            *z_u_v_uv_grad3, *z_v_u_uv_grad3 \
                            ] )
    return direction



def get_relax_direction( myarray ):
    for single in myarray:
        singlegrad = np.gradient( single )
        mynorm = single / (singlegrad[0]**2 + singlegrad[1]**2)
        try:
            u += singlegrad[0] * mynorm
            v += singlegrad[1] * mynorm
        except NameError:
            u = singlegrad[0] * mynorm
            v = singlegrad[1] * mynorm
    u /= -len(myarray)
    v /= -len(myarray)
    return u, v
    

