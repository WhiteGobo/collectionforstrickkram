#!/bin/env python
import argparse
import os.path
#from datagraph_factory.automatic_directory.filehandler import \
#                                                    save_graph, load_graph
from datagraph_factory import automatic_directory as audi
from datagraph_factory.utils import get_all_datatypes
from datagraph_factory import flowgraph
from datagraph_factory import DataRescueException
import clothfactory_parts
from datagraph_factory import datagraph
import logging
logging.basicConfig( level= logging.DEBUG )
for logname in ["datagraph_factory.linear_factorybranch"]:
    logging.getLogger( logname ).setLevel( logging.DEBUG )
    

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
        save_datagraph( err.datagraph, os.path.join( directory_path, "saved" ))
        raise err
    save_datagraph( mydata, directory_path )

def load_datagraph( directory_path ):
    return datagraph.load_from_directory( directory_path )

def complete_data( mydata:datagraph ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
            = get_all_datatypes( clothfactory_parts )
    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()
    myflowgraph = flowgraph.from_factory_leafs( all_factoryleafs , all_conclusions )
    #raise Exception( myflowgraph.get_all_used_factoryleafs(), myflowgraph.get_all_datastates() )
    tmp = audi.complete_datagraph( myflowgraph, mydata )
    return tmp

def save_datagraph( mydata:datagraph, directory_path ):
    mydata.save_graph( directory_path )


if __name__ == "__main__":
    directory_path = get_args()
    main( directory_path )
