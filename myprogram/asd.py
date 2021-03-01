import argparse
import os
from datagraph_factory.find_process_path import create_flowgraph_for_datanodes
from datagraph_factory.linear_factorybranch import create_linear_function
from datagraph_factory import DataRescueException
from datagraph_factory.datagraph import datagraph
from datagraph_factory.processes import factory_leaf
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo

from clothfactory_parts.plyford_mesh_handler import \
        filepath
from clothfactory_parts.plyford_mesh_handler import \
        mesh_pymesh2, \
        mesh_2dmap, \
        map_to_mesh, \
        generated_from, \
        use_stitchdata_for_construction, \
        strickgraph_fit_to_mesh, \
        rand_to_mesh, \
        mesh_rectangleborder

from datagraph_factory.visualize import plot_flowgraph

from clothfactory_parts import \
        strickgraph_container, \
        strickgraph_stitchdata,\
        strickgraph_property_relaxed, \
        springs_of_strickgraph_are_relaxed, \
        strickgraph_property_plainknit, \
        strickgraph_isplainknit
from createcloth.verbesserer import StrickgraphVerbessererException

from clothfactory_parts.plyford_mesh_handler import \
        mesh_to_surfacemap, \
        load_mesh_from_plyford, \
        randrectangle_from_mesh_with_border, \
        strickgraph_dummy_from_rand, \
        relax_strickgraph_on_surface 
from clothfactory_parts import \
        test_if_strickgraph_isrelaxed, \
        test_if_strickgraph_is_plainknit, \
        relax_tension, \
        relax_pressure

from createcloth.strickgraph import tomanual

def main( inputfilepath ):
    myfoo, myfoo2 = create_program()
    mystitchinfo_node = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )
    myfilepath_node = filepath( inputfilepath )

    asd = myfoo( meshfile=myfilepath_node )
    try:
        myfoo2( mymesh= asd["mymesh"], mysurfmaps= asd["asdf"], \
                stitchdata= mystitchinfo_node, \
                myrand= asd["myrand"] ) 
    except DataRescueException as err:
        print( err.datagraph )
        strgras = [ a for a in err.datagraph.values() \
                    if type(a)==strickgraph_container ]
        for tmpstrick_container in strgras:
            tmpstrick = tmpstrick_container.strickgraph
            print( tomanual( tmpstrick, globalstitchinfo ) )

        causeerror = err.__cause__
        if type( causeerror ) == StrickgraphVerbessererException:
            verb = causeerror.usedverbesserer
            mystrick = causeerror.usedstrickgraph
            markednode = causeerror.markednodeinstrickgraph
            verb.print_compare_to_graph_at_position( mystrick, markednode )

        raise err



def get_args():
    parser = argparse.ArgumentParser( description='myprogram' )
    parser.add_argument( 'meshfile', type=str )
    args = parser.parse_args()
    if not os.path.isfile( args.meshfile ):
        raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
                        +", which is not a file" )
    asd = os.path.abspath( args.meshfile )
    return { "inputfilepath":asd }

def create_program():
    all_leafs = [ \
            test_if_strickgraph_isrelaxed, \
            test_if_strickgraph_is_plainknit, \
            mesh_to_surfacemap, \
            load_mesh_from_plyford, \
            randrectangle_from_mesh_with_border, \
            strickgraph_dummy_from_rand, \
            relax_strickgraph_on_surface ,\
            ]

    plyfordleafs = [ \
            mesh_to_surfacemap, \
            load_mesh_from_plyford, \
            randrectangle_from_mesh_with_border, \
            strickgraph_dummy_from_rand, \
            relax_strickgraph_on_surface , \
            ]

    flowgraph_plyford_and_files = create_flowgraph_for_datanodes( plyfordleafs )

    strickgraph_leafs = [ \
            relax_strickgraph_on_surface, \
            strickgraph_dummy_from_rand, \
            test_if_strickgraph_is_plainknit, \
            test_if_strickgraph_isrelaxed, \
            create_dummy_factleaf(), \
            relax_tension, \
            relax_pressure, \
            ]
    flowgraph_strickgraph_generation = create_flowgraph_for_datanodes( strickgraph_leafs )


    tmp = datagraph()
    tmp.add_node( "meshfile", filepath )
    inputgraph = tmp.copy()
    tmp.add_node( "mymesh", mesh_pymesh2 )
    tmp.add_node( "asdf", mesh_2dmap )
    tmp.add_edge( "asdf", "mymesh", map_to_mesh )
    tmp.add_edge( "mymesh", "meshfile", generated_from )
    tmp.add_node( "myrand", mesh_rectangleborder )
    tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
    outputgraph = tmp
    create_surfacemaps_from_file = create_linear_function( \
                                                flowgraph_plyford_and_files,\
                                                inputgraph, outputgraph )
    del( tmp, inputgraph, outputgraph )

    tmp = datagraph()
    tmp.add_node( "mymesh", mesh_pymesh2 )
    tmp.add_node( "mysurfmaps", mesh_2dmap )
    tmp.add_node( "stitchdata", strickgraph_stitchdata )
    tmp.add_node( "myrand", mesh_rectangleborder )
    tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
    tmp.add_edge( "mysurfmaps", "mymesh", map_to_mesh )
    tmp.add_edge( "stitchdata", "mymesh", use_stitchdata_for_construction )
    inputgraph = tmp.copy()
    tmp.add_node( "mystrick", strickgraph_container )
    tmp.add_edge( "mystrick", "mymesh", strickgraph_fit_to_mesh )
    tmp.add_node( "isplain", strickgraph_property_plainknit )
    tmp.add_edge( "mystrick", "isplain", strickgraph_isplainknit )
    tmp.add_node( "isrelaxed", strickgraph_property_relaxed )
    tmp.add_edge( "mystrick", "isrelaxed", springs_of_strickgraph_are_relaxed )
    outputgraph = tmp.copy()
    #plot_flowgraph( flowgraph_strickgraph_generation )
    create_asdf = create_linear_function( flowgraph_strickgraph_generation, \
                                            inputgraph, outputgraph, \
                                            verbosity=1 )
    del( tmp, inputgraph, outputgraph )
                                        

    myflowgraph = create_flowgraph_for_datanodes( all_leafs )
    return create_surfacemaps_from_file, create_asdf


def create_dummy_factleaf():
    tmp = datagraph()
    tmp.add_node( "mymesh", mesh_pymesh2 )
    tmp.add_node( "mysurfmaps", mesh_2dmap )
    tmp.add_node( "stitchdata", strickgraph_stitchdata )
    tmp.add_node( "myrand", mesh_rectangleborder )
    tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
    tmp.add_edge( "mysurfmaps", "mymesh", map_to_mesh )
    tmp.add_edge( "stitchdata", "mymesh", use_stitchdata_for_construction )
    return factory_leaf( tmp, tmp )

if __name__=="__main__":
    myargs = get_args()
    main( **myargs )
