from pymesh import load_mesh as fileload_mesh
import pymesh
#import numba
import numpy as np
from .randrectangle import randrectangle_points
import somoclu
from .somoclu_extension import boundary_train_som
import hashlib

import pathlib

from pathlib import Path
import json
import os
import itertools

LOADMESH_ISEDGE_ATTRIBUTENAME = "vertex_isedge"

class surfacemap():
    def __init__( self, xyshape, pos_array, data_x, data_y, data_z, \
                                            numba_support = False ):
        """
        :todo: xyshape is not the shape of data_i; its xyshape[i]+1, ...
        """
        if numba_support:
            raise Exception("numba currently not supported")
        self.range_x = [0, xyshape[0]]
        self.range_y = [0, xyshape[1]]
        self.pos_array = pos_array
        self.data_x, self.data_y, self.data_z = data_x, data_y, data_z


        griddata_x = np.array(data_x).reshape((xyshape[1]+1, xyshape[0]+1))
        griddata_y = np.array(data_y).reshape((xyshape[1]+1, xyshape[0]+1))
        griddata_z = np.array(data_z).reshape((xyshape[1]+1, xyshape[0]+1))

        self.surfacemap_x, self.surfacemap_y, self.surfacemap_z = \
                self.create_surfacemaps_from_data( xyshape, pos_array, \
                                            griddata_x, griddata_y, griddata_z,\
                                            numba_support)

        self.surfacemap_gradhx, self.surfacemap_gradhy, self.surfacemap_gradhz,\
                self.surfacemap_gradvx, self.surfacemap_gradvy,\
                self.surfacemap_gradvz \
                = self.create_gradient_tensors_from_griddata( \
                                    xyshape, pos_array, 
                                    griddata_x, griddata_y, griddata_z)
        self.maxdistance = self.calc_max_distance_with_grad(  \
                                        griddata_x, griddata_y, griddata_z )

    def grad_maxdistance( self ):
        return self.maxdistance

    def calc_max_distance_with_grad( self, data_x, data_y, data_z ):
        maximal_error = 0.1

        max_divgrad_hv = 0
        for data in ( data_x, data_y, data_z ):
            grad1, grad2 = np.gradient( data )
            for grad in (grad2, grad2):
                divgrad1, divgrad2 = np.gradient( grad )
                for i in itertools.chain( *divgrad1, *divgrad2 ):
                    max_divgrad_hv = max( max_divgrad_hv, np.abs( i ) )
        
        return np.sqrt( maximal_error/max_divgrad_hv )

    def create_gradient_tensors_from_griddata( self, xyshape, pos_array, \
                                        data_x, data_y, data_z):
        """
        Those tensors meant to translate a movement in xyz space to
        map space.
        map position willl be v and h
        horizontal(h) means in one row, row[0][0] to row[0][1]
        vertical(v) means translation between rows, row[0][0] to row[1][0]
        :todo: rechnung aufstellen fuer berechnung von gradient v(x,y,z)
        :todo: compact via function also fo rthe other method
        """
        grad_xv, grad_xh = np.gradient( data_x )
        grad_yv, grad_yh = np.gradient( data_y )
        grad_zv, grad_zh = np.gradient( data_z )
        
        maxx, maxy = xyshape[0], xyshape[1]
        curveposition = np.concatenate(( pos_array,\
                                        pos_array[-(maxx+2):-1]))

        # also calculates the surfacenormal (nx, ny, nz)
        grad_hx, grad_hy, grad_hz, grad_vx, grad_vy, grad_vz, nx, ny, nz \
                        = pseudoinvert_matrix_grad_xyz_ab( \
                                        grad_xh, grad_yh, grad_zh, \
                                        grad_xv, grad_yv, grad_zv, \
                                        )
        grad_hx = extend_matrix_right( grad_hx )
        grad_hy = extend_matrix_right( grad_hy )
        grad_hz = extend_matrix_right( grad_hz )
        grad_vx = extend_matrix_right( grad_vx )
        grad_vy = extend_matrix_right( grad_vy )
        grad_vz = extend_matrix_right( grad_vz )

        # grid to array
        #ss = curveposition.size
        #grad_hx = np.array( grad_hx ).reshape((ss))
        #grad_hy = np.array( grad_hy ).reshape((ss))
        #grad_hz = np.array( grad_hz ).reshape((ss))
        #grad_vx = np.array( grad_vx ).reshape((ss))
        #grad_vy = np.array( grad_vy ).reshape((ss))
        #grad_vz = np.array( grad_vz ).reshape((ss))
        #curveposition = curveposition.reshape((ss))

        griddata_gradhx = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_hx )
        griddata_gradhy = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_hy )
        griddata_gradhz = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_hz )
        griddata_gradvx = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_vx )
        griddata_gradvy = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_vy )
        griddata_gradvz = self.create_mapping_device_fromgrid( curveposition, \
                                                            grad_vz )
        return griddata_gradhx, griddata_gradhy, griddata_gradhz, \
                    griddata_gradvx, griddata_gradvy, griddata_gradvz

    def create_surfacemaps_from_data( self, xyshape, pos_array, data_x, data_y,\
                                                        data_z, numba_support):
        """
        :todo: maxx and maxy to maxv and maxh, map dimensions are v,h instead
                of x and y
        """
        maxx, maxy = xyshape[0], xyshape[1]

        # add to every data grid an aditional line (copy of last line)
        curveposition = np.concatenate(( pos_array,\
                                        pos_array[-(maxx+2):-1]))
        #curveddata_x = np.concatenate(( data_x, data_x[-(maxx+2):-1] ))
        #curveddata_y = np.concatenate(( data_y, data_y[-(maxx+2):-1] ))
        #curveddata_z = np.concatenate(( data_z, data_z[-(maxx+2):-1] ))

        #curveddata_x = np.array(data_x).reshape( (xyshape[1]+1,xyshape[0]+1) )
        curveddata_x = extend_matrix_right( data_x )
        curveddata_y = extend_matrix_right( data_y )
        curveddata_z = extend_matrix_right( data_z )

        # grid to array
        #ss = curveposition.size
        #curveposition = np.array( curveposition ).reshape((ss))
        #curveddata_x, curveddata_y, curveddata_z = \
        #        np.array(curveddata_x).reshape((ss)), \
        #        np.array(curveddata_y).reshape((ss)), \
        #        np.array(curveddata_z).reshape((ss))

        surfacemap_x = self.create_mapping_device_fromgrid( curveposition, \
                                                            curveddata_x )
        surfacemap_y = self.create_mapping_device_fromgrid( curveposition, \
                                                            curveddata_y )
        surfacemap_z = self.create_mapping_device_fromgrid( curveposition, \
                                                            curveddata_z )
        return surfacemap_x, surfacemap_y, surfacemap_z
        #if numba_support == True:
        #    griddata_x = numba.njit( griddata_x )
        #    griddata_y = numba.njit( griddata_y )
        #    griddata_z = numba.njit( griddata_z )
        return griddata_x, griddata_y, griddata_z

    def create_mapping_device_fromgrid( self, curveposition, curveddata_z):
        ss = curveposition.size
        maxx = curveddata_z.shape[1] - 1
        maxh = curveddata_z.shape[0] - 2
        curveposition = np.array( curveposition ).reshape((ss))
        curveddata_z = np.array(curveddata_z).reshape((ss))
        return self.create_mapping_device( maxx, maxh, \
                                            curveposition, curveddata_z )

    def create_mapping_device( self, maxx,maxh, curveposition, curveddata_z ):
        def griddata_z( posv, posh ):
            #posv = min( max( 0.0, posv),maxx)
            #posh = min( max( 0.0, posh),maxh)
            #if posh > maxh:
            #    print( posh, maxh, maxx )
            #if posv > maxx:
            #    print( posv, maxx, maxh )

            factor = np.remainder( posh, 1 )
            s_lower = posv + (maxx+1)*(posh - factor)
            s_higher = s_lower + (maxx+1)

            z1 = np.interp( s_lower, curveposition, curveddata_z )
            z2 = np.interp( s_higher, curveposition, curveddata_z )
            z = factor * (z2 - z1) + z1
            return z
        return griddata_z

    def singularmaps( self ):
        return self.surfacemap_x, self.surfacemap_y, self.surfacemap_z

    def grad_realtomap( self ):
        return self.surfacemap_gradhx, self.surfacemap_gradhy, \
                self.surfacemap_gradhz, \
                self.surfacemap_gradvx, self.surfacemap_gradvy, \
                self.surfacemap_gradvz

    def xmin( self ):
        return self.range_x[0]
    def ymin( self ):
        return self.range_y[0]
    def xmax( self ):
        return self.range_x[1]
    def ymax( self ):
        return self.range_y[1]

    def __call__( self, x, y ):
        xreal = self.surfacemap_x( x, y )
        yreal = self.surfacemap_y( x, y )
        zreal = self.surfacemap_z( x, y )
        return xreal, yreal, zreal

def get_surfacemap( filename, numba_support=False, force_new=False ):
    """
    this generates a 2d mapping of a surface retrieved from the file filename
    :param force_new: tries to retrieve an existing surfacemap to file
    :rtype map: converts 2d to 3d
    """
    if not force_new:
        returnsurfacemap = check_for_existing_surfacemap( filename, \
                                                numba_support = numba_support )
        if None != returnsurfacemap:
            return returnsurfacemap

    mesh, edges = load_mesh( filename, lengthfactor=1.5 )
    #mesh_border = load_rand( mesh, edges )
    mesh_border = randrectangle_points(edges[0], edges[1], edges[2], edges[3], \
                                mesh, None)
    som = train_kohonenmap( mesh, mesh_border )



    xyshape, pos_array, data_x, data_y, data_z = create_surfacemap_data( som )
    # it replaces this function
    #surfacemap_x, surfacemap_y, surfacemap_z, range_x, range_y = \
    #        create_gridinterpolator_fromsom( som, numba_support )
    #returnsurfacemap =  surfacemap( surfacemap_x, surfacemap_y, surfacemap_z,\
    #                                range_x, range_y)

    returnsurfacemap = surfacemap( xyshape, pos_array, data_x, data_y, data_z )
    save_surfacemap_in_file( returnsurfacemap, filename )
    return returnsurfacemap

def filepath_to_cachepath( filename ):
    """
    :type filename: str or pathlib.Path
    """
    filename = converttostring( filename )
    hashval = hashlib.sha1( filename.encode("utf-8") ).hexdigest()
    return Path( "__pycache__/" + str(hashval) + ".surfacemap" )

def check_for_existing_surfacemap( filename, numba_support=True ):
    filename = converttostring( filename )
    cache_filepath = filepath_to_cachepath( filename )
    if Path(cache_filepath).is_file():
        surfacefile = open( cache_filepath, 'r' )
        mysurfacemap = surfacemap( *json.loads( surfacefile.read() ),
                                numba_support = numba_support )

        surfacefile.close()
        return mysurfacemap
    return None

class _mynumpydecoder( json.JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, np.int_ ):
            return int( obj )
        elif isinstance( obj, np.ndarray ):
            return obj.tolist()
        elif isinstance( obj, np.matrix ):
            return obj.tolist()
        else:
            return json.JSONEncoder.default( self, obj )

def save_surfacemap_in_file( mysurfacemap, meshfilename ):
    surfacemap_filepath = filepath_to_cachepath( meshfilename )

    surfacefile = open( surfacemap_filepath, 'w' )
    try:
        dumpling = [ [mysurfacemap.range_x[1], mysurfacemap.range_y[1]],\
                mysurfacemap.pos_array, mysurfacemap.data_x, \
                mysurfacemap.data_y, mysurfacemap.data_z]
        surfacefile.write( json.dumps( dumpling, cls=_mynumpydecoder ) )
    except:
        surfacefile.close()
        os.remove( surfacemap_filepath )
        raise
    surfacefile.close()

def create_gridinterpolator_fromsom( som, numba_support ):
    """
    :todo: this will be replaced by create_surfacemap_data
    """
    shape = som.codebook.shape
    xsize = shape[0]
    ysize = shape[1]

    tmpgrid = np.array(np.meshgrid( range(shape[1]), range(shape[0])))
    somgrid = np.hstack((tmpgrid[0].reshape((tmpgrid[0].size,1)),
                            tmpgrid[1].reshape((tmpgrid[1].size,1))))
    codebookshape = (len(somgrid),3)
    datapoints = som.codebook.reshape(codebookshape)

    surfacemap_x, surfacemap_y, surfacemap_z = \
                    create_gridinterpolator(\
                            somgrid, xsize, ysize, datapoints, numba_support \
                            )
    return surfacemap_x, surfacemap_y, surfacemap_z, (0,xsize), (0,ysize)

def create_surfacemap_data( som ):
    shape = som.codebook.shape
    xsize = shape[0]
    ysize = shape[1]

    tmpgrid = np.array(np.meshgrid( range(shape[1]), range(shape[0])))
    somgrid = np.hstack((tmpgrid[0].reshape((tmpgrid[0].size,1)),
                            tmpgrid[1].reshape((tmpgrid[1].size,1))))
    codebookshape = (len(somgrid),3)
    datapoints = som.codebook.reshape(codebookshape)

    xyshape, pos_array, data_x, data_y, data_z = create_arraysformapping( \
                                            somgrid, xsize, ysize, datapoints)
    return xyshape, pos_array, data_x, data_y, data_z
    surfacemap_x, surfacemap_y, surfacemap_z = \
                    create_gridinterpolator(\
                            somgrid, xsize, ysize, datapoints, numba_support \
                            )
    return surfacemap_x, surfacemap_y, surfacemap_z, (0,xsize), (0,ysize)

def load_mesh( file_name, lengthfactor=0.1 ):
    """
    uses wavefront-file for meshloading
    :type file_name: path or file-like
    :return: return a mesh with edgelength is maximal the distance between
        the vertices in the loaded mesh
    """
    mesh, dump, minimaldistance = None, None, None

    file_name = converttostring( file_name )
    mesh_original = fileload_mesh( file_name )

    edges = extract_edges( mesh_original )

    minimaldistance = findminimaldistance( mesh_original.vertices )
    max_length = lengthfactor * minimaldistance
    mesh, dump = pymesh.split_long_edges( mesh_original, max_length )

    return mesh, edges

def _conv_pathtostr( path ):
    return path.name
def _conv_iobufferedreadertostr( reader ):
    return reader.name
def _conv_strtostr( mystring ):
    return mystring
from _io import BufferedReader
_convertlib = {
        Path:_conv_pathtostr,
        BufferedReader:_conv_iobufferedreadertostr,
        str:_conv_strtostr,
        }
def converttostring( filename ):
    return _convertlib[ type(filename) ](filename)

def extend_matrix_down( mymatrix ):
    #mymatrix = np.append( mymatrix, mymatrix[-1:,:], 0 )
    mymatrix = np.append( mymatrix, mymatrix[:,-1:], 1 )
    return mymatrix

def extend_matrix_right( mymatrix ):
    mymatrix = np.append( mymatrix, mymatrix[-1:,:], 0 )
    #mymatrix = np.append( mymatrix, mymatrix[:,-1:], 1 )
    return mymatrix


def extract_edges( mesh ):
    isedge_data = mesh.get_vertex_attribute( LOADMESH_ISEDGE_ATTRIBUTENAME )
    edges = [-1,-1,-1,-1]
    for i in range( len(isedge_data)):
        if isedge_data[i] == 1:
            edges[0] = i
        elif isedge_data[i] == 2:
            edges[1] = i
        elif isedge_data[i] == 3:
            edges[2] = i
        elif isedge_data[i] == 4:
            edges[3] = i
    if -1 in edges:
        raise Exception("not all four edges found in mesh.ply")
    return edges



def findminimaldistance( vertices ):
    """
    :param vertices:    list of all vertices
    :type vertices: list with type(list[*])=point
    :type point:    type(point)=numpy.array-like; len(point)=3
    :param return:  return minimal distance between any vertices
    """
    tmpdistance = None
    tmpvertices = []
    for tmpvertice in vertices:
        tmpvertices.append( np.array(tmpvertice) )

    tmpminimaldistance = np.linalg.norm( tmpvertices[0]-tmpvertices[1] )
    for i in range(len(tmpvertices)):
        for ii in range(0,i):
            tmpdistance = np.linalg.norm( tmpvertices[i]-tmpvertices[ii] )
            tmpminimaldistance = min( tmpminimaldistance, tmpdistance )
        for ii in range(i+1,len(tmpvertices)):
            tmpdistance = np.linalg.norm( tmpvertices[i]-tmpvertices[ii] )
            tmpminimaldistance = min( tmpminimaldistance, tmpdistance )
    return tmpminimaldistance

def create_arraysformapping( grid, xsize, ysize, gridvalues ):
    """
    :param grid: grid is an array of 2d points example [[0,0],[1,0]] 
            it has to have a meshgrid form
    """
    maxx, maxy = grid[-1] #the last point has both values to max
    #curveposition = np.zeros( (xsize*(ysize+1), ))
    #curveposition = np.array(grid)*np.matrix((1,maxx+1)).T
    #curveddata_x = np.array(gridvalues)*np.matrix((1,0,0)).T
    #curveddata_y = np.array(gridvalues)*np.matrix((0,1,0)).T
    #curveddata_z = np.array(gridvalues)*np.matrix((0,0,1)).T
    curveposition = np.array((1,maxx+1)).dot(np.array(grid).T)
    curveposition = curveposition.reshape((len(curveposition),1))
    curveddata_x = np.array((1,0,0)).dot( np.array(gridvalues).T )
    curveddata_y = np.array((0,1,0)).dot( np.array(gridvalues).T )
    curveddata_z = np.array((0,0,1)).dot( np.array(gridvalues).T )

    return [maxx, maxy], curveposition, curveddata_x, curveddata_y, curveddata_z

def create_gridinterpolator( grid, xsize, ysize, gridvalues, \
                            numba_support=True ):
    """
    :todo: this is obsolete together with create_gridinterpiolator_fromsom
    :param grid: grid is an array of 2d points example [[0,0],[1,0]] 
            it has to have a meshgrid form
    """
    maxx, maxy = grid[-1] #the last point has both values to max
    #curveposition = np.zeros( (xsize*(ysize+1), ))
    curveposition = np.array((1,maxx+1)).dot(np.array(grid).T)
    curveposition = curveposition.reshape((len(curveposition),1))
    curveddata_x = np.array((1,0,0)).dot( np.array(gridvalues).T )
    curveddata_y = np.array((0,1,0)).dot( np.array(gridvalues).T )
    curveddata_z = np.array((0,0,1)).dot( np.array(gridvalues).T )
    curveposition = np.concatenate((curveposition,curveposition[-(maxx+2):-1]))
    curveddata_x = np.concatenate((curveddata_x,curveddata_x[-(maxx+2):-1]))
    curveddata_y = np.concatenate((curveddata_y,curveddata_y[-(maxx+2):-1]))
    curveddata_z = np.concatenate((curveddata_z,curveddata_z[-(maxx+2):-1]))
    ss = curveposition.size
    curveposition, curveddata_x, curveddata_y, curveddata_z = \
            np.array(curveposition).reshape((ss)),\
            np.array(curveddata_x).reshape((ss)), \
            np.array(curveddata_y).reshape((ss)), \
            np.array(curveddata_z).reshape((ss))

    def griddata_x( posx, posy ):
        factor = np.remainder( posy, 1 )
        s_lower = posx + (maxx+1)*(posy - factor)
        s_higher = s_lower + (maxx+1)

        x1 = np.interp( s_lower, curveposition, curveddata_x )
        x2 = np.interp( s_higher, curveposition, curveddata_x )
        x = factor * (x2 - x1) + x1
        return x
    def griddata_y( posx, posy ):
        factor = np.remainder( posy, 1 )
        s_lower = posx + (maxx+1)*(posy - factor)
        s_higher = s_lower + (maxx+1)

        y1 = np.interp( s_lower, curveposition, curveddata_y )
        y2 = np.interp( s_higher, curveposition, curveddata_y )
        y = factor * (y2 - y1) + y1
        return y
    def griddata_z( posx, posy ):
        factor = np.remainder( posy, 1 )
        s_lower = posx + (maxx+1)*(posy - factor)
        s_higher = s_lower + (maxx+1)

        z1 = np.interp( s_lower, curveposition, curveddata_z )
        z2 = np.interp( s_higher, curveposition, curveddata_z )
        z = factor * (z2 - z1) + z1
        return z
    #if numba_support == True:
    #    griddata_x = numba.njit( griddata_x )
    #    griddata_y = numba.njit( griddata_y )
    #    griddata_z = numba.njit( griddata_z )
    return griddata_x, griddata_y, griddata_z

def train_kohonenmap( mesh, rand, n_columns=121, n_rows=101 ):
    #data = np.matrix( mesh.vertices )
    data = np.array( mesh.vertices )
    som = somoclu.Somoclu( n_columns, n_rows, compactsupport=True )
    boundary_train_som( som, data,  \
            mesh.vertices[rand.up], mesh.vertices[rand.down], \
            mesh.vertices[rand.left], mesh.vertices[rand.right], \
            rand.updist, rand.downdist, rand.leftdist, rand.rightdist,\
            radius0=100, epochs=10, extrarand=8)
    return som


def pseudoinvert_matrix_grad_xyz_ab( grad_xh, grad_yh, grad_zh, \
                                        grad_xv, grad_yv, grad_zv ):
    oldshape = grad_xh.shape
    grad_hx, grad_hy, grad_hz \
            = np.zeros( oldshape ), np.zeros( oldshape ), np.zeros( oldshape )
    grad_vx, grad_vy, grad_vz \
            = np.zeros( oldshape ), np.zeros( oldshape ), np.zeros( oldshape )
    nx, ny, nz \
            = np.zeros( oldshape ), np.zeros( oldshape ), np.zeros( oldshape )
    for a, b in itertools.product( range(oldshape[0]), range(oldshape[1])):
        matrix = ((grad_xv[a][b], grad_xh[a][b]), \
                    (grad_yv[a][b], grad_yh[a][b]), \
                    ( grad_zv[a][b],grad_zh[a][b]))
        tmp = np.linalg.pinv( matrix )
        grad_hx[a][b], grad_hy[a][b], grad_hz[a][b] = tmp[0]
        grad_vx[a][b], grad_vy[a][b], grad_vz[a][b] = tmp[1]
        tmpvector = np.cross( tmp[0], tmp[1] )
        nx[a][b], ny[a][b], nz[a][b] = tmpvector / np.linalg.norm( tmpvector )
    return grad_hx, grad_hy, grad_hz, grad_vx, grad_vy, grad_vz, nx, ny, nz
