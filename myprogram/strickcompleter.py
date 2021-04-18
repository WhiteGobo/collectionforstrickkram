import clothfactory_parts as clops
import datagraph_factory as dagfa
from datagraph_factory import automatic_directory as audi
import argparse

def get_args():
    parser = argparse.ArgumentParser( description='strick_datagraph_completer' )
    parser.add_argument( 'directory', type=str )
    args = parser.parse_args()
    if not os.path.isdirectory( args.directory ):
        raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
                        +", which is not a file" )
    asd = os.path.abspath( args.meshfile )
    return asd


def main( directory_path ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                    = dagfa.get_all_datatypes( mainmodule )
    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()

    flowgraph = dagfa.create_flowgraph_for_datanodes( all_factoryleafs, \
                                                        all_conclusions )

    wholegraph = audi.load_graph( directory_path, [ clops ] )
    audi.complete_datagraph( wholegraph )
    audi.save_graph( wholegraph, directory_path, [ clops ] )



if __name__=="__main__":
    directory_path = get_args()
    main( directory_path )
