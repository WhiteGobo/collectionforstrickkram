import unittest
import pkg_resources as pkr
from . import plyford_mesh_handler
from .strickgraph_datatypes import strickgraph_stitchdata
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo
from datagraph_factory.find_process_path import create_flowgraph_for_datanodes
from datagraph_factory.linear_factorybranch import create_linear_function
from datagraph_factory.datagraph import datagraph
from datagraph_factory.constants import DATAGRAPH_DATATYPE as DATATYPE
from datagraph_factory.constants import DATAGRAPH_EDGETYPE as EDGETYPE
from .plyford_mesh_handler import all_factoryleafs
from .plyford_mesh_handler import filepath, mesh_2dmap, mesh_rectangleborder,\
                    mesh_pymesh2, generated_from, map_to_mesh
from datagraph_factory.processes import factory_leaf
import itertools
from .strickgraph_datatypes import strickgraph_stitchdata, strickgraph_spatialdata, strickgraph_container


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
        flowgraph = create_flowgraph_for_datanodes( all_factoryleafs )
                    #itertools.chain(all_factoryleafs,[startdummy] ) \
                    #)
        #print( flowgraph.node_to_datatype )

        #for m in flowgraph.nodes():
        #    print(m)
        #print("bruuuuubruuuuu")
        #for e in flowgraph.edges():
        #    print(e)

        tmp = datagraph()
        tmp.add_node( "filename", filepath )
        #tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        inputgraph = tmp.copy()
        tmp.add_node( "mymesh", mesh_pymesh2 )
        tmp.add_edge( "filename", "mymesh", generated_from )
        tmp.add_node( "surfacemaps", mesh_2dmap )
        tmp.add_edge( "surfacemaps", "mymesh", map_to_mesh )
        #tmp.add_node( "startstrickgraph", strickgraph_container )
        #tmp.add_node( "myborder", mesh_rectangleborder )
        outputgraph = tmp.copy()
        del( tmp )

        testfilename = pkr.resource_filename( __name__, \
                                                "test/meshfortests.ply" )
        myfilepathconstruct = filepath( testfilename )
        mystitchinfo = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )

        myfoo = create_linear_function( flowgraph, inputgraph, outputgraph, \
                                        verbosity=1 )
        myout = myfoo( filename = myfilepathconstruct )#, \
                        #stitchinfo = mystitchinfo )
        return


        
        tmp = datagraph()
        #tmp.add_node( "stitchinfo", **{DATATYPE: strickgraph_stitchdata} )
        tmp.add_node( "myborder", mesh_rectangleborder )
        tmp.add_node( "surfacemaps", mesh_2dmap )
        tmp.add_node( "startstrickgraph", strickgraph_container )
        inputgraph = tmp.copy()
        tmp.add_node( "positiondata", strickgraph_spatialdata )
        outputgraph = tmp.copy()
        
        posfoo = create_linear_function( flowgraph, inputgraph, outputgraph, \
                                        verbosity=1 )
        myfilteredout = { key:value for key, value in myout.items() \
                            if key in posfoo.prestatus.nodes() }
        posout = posfoo( **myfilteredout )


class startdummy( factory_leaf ):
    tmp = datagraph()
    tmp.add_node( "filename", filepath )
    tmp.add_node( "stitchinfo", strickgraph_stitchdata )
    prestatus = tmp.copy()
    poststatus = tmp.copy()


if __name__=="__main__":
    unittest.main()
