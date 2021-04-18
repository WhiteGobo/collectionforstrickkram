import clothfactory_parts as clops
import datagraph_factory as dagfa
from datagraph_factory import automatic_directory as audi
import argparse
import os.path

def get_args():
    parser = argparse.ArgumentParser( description='strick_datagraph_completer' )
    parser.add_argument( 'directory', type=str )
    args = parser.parse_args()
    #if not os.path.isdir( args.directory ):
    #    raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
    #                    +", which is not a file" )
    asd = os.path.abspath( args.directory )
    return asd

def main( directory_path ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                    = dagfa.get_all_datatypes( clops )
    for a,b in datatypes.items():
        print( f"{a}: \n  {b}" )
    return

    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()

    flowgraph = dagfa.create_flowgraph_for_datanodes( all_factoryleafs, \
                                                        all_conclusions )
    wholegraph = create_datagraph()

    audi.save_graph( wholegraph, directory_path, [ clops ] )


def create_datagraph():
    tmp = dagfa.datagraph()
    tmp.add_node( "meshfile", ply_surface )
    tmp.add_node( "mesh2dmap", ply_2dmap )
    #tmp.add_node( "meshfile", plyfilepath )
    #tmp.add_node( "mymesh", mesh_pymesh2 )
    #tmp.add_edge( "mymesh", "meshfile", generated_from )
    #tmp.add_node( "myrand", mesh_rectangleborder )
    #tmp.add_edge( "myrand", "mymesh", rand_to_mesh )
    tmp.add_node( "stitchdata", strickgraph_stitchdata )
    tmp.add_edge( "stitchdata", "mymesh", use_stitchdata_for_construction )

    tmp.add_node( "mystrick", strickgraph_container )
    tmp.add_edge( "mystrick", "mymesh", strickgraph_fit_to_mesh )
    tmp.add_node( "isplain", strickgraph_property_plainknit )
    tmp.add_edge( "mystrick", "isplain", strickgraph_isplainknit )
    tmp.add_node( "isrelaxed", strickgraph_property_relaxed )
    tmp.add_edge( "mystrick", "isrelaxed", springs_of_strickgraph_are_relaxed )
    return tmp


if __name__=="__main__":
    directory_path = get_args()
    main( directory_path )

