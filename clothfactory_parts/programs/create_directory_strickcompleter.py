#!/bin/env python
"""Program for creating a directory for a knitpiece generation

"""
import clothfactory_parts as clop
import datagraph_factory as dagfa
from datagraph_factory import automatic_directory as audi
import argparse
import os.path
from createcloth.stitchinfo import basic_stitchdata as stinfo

def get_args():
    parser = argparse.ArgumentParser( description='strick_datagraph_completer' )
    parser.add_argument( 'directory', type=str )
    parser.add_argument( 'meshfile', type=str )
    parser.add_argument( '--dont-overwrite', dest="dontoverwrite", \
                        action=argparse.BooleanOptionalAction,\
                        help="fails if directory is not empty" )
    parser.add_argument( '--force', dest="force", \
                        action=argparse.BooleanOptionalAction,\
                        help="overwrites without question" )
    args = parser.parse_args()
    #if not os.path.isdir( args.directory ):
    #    raise KeyError( f"given argument 'meshfile' was given {args.meshfile}"\
    #                    +", which is not a file" )
    if args.dontoverwrite and args.force:
        print( " '--dont-overwrite' and '--force' cant be used together" )
        exit(0)
    savepath = os.path.abspath( args.directory )
    meshfilepath = os.path.abspath( args.meshfile )
    return savepath, meshfilepath, args.force, args.dontoverwrite

def main( directory_path:str, mesh_filepath:str, force:bool, dontoverwrite:bool ):
    datatypes, edgetypes, factoryleafs_dict, conclusionleaf_dict \
                    = dagfa.get_all_datatypes( clop )
    #for a,b in datatypes.items():
    #    print( f"{a}: \n  {b}" )

    all_factoryleafs = factoryleafs_dict.values()
    all_conclusions = conclusionleaf_dict.values()

    flowgraph = dagfa.create_flowgraph_for_datanodes( all_factoryleafs, \
                                                        all_conclusions )
    wholegraph = create_datagraph( mesh_filepath )

    audi.save_graph( wholegraph, directory_path, [ clop ] )


def create_datagraph( meshfilepath ):
    tmp = dagfa.datagraph()
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

    tmp[ "mesh" ] = clop.ply_surface.load_from( meshfilepath )
    tmp["stitchinfo"] = clop.strickgraph_stitchdata( stinfo, "knit", \
                                                "yarnover", "bindoff" )
    return tmp

class checkdirectoryfail( Exception):
    pass

def check_directory( directory_path, force:bool, dontoverwrite:bool ):
    if os.path.exists( directory_path ):
        if os.path.isdir( directory_path ):
            if len(os.listdir( directory_path )) != 0:
                if dontoverwrite:
                    raise checkdirectoryfail( "given directory has files in it" )
                elif force:
                    set_force = True
                else:
                    q = input( "Directory is already filled with info. Overwrite?(y/N)" )
                    q += "N"
                    if q[0] in ('y', 'Y'):
                        print( "Overwriting..." )
                    else:
                        raise checkdirectoryfail( "given directory has files in it" )
                    raise Exception("notimplemented yet, for security reasons:)")
                    os.rmdir( directory_path )
                    shutil.rmtree( directory_path )
                    os.mkdir( directory_path )
        else:
            raise checkdirectoryfail( "given directory is a file" )
    else:
        os.mkdir( directory_path )

if __name__=="__main__":
    directory_path, mesh_file, force, dontoverwrite = get_args()
    try:
        check_directory( directory_path, force, dontoverwrite )
    except checkdirectoryfail as err:
        print( "FAILED" )
        for msg in err.args:
            print(msg)
        exit()
    if not os.path.exists( mesh_file ):
        print( "there is no ply file" )
        exit()
    main( directory_path, mesh_file, force, dontoverwrite )
