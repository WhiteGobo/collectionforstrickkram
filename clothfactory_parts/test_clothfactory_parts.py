import unittest
from . import physics
import pkg_resources as pkr
#from .strickgraph_datatypes import strickgraph_stitchdata
from createcloth.stitchinfo import basic_stitchdata as globalstitchinfo
from createcloth.strickgraph.strickgraph_base import strickgraph
from datagraph_factory.find_process_path import flowgraph
from datagraph_factory import datagraph
from datagraph_factory import complex_linear_factory_leaf
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
from . import strickgraph_fit_to_mesh, strickgraph_property_relaxed, springs_of_strickgraph_are_relaxed, strickgraph_property_plainknit,  strickgraph_isplainknit, strickgraph_stitchdata, map_to_mesh, use_stitchdata_for_construction, stitchposition

from . import ply_surface, ply_2dmap
import importlib.resources
import tempfile
import os.path
from . import meshthings
import networkx as netx
import logging
logger = logging.getLogger( __name__ )
logging.basicConfig( level=logging.WARNING )
#for logname in ["datagraph_factory.linear_factorybranch", "clothfactory_parts.plainknit.factory_leaf"]:
#    interestinglogger = logging.getLogger( logname )
#    interestinglogger.setLevel( logging.DEBUG )
#matplotlogger = logging.getLogger("matplotlib.font_manager")
#matplotlogger.setLevel()

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

        myflowgraph = flowgraph.from_datanodes( all_factoryleafs, \
                                                        all_conclusions )
        return
                    #)
        #print( flowgraph.node_to_datatype )

        tmp = datagraph()
        tmp.add_node( "filename", plyfilepath )
        #tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        inputgraph = tmp.copy()
        tmp.add_node( "mymesh", mesh_pymesh2 )
        tmp.add_edge( "mymesh", "filename", map_to_mesh )
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

        myfoo = complex_linear_factory_leaf.create_linear_function( \
                                        flowgraph, inputgraph, outputgraph, \
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


    @unittest.skip( "needs too much time" )
    def test_generate_2dmap( self ):
        """

        :todo: shorten time needed
        """
        from createcloth.meshhandler import test_src 
        with importlib.resources.path( test_src, "tester.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        output = meshthings.mesh_to_surfacemap( mymesh = tmpsurf )
        self.assertTrue( "mysurfacemaps" in output.keys() )



    @unittest.expectedFailure
    def test_strickgraphdummy( self ):
        """

        :todo: ply_2dmap has no load_from anymore
        """
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



    @unittest.expectedFailure
    def test_meshhandler( self ):
        """

        :todo: ply_2dmap jas no load_from
        """
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
            mystrigracont.save_as( filepath )
            asd = strigra.strickgraph_container.load_from( filepath )
        self.assertEqual( asd.strickgraph, mystrigracont.strickgraph )


    def test_saveloadstitchdata( self ):
        mystitchinfo = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join( tmpdir, "tmpfile" )
            mystitchinfo.save_as( filepath )
            copy_stinfo = strickgraph_stitchdata.load_from( filepath )


    #@unittest.skip( "takes too much time" )
    def test_completingdatagraph( self ):
        datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                = get_all_datatypes( mainmodule )
        all_factoryleafs = set( factoryleafs_dict.values() )
        all_conclusions = set( conclusionleaf_dict.values() )

        myflowgraph = flowgraph.from_datanodes( all_factoryleafs, \
                                                        all_conclusions )
        #from datagraph_factory.visualize import plot_flowgraph
        #plot_flowgraph( flowgraph )
        tmp = datagraph()

        tmp.add_node( "mesh", ply_surface )
        tmp.add_node( "maptomesh", ply_2dmap )
        tmp.add_node( "strickgraph", strickgraph_container )
        tmp.add_node( "spat", strickgraph_spatialdata )
        tmp.add_edge( "strickgraph", "spat", stitchposition )
        tmp.add_edge( "maptomesh", "mesh", map_to_mesh )
        tmp.add_edge( "strickgraph", "mesh", strickgraph_fit_to_mesh )
        tmp.add_edge( "maptomesh", "strickgraph", physics.map_for_strickgraph )
        tmp.add_node( "isrelaxed" , strickgraph_property_relaxed )
        tmp.add_node( "isplainknit", strickgraph_property_plainknit )
        tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        tmp.add_edge( "stitchinfo", "mesh", use_stitchdata_for_construction )
        tmp.add_edge( "strickgraph", "isrelaxed", \
                        springs_of_strickgraph_are_relaxed )
        tmp.add_edge( "strickgraph", "isplainknit", strickgraph_isplainknit )

        tmp["stitchinfo"] = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )
        from createcloth.meshhandler import test_src 
        from . import test
        #with importlib.resources.path( test_src, "tester.ply" ) as filepath:
        #with importlib.resources.path( test_src, "surfmap.ply" ) as filepath:
        with importlib.resources.path( test, "testbody_withmap.ply" ) as filepath:
            tmpsurf = ply_surface.load_from( filepath )
        tmp["mesh"] = tmpsurf
        #with importlib.resources.path( test_src, "tester_surfmap.ply" ) \
        #                                                        as filepath:
        #    tmpmap = ply_2dmap.load_from( filepath )
        #tmp["maptomesh"] = tmpmap
        from datagraph_factory.automatic_directory import complete_datagraph

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp.save_graph( tmpdir )

        return
        from datagraph_factory import DataRescueException
        try:
            tmp = complete_datagraph( myflowgraph, tmp )
        except DataRescueException as err:
            mydatarescue( err )
            raise err
        from createcloth.visualizer import plotter
        
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_graph( tmp, tmpdir, [ meshthings, physics, plainknit, strickgraph] )
            #input( tmpdir )
        #from createcloth.visualizer import plotter
        #plotter.myvis3d( tmp["spat"].posgraph )
        self.assertEqual( tmp["strickgraph"].strickgraph.to_manual(globalstitchinfo) , examplestrickman )
        
def mydatarescue( err ):
    from datagraph_factory import DataRescueException
    from createcloth.verbesserer import StrickgraphVerbessererException
    print( err.datagraph )
    print( err.__cause__.args )
    print("brubru",*( gracon.args for gracon in err.datagraph.values() \
                if type(gracon) == strickgraph_property_plainknit ))
    strgras = [ a for a in err.datagraph.values() \
                if type(a)==strickgraph_container ]
    strpos = [ a for a in err.datagraph.values() \
                if type(a)==strickgraph_spatialdata ]
    from createcloth.visualizer import plotter
    for tmpstrick_container in strgras:
        tmpstrick = tmpstrick_container.strickgraph
        print( tmpstrick.to_manual( globalstitchinfo ) )


    for tmppos in strpos:
        plotter.myvis3d( tmppos.posgraph )
        tmpedges = [e[:2] for e in strgras[0].strickgraph.get_edges_with_labels()]
        plotter.myvis3d( tmppos.xposition, tmppos.yposition, tmppos.zposition, tmpedges )

    causeerror = err.__cause__
    if type( causeerror ) == StrickgraphVerbessererException:
        verb = causeerror.usedverbesserer
        mystrick = causeerror.usedstrickgraph
        markednode = causeerror.markednodeinstrickgraph
        print( mystrick.nodes[markednode] )
        import traceback
        print("brubru\n\n\n")
        traceback.print_exc()
        verb.print_compare_to_graph_at_position( mystrick, markednode )
    raise err

examplestrickman = "20yo\n20k\n2k 1yo 16k 1yo 2k\n2k 1yo 18k 1yo 2k\n24k\n2k 1yo 20k 1yo 2k\n26k\n2k 1yo 22k 1yo 2k\n28k\n2k 1yo 24k 1yo 2k\n30k\n30k\n30k\n30k\n30k\n30k\n30k\n2k 1k2tog 22k 1k2tog 2k\n28k\n2k 1k2tog 20k 1k2tog 2k\n26k\n2k 1k2tog 18k 1k2tog 2k\n24k\n2k 1k2tog 16k 1k2tog 2k\n2k 1k2tog 14k 1k2tog 2k\n20bo"


if __name__=="__main__":
    unittest.main()
