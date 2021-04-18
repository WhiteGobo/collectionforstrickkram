import unittest
import pkg_resources as pkr
#from .strickgraph_datatypes import strickgraph_stitchdata
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo
from createcloth.strickgraph.strickgraph_base import strickgraph
from datagraph_factory.find_process_path import create_flowgraph_for_datanodes
from datagraph_factory.linear_factorybranch import create_linear_function
from datagraph_factory.datagraph import datagraph
from datagraph_factory.utils import get_all_datatypes, \
                                list_available_edges_with_datatype 
#from .plyford_mesh_handler import all_factoryleafs
#from .plyford_mesh_handler import filepath, mesh_2dmap, mesh_rectangleborder,\
#                    mesh_pymesh2, generated_from, map_to_mesh
from datagraph_factory.processes import factory_leaf
import itertools
#from .strickgraph_datatypes import strickgraph_stitchdata, strickgraph_spatialdata, strickgraph_container

from . import __init__ as mainmodule
from . import strickgraph_container, strickgraph_spatialdata, \
            strickgraph_stitchdata
from . import ply_surface, ply_2dmap
import importlib.resources
import tempfile
import os.path
from . import meshthings
import networkx as netx

class TestClothfactoryParts( unittest.TestCase ):
    #def SetUp
    def test_generate_relaxation( self ):
        """
        Tests following things:
        import ply-format
        identify rectangle surface of special ply-format. 
        must be written in file
        create surfacemap from rectangle surface
        create easy rectangular strickgraph from rectangle surface
        get relaxation position of strickgraph with surfacemaps
        """

        #print( list_available_edges_with_datatype( plyfilepath, mainmodule ) )
        datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                = get_all_datatypes( mainmodule )
        all_factoryleafs = factoryleafs_dict.values()
        all_conclusions = conclusionleaf_dict.values()

        flowgraph = create_flowgraph_for_datanodes( all_factoryleafs, \
                                                        all_conclusions )
        return
                    #)
        #print( flowgraph.node_to_datatype )

        tmp = datagraph()
        tmp.add_node( "filename", plyfilepath )
        #tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        inputgraph = tmp.copy()
        tmp.add_node( "mymesh", mesh_pymesh2 )
        tmp.add_edge( "mymesh", "filename", generated_from )
        tmp.add_node( "surfacemaps", mesh_2dmap )
        tmp.add_edge( "surfacemaps", "mymesh", map_to_mesh )
        #tmp.add_node( "startstrickgraph", strickgraph_container )
        #tmp.add_node( "myborder", mesh_rectangleborder )
        outputgraph = tmp.copy()
        del( tmp )

        testfilename = pkr.resource_filename( __name__, \
                                                "test/meshfortests.ply" )
        myfilepathconstruct = plyfilepath( testfilename )
        mystitchinfo = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )

        myfoo = create_linear_function( flowgraph, inputgraph, outputgraph, \
                                        verbosity=1 )
        myout = myfoo( filename = myfilepathconstruct )#, \
                        #stitchinfo = mystitchinfo )
        return


        
        tmp = datagraph()
        tmp.add_node( "myborder", mesh_rectangleborder )
        tmp.add_node( "surfacemaps", mesh_2dmap )
        tmp.add_edge( "myborder", "surfacemaps", randtomesh )
        tmp.add_node( "startstrickgraph", strickgraph_container )
        inputgraph = tmp.copy()
        tmp.add_node( "positiondata", strickgraph_spatialdata )
        outputgraph = tmp.copy()
        
        posfoo = create_linear_function( flowgraph, inputgraph, outputgraph, \
                                        verbosity=1 )
        myfilteredout = { key:value for key, value in myout.items() \
                            if key in posfoo.prestatus.nodes() }
        posout = posfoo( **myfilteredout )

    def test_asdf( self ):
        datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                = get_all_datatypes( mainmodule )
        #all_factoryleafs = factoryleafs_dict.values()
        #all_conclusions = conclusionleaf_dict.values()
        #for i,j in factoryleafs_dict.items():
        #    print( i )
        #    print( j)
        #    print()


    def test_generate_2dmap( self ):
        from createcloth.meshhandler import test_src 
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        output = meshthings.mesh_to_surfacemap( mymesh = tmpsurf )
        self.assertTrue( "mysurfacemaps" in output.keys() )


    def test_physics( self ):
        from createcloth.meshhandler import test_src 
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        with importlib.resources.path( test_src, "tester_surfmap.ply" ) \
                                                                as filepath:
            tmpmap = ply_2dmap.load_from( filepath )
        from . import strickgraph as strigra
        tmpgrid = netx.grid_2d_graph(10,10)
        firstrow = [ node for node in tmpgrid.nodes if node[0]==0 ]
        tmpstrick = strickgraph.from_gridgraph( tmpgrid, firstrow, \
                                                    globalstitchinfo )
        mystrigracont = strigra.strickgraph_container( tmpstrick )

        from . import physics as relsurf
        output = relsurf.relax_strickgraph_on_surface( mymesh=tmpsurf, \
                                mysurf=tmpmap, inputstrickgraph=mystrigracont )
        self.assertEqual( set(("positiondata",)), output.keys() )
        self.assertEqual( type(output["positiondata"]), strickgraph_spatialdata)
        strickpositions = output["positiondata"]

        output = relsurf.test_if_strickgraph_isrelaxed( mystrick=mystrigracont,\
                                            positions=strickpositions )
        self.assertEqual( set(("havetension",)), output.keys() )
        tensionpropcont = output["havetension"]
        #output["havepressure"]
        #output["havetension"]
        #output["isrelaxed"]

        #def test_plainknit( self ):
        from . import strickgraph as strigra
        tmpgrid = netx.grid_2d_graph(10,10)
        firstrow = [ node for node in tmpgrid.nodes if node[0]==0 ]
        tmpstrick = strickgraph.from_gridgraph( tmpgrid, firstrow, \
                                                    globalstitchinfo )
        mystrigracont = strigra.strickgraph_container( tmpstrick )
        from . import plainknit
        output = plainknit.test_if_strickgraph_is_plainknit( \
                                                    mystrick=mystrigracont )
        self.assertEqual( set(("isplainknit",)), output.keys() )
        plainknitprop = output["isplainknit"]

        from . import plainknit
        #plainknit.relax_pressure( isrelaxed=output["havepressure"], isplainknit=output["isplainknit"], mystrickgraph=, mymesh= )
        output = plainknit.relax_tension( isrelaxed = tensionpropcont, \
                                isplainknit = plainknitprop,\
                                mystrickgraph = mystrigracont, \
                                mymesh = tmpmap,\
                                )
        self.assertEqual( set(("newstrickgraph",)), output.keys() )



    def test_strickgraphdummy( self ):
        from createcloth.meshhandler import test_src 
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        with importlib.resources.path( test_src, "tester_surfmap.ply" ) \
                                                                as filepath:
            tmpmap = ply_2dmap.load_from( filepath )

        mystitchcont = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )
        from . import meshthings
        output = meshthings.strickgraph_dummy_from_rand( \
                                    stitchdata=mystitchcont, mymesh=tmpsurf )
        self.assertEqual( output.keys(), set(("roughstrickgraph",)))
        mystrickgraph = output["roughstrickgraph"]



    def test_meshhandler( self ):
        from createcloth.meshhandler import test_src 
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        with importlib.resources.path( test_src, "tester_surfmap.ply" ) \
                                                                as filepath:
            tmpmap = ply_2dmap.load_from( filepath )

        from createcloth.meshhandler.surface_container import surface,surfacemap
        self.assertEqual( type(tmpsurf.surfacemesh), surface )
        self.assertEqual( type(tmpmap.surfacemap), surfacemap )

        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "asdf" )
            tmpsurf.save_as( myfilepath )
            myfilepath = os.path.join( tmpdir, "asdg" )
            tmpmap.save_as( myfilepath )

    def test_strickgraphcontainer( self ):
        from . import strickgraph as strigra
        tmpgrid = netx.grid_2d_graph(10,10)
        firstrow = [ node for node in tmpgrid.nodes if node[0]==0 ]
        tmpstrick = strickgraph.from_gridgraph( tmpgrid, firstrow, \
                                                    globalstitchinfo )
        mystrigracont = strigra.strickgraph_container( tmpstrick )
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join( tmpdir, "tmpfile" )
            mystrigracont.save_to( filepath )
            asd = strigra.strickgraph_container.load_from( filepath )
        self.assertEqual( asd.strickgraph, mystrigracont.strickgraph )

    def test_saveloadstitchdata( self ):
        raise Exception()

if __name__=="__main__":
    unittest.main()
