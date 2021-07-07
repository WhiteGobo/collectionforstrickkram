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
import tempfile
from datagraph_factory.utils import get_all_datatypes


from datagraph_factory.find_process_path import create_flowgraph_for_datanodes
from datagraph_factory.linear_factorybranch import create_linear_function
from datagraph_factory.datagraph import datagraph
from datagraph_factory.utils import get_all_datatypes
from createcloth.strickgraph.load_stitchinfo import myasd as globalstitchinfo
from . import __init__ as mainmodule
import clothfactory_parts as clop


from datagraph_factory.automatic_directory.filehandler import \
                                            save_graph, load_graph
from datagraph_factory.automatic_directory import complete_datagraph
from clothfactory_parts import meshthings, plainknit, strickgraph
from datagraph_factory import DataRescueException
from createcloth.visualizer import plotter
import traceback


import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig( format=FORMAT, level=logging.WARNING )
#print( set(logging.root.manager.loggerDict.keys()) )
datagraph_loggernames = [ name \
                for name in logging.root.manager.loggerDict.keys() \
                if "datagraph" in name ]
for loggername in datagraph_loggernames:
    logger = logging.getLogger( loggername )
    logger.setLevel( logging.DEBUG )


def get_args():
    parser = argparse.ArgumentParser( description='myprogram' )
    parser.add_argument( 'meshfile', type=str )
    args = parser.parse_args()
    if not os.path.isfile( args.meshfile ):
        raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
                        +", which is not a file" )
    asd = os.path.abspath( args.meshfile )
    return { "inputfilepath":asd }


def example_from_test( filepath ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
            = get_all_datatypes( clop )
    all_factoryleafs = set( factoryleafs_dict.values() )
    all_conclusions = set( conclusionleaf_dict.values() )

    flowgraph = create_flowgraph_for_datanodes( all_factoryleafs, \
                                                    all_conclusions )
    #from datagraph_factory.visualize import plot_flowgraph
    #plot_flowgraph( flowgraph )
    tmp = datagraph()

    tmp.add_node( "mesh", clop.ply_surface )
    tmp.add_node( "maptomesh", clop.ply_2dmap )
    tmp.add_node( "strickgraph", clop.strickgraph_container )
    tmp.add_node( "spat", clop.strickgraph_spatialdata )
    tmp.add_edge( "strickgraph", "spat", clop.stitchposition )
    tmp.add_edge( "maptomesh", "mesh", clop.map_to_mesh )
    tmp.add_edge( "strickgraph", "mesh", clop.strickgraph_fit_to_mesh )
    tmp.add_edge( "maptomesh", "strickgraph", clop.physics.map_for_strickgraph )
    tmp.add_node( "isrelaxed" , clop.strickgraph_property_relaxed )
    tmp.add_node( "isplainknit", clop.strickgraph_property_plainknit )
    tmp.add_node( "stitchinfo", clop.strickgraph_stitchdata )
    tmp.add_edge( "stitchinfo", "mesh", clop.use_stitchdata_for_construction )
    tmp.add_edge( "strickgraph", "isrelaxed", \
                    clop.springs_of_strickgraph_are_relaxed )
    tmp.add_edge( "strickgraph", "isplainknit", clop.strickgraph_isplainknit )

    tmp["stitchinfo"] = clop.strickgraph_stitchdata( globalstitchinfo, "knit", \
                                                "yarnover", "bindoff" )

    tmpsurf = clop.ply_surface.load_from( filepath )
    tmp["mesh"] = tmpsurf
    #with importlib.resources.path( test_src, "tester_surfmap.ply" ) \
    #                                                        as filepath:
    #    tmpmap = ply_2dmap.load_from( filepath )
    #tmp["maptomesh"] = tmpmap

    #with tempfile.TemporaryDirectory() as tmpdir:
    #    save_graph( tmp, tmpdir, [ meshthings, physics, plainknit, strickgraph] )
    try:
        tmp = complete_datagraph( flowgraph, tmp )
    except DataRescueException as err:
        mydatarescue( err )
        raise err
    outputstrickgraph = tmp["strickgraph"].strickgraph
    print( tomanual( outputstrickgraph, globalstitchinfo ) )
    with tempfile.TemporaryDirectory() as tmpdir:
        save_graph( tmp, tmpdir, [ clop ])
        input( f"temporary saved output to: {tmpdir}" )
    plotter.myvis3d( tmp["spat"].posgraph )

def mydatarescue( err ):
    #from datagraph_factory import DataRescueException
    #from createcloth.verbesserer import StrickgraphVerbessererException
    #print( err.datagraph )
    #print( err.__cause__.args )
    #print("brubru",*( gracon.args for gracon in err.datagraph.values() \
    #            if type(gracon) == strickgraph_property_plainknit ))
    strgras = [ a for a in err.datagraph.values() \
                if type(a)==clop.strickgraph_container ]
    strpos = [ a for a in err.datagraph.values() \
                if type(a)==clop.strickgraph_spatialdata ]
    for tmpstrick_container in strgras:
        tmpstrick = tmpstrick_container.strickgraph
        print( tmpstrick.to_manual( globalstitchinfo ) )
    causeerror = err.__cause__
    if type( causeerror ) == StrickgraphVerbessererException:
        verb = causeerror.usedverbesserer
        mystrick = causeerror.usedstrickgraph
        markednode = causeerror.markednodeinstrickgraph
        print( mystrick.nodes[markednode] )
        print("brubru\n\n\n")
        traceback.print_exc()
        verb.print_compare_to_graph_at_position( mystrick, markednode )
    else:
        for tmppos in strpos:
            plotter.myvis3d( tmppos.posgraph )


if __name__=="__main__":
    myargs = get_args()
    example_from_test( myargs["inputfilepath"] )
    #main( **myargs )
