import numpy as np
from scipy.ndimage import filters

def relax_with_numpy( uv_to_xyz, u_array, v_array ):
    from .create_surfacemap import create_surfacemap
    surfmap = create_surfacemap( uv_to_xyz, len( u_array ) , len(v_array) )
    raise Exception()
    mapdxdu, mapdxdv, mapdydu, mapdydv, mapdzdu, mapdzdv \
            = surfmap.grad_realtomap()
    def surfmap_grad( u, v ):
        return np.array((\
                ( mapdxdu( u, v ), mapdxdv(u,v)), \
                ( mapdydu( u, v ), mapdydv(u,v)), \
                ( mapdzdu( u, v ), mapdzdv(u,v)), \
                ))

    uv_grid = np.ndarray((len(u_array),len( v_array), 2))
    for i, u in enumerate( u_array ):
        for j, v in enumerate( v_array ):
            uv_grid[i,j] = (u, v)

    #print( uv_grid[0:3,0:3,1], "\n" )
    #for i in range( 100 ):
    #    uv_grid = cycle( uv_grid, surfmap, surfmap_grad )
    #maximal_distance_to_goal, testlength = 1e-1, 20
    maximal_distance_to_goal, testlength = 1e-3, 20
    uv_grid = relax_till( uv_grid, surfmap, surfmap_grad, \
                                maximal_distance_to_goal, testlength )
    #print( uv_grid[0:3,0:3,1] )
    pos_array = get_xyz_grid( uv_grid, surfmap, surfmap_grad )
    return uv_grid[:,:,0], uv_grid[:,:,1], \
            pos_array[:,:,0], pos_array[:,:,1], pos_array[:,:,2]
    return uv_grid, pos_array
            

def relax_till( uv_grid, surfmap, surfmap_grad, maximal_distance_to_goal, \
                                        testlength, accuracy=0.1 ):
    distance_to_goal = np.infty
    testarray = np.array([np.infty]*testlength)
    i = 0
    def insert_datapoint( datapoint, i ):
        testarray[i] = datapoint
        return (i+1) % testlength
    #def calc_distance_to_goal():
    def calc_expected_value_with_accuracy():
        erwartungswert = np.mean( testarray )
        stichprobenvarianz = np.mean(tuple( np.square( single-erwartungswert ) \
                                    for single in testarray ))
        if stichprobenvarianz < abs( erwartungswert*accuracy ):
            return erwartungswert
        else:
            return np.infty
    myshape = uv_grid.shape
    ssize = uv_grid.size
    array_shape = ( myshape[0]*myshape[1], myshape[2] )

    np.seterr( divide='ignore' ) #ignore zero divisions
    olddifference = np.array( 0 )
    middle_difference = np.array( 0 )
    while distance_to_goal > maximal_distance_to_goal:
        uv_grid, delta_grid = cycle( uv_grid, surfmap, surfmap_grad )
        newdifference = np.array( max( np.linalg.norm( single ) \
                            for single in delta_grid.reshape( array_shape ) ))

        datapoint = newdifference / olddifference
        i = insert_datapoint( datapoint, i )
        olddifference = newdifference

        expected_quotient = calc_expected_value_with_accuracy()

        middle_difference = (middle_difference + newdifference)/2
        if expected_quotient < 1.0:
            distance_to_goal = middle_difference / (1-expected_quotient)
        else:
            distance_to_goal = np.infty
        #print( "%10.3e, %10.3e, %10.3e, %10.3e" % (distance_to_goal, expected_quotient, middle_difference, newdifference ))
    np.seterr( divide='warn' )
    return uv_grid

    


def cycle( uv_grid, surfmap, surfmap_grad ):
    il, jl, tmp = uv_grid.shape
    pos_array = get_xyz_grid( uv_grid, surfmap, surfmap_grad )
    Dx = filters.laplace( pos_array[:,:,0] )
    Dy = filters.laplace( pos_array[:,:,1] )
    Dz = filters.laplace( pos_array[:,:,2] )
    delta_uv = np.zeros((il, jl, 2))
    for i in range(1, il-1 ):
        for j in range(1, jl-1 ):
            Duv_Dxyz = surfmap_grad( *uv_grid[i,j] ).T
            Dxyz = (Dx[i,j], Dy[i,j], Dz[i,j] )
            delta_uv[ i, j ] = Duv_Dxyz.dot( Dxyz )
    return uv_grid - delta_uv, delta_uv

def get_xyz_grid( uv_grid, surfmap, surfmap_grad ):
    il, jl, tmp = uv_grid.shape
    pos_array = np.ndarray((il, jl, 3))
    for i in range(il):
        for j in range(jl):
            pos_array[i,j] = surfmap( *uv_grid[ i, j ] )
    return pos_array
