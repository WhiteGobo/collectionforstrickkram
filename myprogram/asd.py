import argparse
import os
from datagraph_factory.find_process_path import create_flowgraph_for_datanodes
from datagraph_factory.linear_factorybranch import create_linear_function
from datagraph_factory import DataRescueException
from datagraph_factory.datagraph import datagraph
from datagraph_factory.processes import factory_leaf
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo

from datagraph_factory.visualize import plot_flowgraph

from createcloth.verbesserer import StrickgraphVerbessererException

from createcloth.strickgraph import tomanual
from createcloth.visualizer import easygraph

from clothfactory_parts import plyfilepath, mesh_pymesh2, \
            generated_from, map_to_file, generated_from, mesh_rectangleborder, \
            rand_to_mesh, mesh_2dmap, map_to_mesh, \
            use_stitchdata_for_construction, strickgraph_container, \
            strickgraph_fit_to_mesh, strickgraph_isplainknit, \
            strickgraph_property_plainknit, strickgraph_property_relaxed, \
            springs_of_strickgraph_are_relaxed, strickgraph_property_plainknit,\
            strickgraph_stitchdata

from datagraph_factory.utils import get_all_datatypes

def main( inputfilepath ):
    myfoo, myfoo2 = create_program()
    mystitchinfo_node = strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                    "yarnover", "bindoff" )
    myfilepath_node = plyfilepath( inputfilepath )

    asd = myfoo( meshfile=myfilepath_node )
    try:
        #mydatagraph = myfoo2( mymesh= asd["mymesh"], mysurfmaps= asd["asdf"], \
        mydatagraph = myfoo2( mymesh= asd["mymesh"],\
                    stitchdata= mystitchinfo_node, myrand= asd["myrand"] ) 
    except DataRescueException as err:
        print( err.datagraph )
        print( err.__cause__.args )
        print("brubru",*( gracon.args for gracon in err.datagraph.values() \
                    if type(gracon) == strickgraph_property_plainknit ))
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
            print( mystrick.nodes[markednode] )
            import traceback
            print("brubru\n\n\n")
            traceback.print_exc()
            verb.print_compare_to_graph_at_position( mystrick, markednode )


        else:
            raise err
    outputstrickgraph = mydatagraph["mystrick"].strickgraph
    print( tomanual( outputstrickgraph, globalstitchinfo ) )
    easygraph( outputstrickgraph )



def get_args():
    parser = argparse.ArgumentParser( description='myprogram' )
    parser.add_argument( 'meshfile', type=str )
    args = parser.parse_args()
    if not os.path.isfile( args.meshfile ):
        raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
                        +", which is not a file" )
    asd = os.path.abspath( args.meshfile )
    return { "inputfilepath":asd }

import clothfactory_parts

def create_program():
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
            = get_all_datatypes( clothfactory_parts )
    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()

    flowgraph_plyford_and_files = create_flowgraph_for_datanodes( \
                                                    all_factoryleafs, \
                                                    all_conclusions )
    flowgraph_strickgraph_generation = flowgraph_plyford_and_files


    tmp = datagraph()
    tmp.add_node( "meshfile", plyfilepath )
    inputgraph = tmp.copy()
    tmp.add_node( "mymesh", mesh_pymesh2 )
    #tmp.add_node( "asdf", mesh_2dmap )
    #tmp.add_edge( "asdf", "mymesh", map_to_mesh )
    #tmp.add_edge( "asdf", "meshfile", map_to_file )
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
    #tmp.add_node( "mysurfmaps", mesh_2dmap )
    tmp.add_node( "stitchdata", strickgraph_stitchdata )
    tmp.add_node( "myrand", mesh_rectangleborder )
    tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
    #tmp.add_edge( "mysurfmaps", "mymesh", map_to_mesh )
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
                                        

    myflowgraph = create_flowgraph_for_datanodes( all_factoryleafs )
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
