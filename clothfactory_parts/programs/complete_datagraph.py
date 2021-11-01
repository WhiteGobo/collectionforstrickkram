#!/bin/env python
import argparse
import os.path
#from datagraph_factory.automatic_directory.filehandler import \
#                                                    save_graph, load_graph
from datagraph_factory import automatic_directory as audi
from datagraph_factory.utils import get_all_datatypes
from datagraph_factory.find_process_path import flowgraph
from datagraph_factory import DataRescueException
import clothfactory_parts
from datagraph_factory import datagraph
import logging
logging.basicConfig( level= logging.DEBUG )

def get_args():
    parser = argparse.ArgumentParser( description='strick_datagraph_completer' )
    parser.add_argument( 'directory', type=str )
    args = parser.parse_args()
    directorypath = os.path.abspath( args.directory )
    return directorypath

def main( directory_path ):
    mydata = load_datagraph( directory_path )
    try:
        mydata = complete_data( mydata )
    except DataRescueException as err:
        #tmp = err.datagraph
        for key, val in err.datagraph.items():
            if key in mydata.nodes():
                mydata[ key ] = val
        tmp = mydata
        save_datagraph( mydata, directory_path )
        raise err
    save_datagraph( mydata, directory_path )

def load_datagraph( directory_path ):
    return datagraph.load_from_directory( directory_path )

def complete_data( mydata:datagraph ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
            = get_all_datatypes( clothfactory_parts )
    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()
    myflowgraph = flowgraph.from_datanodes( all_factoryleafs, all_conclusions )
    tmp = audi.complete_datagraph( myflowgraph, mydata )
    return tmp

def save_datagraph( mydata:datagraph, directory_path ):
    mydata.save_graph( directory_path )


if __name__ == "__main__":
    directory_path = get_args()
    main( directory_path )
