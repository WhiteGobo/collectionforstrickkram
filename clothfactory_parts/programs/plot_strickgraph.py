#!/bin/env python
import argparse
import os.path
#from datagraph_factory.automatic_directory.filehandler import \
#                                                    save_graph, load_graph
from datagraph_factory import automatic_directory as audi
from datagraph_factory.utils import get_all_datatypes
from datagraph_factory.find_process_path import flowgraph
import clothfactory_parts
from datagraph_factory import datagraph

def get_args():
    parser = argparse.ArgumentParser( description='strick_datagraph_completer' )
    parser.add_argument( 'directory', type=str )
    args = parser.parse_args()
    directorypath = os.path.abspath( args.directory )
    return directorypath

def main( directory_path ):
    mydata = load_datagraph( directory_path )
    retrieve_strickgraphs_from_data( mydata )

def load_datagraph( directory_path ):
    return datagraph.load_from_directory( directory_path )

def retrieve_strickgraphs_from_data( mydata:datagraph ):
    import clothfactory_parts as clops
    from createcloth.visualizer import plotter
    #plotter.myvis3d( tmp["spat"].posgraph )
    #strgras = [ a for a in err.datagraph.values() \
    #            if type(a)==strickgraph_container ][0]
    strpos = [ a for a in mydata.values() \
                if type(a) == clops.strickgraph_spatialdata ][0]
    from createcloth.visualizer import plotter
    plotter.myvis3d( strpos.xposition, strpos.yposition, strpos.zposition, \
                                                            strpos.edges )


if __name__ == "__main__":
    directory_path = get_args()
    main( directory_path )

