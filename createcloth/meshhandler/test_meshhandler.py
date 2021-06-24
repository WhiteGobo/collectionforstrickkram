import unittest
from .create_surfacemap import get_surfacemap
from ..strickgraph.load_stitchinfo import myasd as stinfo
from .create_surfacemap import load_mesh
from .main import relax_strickgraph_on_surface
import pkg_resources
import importlib.resources
from . import test_src
import os.path
from .gridrelaxator import gridrelaxator

#import sys
#sys.path.append("../strickgraph/")
from ..strickgraph import strickgraph_fromgrid as fromgrid
import networkx as netx

import numpy as np


import tempfile
from .surface_container import surface, \
                        surfacemap

class TestMeshhandlerMethods( unittest.TestCase ):
    def setUp( self ):
        self.testmeshfilename = "meshfortests.ply"
        #self.testmeshfile = "meshfortests.ply"
        pass

    def test_createsurfacemap( self ):
        return
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            mysurface = surface.from_plyfile( filepath )
        mysurfacemap = surfacemap.from_surface( mysurface )

        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "surfmap.ply" )
            mysurfacemap.to_plyfile( myfilepath )
            copy_surfmap = surfacemap.from_plyfile( myfilepath )


    def test_create_surfacemap( self ):
        with importlib.resources.path( test_src, "tester_surfmap.ply" ) as \
                                                                    filepath:
            mysurface = surfacemap.from_plyfile( filepath )
        (x, y, z) = mysurface.singularmaps()
        self.assertTrue( np.allclose( \
                ( x(0,0), x(1,0), x(1,1), x(0,1), \
                x(.5, .5 ), y(.5, .5 ), z(.5,.5)),\
                (-0.51956, 0.51956, 0.51956, -0.51956, \
                0.00015575, 0.99217575, 0.0002222500000000037),\
                rtol=1e-3))


    def test_wholerelaxing( self ):
        with importlib.resources.path( test_src, "tester_surfmap.ply" ) as \
                                                                    filepath:
            mysurfacemap = surfacemap.from_plyfile( filepath )
        #mygraph = netx.grid_2d_graph( 32,32 )
        #for node in mygraph.nodes:
        #    mygraph.nodes[node]["x"] = mysurfacemap
        #                                   .xyzmatrix[node[0]][node[1]][0]
        #    mygraph.nodes[node]["y"] = mysurfacemap
        #                                    .xyzmatrix[node[0]][node[1]][1]
        #    mygraph.nodes[node]["z"] = mysurfacemap
        #                                    .xyzmatrix[node[0]][node[1]][2]
        #myvis3d( mygraph )
        mygraph = netx.grid_2d_graph( 30,30 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        gridgraph = fromgrid.create_strickgraph_from_gridgraph( mygraph, \
                                                        firstrow, \
                                                        stinfo )


        default_length = 0.1
        border = gridgraph.get_borders()

        no_solution = True
        maximal_error = 1e-6 #this should be caculated
        # maximal error can be estimated with consideration 
        # of strength to movement
        # and maximal Spiel(german) of each node
        while no_solution:
            myrelaxator = gridrelaxator( gridgraph, mysurfacemap, border )
            myrelaxator.relax()

            no_solution = False
        returngraph = myrelaxator.get_positiongrid()
        xdict = netx.get_node_attributes( returngraph, "x" )
        nodes = sorted( set(xdict.keys()).difference(("start", "end")) )
        xpos = [ xdict[n] for n in nodes ]
        #myvis3d( returngraph )
        #print( ",".join("%.3f" %(x) for x in xpos ) )
        try:
            tmpbool = np.allclose( xpos, testdings, atol=0.1 )
            self.assertTrue( tmpbool )
        except AssertionError as err:
            err.args = ( *err.args, "Calculation was totally off" )
            raise err

    def test_relax_strickgraph_withdifferenttypes( self ):
        return
        filename = pkg_resources.resource_stream( __name__, \
                                                        "meshfortests.ply" )
        mygraph = netx.grid_2d_graph( 10,10 )
        firstrow = [ x for x in mygraph.nodes() if x[0] == 0 ]
        asd = fromgrid.create_strickgraph_from_gridgraph( mygraph, firstrow, \
                                                        stinfo )

        datagraph = relax_strickgraph_on_surface( asd, filename, \
                                                        numba_support=False )
        mysurfacemap = get_surfacemap( filename )
        filename.close()

        datagraph = relax_strickgraph_on_surface( asd, mysurfacemap, \
                                                        numba_support=False )

    def test_loadmesh( self ):
        return
        filename = pkg_resources.resource_stream( __name__, \
                                                        "meshfortests.ply" )
        mesh, edges = load_mesh( filename, lengthfactor=1.5 )
        self.assertEqual( tuple( edges), (123, 130, 107, 104) )
        filename.close()


def myvis3d( graph ):
    x = netx.get_node_attributes( graph, "x" )
    y = netx.get_node_attributes( graph, "y" )
    z = netx.get_node_attributes( graph, "z" )
    myarray = []
    for node in x:
        myarray.append( [ x[node], y[node], z[node] ] )
    myarray = np.array( myarray )
    myarray = myarray.T

    edgelist = []
    #length = netx.get_edge_attributes( graph, "tension" )
    length = {}
    for edge in graph.edges():
        a = (x[edge[0]],z[edge[0]],y[edge[0]])
        b = (x[edge[1]],z[edge[1]],y[edge[1]])
        tmp = np.linalg.norm( np.subtract(a, b) )
        length.update({ edge: tmp })
    listlength = [ value for key, value in length.items() ]

    minima, maxima = min( listlength ), max( listlength )
    for tmpedge in length:
        tmpxs = ( x[tmpedge[0]], x[tmpedge[1]] )
        tmpys = ( y[tmpedge[0]], y[tmpedge[1]] )
        tmpzs = ( z[tmpedge[0]], z[tmpedge[1]] )
        edgelist.append((tmpxs, tmpys, tmpzs, length[ tmpedge ]))
        #minima = min( minima, length[ tmpedge ])
        #maxima = max( maxima, length[ tmpedge ])



    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.cm as cm
    import matplotlib.colors as colors
    norm = colors.Normalize( vmin=minima, vmax =maxima, clip=True)
    mapper = cm.ScalarMappable( norm=norm, cmap=cm.coolwarm_r )
    fig = plt.figure()
    ax = fig.add_subplot( 111, projection='3d')
    #ax.scatter( myarray[0], myarray[1], myarray[2] )

    for tmpedge in edgelist:
        ax.plot( tmpedge[0], tmpedge[1], tmpedge[2], \
                        color=mapper.to_rgba(tmpedge[3]) )
    plt.show()



testdings = [-0.520,-0.502,-0.481,-0.438,-0.373,-0.321,-0.301,-0.284,-0.256,-0.221,-0.182,-0.141,-0.098,-0.059,-0.020,0.020,0.059,0.098,0.141,0.182,0.221,0.256,0.284,0.301,0.321,0.373,0.438,0.481,0.502,0.520,-0.575,-0.542,-0.510,-0.467,-0.416,-0.371,-0.337,-0.306,-0.273,-0.235,-0.195,-0.152,-0.108,-0.065,-0.022,0.021,0.065,0.108,0.152,0.195,0.235,0.273,0.306,0.337,0.371,0.416,0.467,0.510,0.544,0.575,-0.630,-0.584,-0.543,-0.500,-0.454,-0.410,-0.370,-0.331,-0.292,-0.251,-0.208,-0.163,-0.117,-0.070,-0.023,0.023,0.070,0.116,0.162,0.207,0.251,0.292,0.331,0.370,0.410,0.454,0.499,0.543,0.584,0.630,-0.678,-0.621,-0.575,-0.530,-0.486,-0.442,-0.399,-0.356,-0.312,-0.268,-0.221,-0.173,-0.125,-0.075,-0.025,0.025,0.075,0.124,0.173,0.221,0.268,0.312,0.356,0.399,0.441,0.485,0.530,0.574,0.621,0.678,-0.692,-0.646,-0.602,-0.559,-0.514,-0.469,-0.424,-0.379,-0.332,-0.284,-0.235,-0.184,-0.133,-0.080,-0.027,0.027,0.080,0.132,0.184,0.235,0.284,0.332,0.378,0.424,0.469,0.513,0.558,0.602,0.646,0.692,-0.704,-0.666,-0.627,-0.586,-0.541,-0.495,-0.448,-0.400,-0.350,-0.300,-0.247,-0.194,-0.139,-0.084,-0.028,0.028,0.084,0.139,0.194,0.247,0.300,0.350,0.400,0.448,0.494,0.540,0.585,0.627,0.666,0.704,-0.719,-0.685,-0.649,-0.609,-0.565,-0.518,-0.470,-0.420,-0.368,-0.315,-0.260,-0.204,-0.146,-0.088,-0.029,0.029,0.088,0.146,0.204,0.260,0.315,0.368,0.420,0.470,0.518,0.565,0.609,0.649,0.686,0.719,-0.744,-0.708,-0.672,-0.631,-0.587,-0.539,-0.490,-0.438,-0.385,-0.329,-0.271,-0.213,-0.153,-0.092,-0.031,0.031,0.092,0.153,0.213,0.271,0.329,0.385,0.438,0.490,0.539,0.587,0.632,0.672,0.710,0.744,-0.770,-0.735,-0.696,-0.654,-0.609,-0.560,-0.509,-0.455,-0.399,-0.342,-0.282,-0.221,-0.159,-0.096,-0.032,0.032,0.096,0.159,0.221,0.282,0.342,0.399,0.455,0.509,0.560,0.609,0.655,0.697,0.735,0.770,-0.794,-0.760,-0.718,-0.676,-0.629,-0.579,-0.526,-0.471,-0.413,-0.353,-0.292,-0.229,-0.164,-0.099,-0.033,0.033,0.099,0.164,0.229,0.292,0.354,0.413,0.471,0.526,0.579,0.629,0.676,0.719,0.760,0.794,-0.817,-0.781,-0.738,-0.694,-0.646,-0.594,-0.541,-0.484,-0.424,-0.363,-0.300,-0.235,-0.169,-0.102,-0.034,0.034,0.102,0.169,0.235,0.300,0.363,0.424,0.483,0.540,0.594,0.646,0.694,0.738,0.781,0.817,-0.839,-0.801,-0.757,-0.711,-0.662,-0.608,-0.553,-0.495,-0.434,-0.372,-0.307,-0.240,-0.173,-0.104,-0.035,0.035,0.104,0.173,0.240,0.307,0.372,0.434,0.495,0.553,0.608,0.662,0.711,0.757,0.801,0.839,-0.854,-0.817,-0.770,-0.723,-0.673,-0.619,-0.563,-0.504,-0.442,-0.379,-0.313,-0.245,-0.176,-0.106,-0.035,0.035,0.106,0.176,0.245,0.312,0.379,0.443,0.505,0.564,0.619,0.673,0.724,0.771,0.816,0.854,-0.863,-0.825,-0.779,-0.731,-0.680,-0.625,-0.569,-0.509,-0.446,-0.382,-0.315,-0.247,-0.178,-0.107,-0.036,0.036,0.107,0.178,0.247,0.316,0.383,0.447,0.509,0.569,0.626,0.680,0.731,0.779,0.825,0.863,-0.870,-0.831,-0.785,-0.737,-0.686,-0.630,-0.573,-0.513,-0.449,-0.385,-0.317,-0.249,-0.179,-0.108,-0.036,0.036,0.108,0.179,0.249,0.318,0.385,0.450,0.512,0.573,0.631,0.686,0.737,0.785,0.832,0.870,-0.870,-0.831,-0.785,-0.737,-0.687,-0.630,-0.573,-0.513,-0.450,-0.385,-0.318,-0.249,-0.179,-0.108,-0.036,0.036,0.108,0.179,0.249,0.318,0.385,0.450,0.513,0.573,0.631,0.687,0.737,0.785,0.831,0.870,-0.863,-0.825,-0.779,-0.731,-0.680,-0.625,-0.569,-0.509,-0.446,-0.382,-0.315,-0.247,-0.178,-0.107,-0.036,0.036,0.107,0.178,0.247,0.316,0.382,0.447,0.509,0.569,0.626,0.681,0.731,0.779,0.825,0.863,-0.854,-0.817,-0.770,-0.724,-0.673,-0.619,-0.563,-0.504,-0.442,-0.379,-0.312,-0.245,-0.176,-0.106,-0.035,0.036,0.106,0.177,0.245,0.313,0.379,0.443,0.505,0.564,0.619,0.673,0.723,0.770,0.817,0.854,-0.839,-0.800,-0.756,-0.710,-0.662,-0.608,-0.553,-0.495,-0.434,-0.371,-0.306,-0.240,-0.172,-0.104,-0.034,0.035,0.104,0.173,0.241,0.307,0.372,0.434,0.495,0.553,0.608,0.661,0.710,0.756,0.802,0.839,-0.817,-0.780,-0.738,-0.694,-0.646,-0.594,-0.540,-0.483,-0.424,-0.363,-0.300,-0.235,-0.169,-0.101,-0.034,0.034,0.102,0.169,0.235,0.300,0.363,0.425,0.484,0.541,0.594,0.646,0.694,0.738,0.781,0.817,-0.794,-0.759,-0.718,-0.676,-0.629,-0.579,-0.526,-0.470,-0.413,-0.353,-0.292,-0.228,-0.164,-0.098,-0.033,0.033,0.099,0.165,0.229,0.292,0.354,0.413,0.472,0.527,0.579,0.630,0.676,0.718,0.760,0.794,-0.770,-0.734,-0.695,-0.654,-0.609,-0.560,-0.509,-0.455,-0.399,-0.341,-0.282,-0.221,-0.159,-0.095,-0.032,0.032,0.096,0.159,0.221,0.282,0.342,0.399,0.456,0.509,0.560,0.609,0.655,0.696,0.736,0.770,-0.744,-0.709,-0.672,-0.631,-0.587,-0.539,-0.490,-0.438,-0.384,-0.329,-0.271,-0.212,-0.153,-0.092,-0.030,0.031,0.092,0.153,0.213,0.272,0.330,0.385,0.439,0.491,0.540,0.587,0.632,0.672,0.710,0.744,-0.719,-0.686,-0.649,-0.609,-0.564,-0.518,-0.470,-0.420,-0.368,-0.315,-0.260,-0.203,-0.146,-0.088,-0.029,0.030,0.088,0.147,0.204,0.260,0.315,0.368,0.420,0.470,0.518,0.565,0.609,0.649,0.686,0.719,-0.704,-0.666,-0.627,-0.585,-0.540,-0.494,-0.448,-0.400,-0.350,-0.299,-0.247,-0.194,-0.139,-0.084,-0.028,0.028,0.084,0.140,0.194,0.248,0.300,0.350,0.399,0.447,0.495,0.541,0.585,0.627,0.666,0.704,-0.692,-0.646,-0.602,-0.558,-0.513,-0.469,-0.424,-0.378,-0.332,-0.284,-0.234,-0.184,-0.132,-0.079,-0.026,0.027,0.080,0.133,0.184,0.235,0.284,0.330,0.376,0.423,0.469,0.514,0.559,0.602,0.646,0.692,-0.678,-0.621,-0.574,-0.530,-0.485,-0.441,-0.399,-0.356,-0.313,-0.268,-0.221,-0.173,-0.124,-0.075,-0.025,0.025,0.075,0.125,0.174,0.221,0.267,0.309,0.353,0.398,0.442,0.485,0.530,0.575,0.621,0.678,-0.630,-0.584,-0.542,-0.499,-0.453,-0.410,-0.370,-0.331,-0.292,-0.251,-0.207,-0.162,-0.116,-0.070,-0.023,0.024,0.070,0.117,0.163,0.208,0.250,0.290,0.330,0.369,0.410,0.454,0.500,0.544,0.585,0.630,-0.575,-0.543,-0.510,-0.467,-0.416,-0.371,-0.337,-0.306,-0.273,-0.235,-0.195,-0.152,-0.108,-0.065,-0.021,0.022,0.065,0.109,0.152,0.195,0.235,0.272,0.306,0.337,0.371,0.417,0.468,0.510,0.542,0.575,-0.520,-0.502,-0.481,-0.438,-0.373,-0.321,-0.301,-0.284,-0.256,-0.221,-0.182,-0.141,-0.098,-0.059,-0.020,0.020,0.059,0.098,0.141,0.182,0.221,0.256,0.284,0.301,0.321,0.373,0.438,0.481,0.502,0.520]


if __name__ == "__main__":
    unittest.main()


