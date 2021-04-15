import pkg_resources
from ...verbesserer import manualtoersetzer, verbesserungtoxml, \
                        verbessererfromxml, strick_multiverbessererfromxml
from ...verbesserer.manualtoverbesserung import _start_at_marked
import copy

from ...strickgraph.load_stitchinfo import myasd as stitchinfo
from ...strickgraph.strickgraph_base import stricksubgraph as mygraphtype
from extrasfornetworkx import multiverbesserer
import argparse
from ...strickgraph.fromknitmanual import frommanual
from ...verbesserer.multifrommanuals import main as manstomulti

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",dest="filename", help="outputfile", \
                            type=str, default="")
    parser.add_argument("--reversed",dest="reversed", \
                        help="reverse the manual",\
                        action='store_true')
    args = parser.parse_args()
    return args.filename, args.reversed


pairlist = ( \
        ("6yo\n6k\n6k\n1k 1kmark 1k2tog 2k\n5k\n5bo", \
        "6yo\n6k\n6k\n1k 1kmark 3k 1bo\n5k\n5bo"), \
        \
        ("6yo\n6k\n6k\n1k 1kmark 1k2tog 2k\n1k 1k2tog 2k\n4bo", \
        "6yo\n6k\n6k\n1k 1kmark 3k 1bo\n1k 1k2tog 2k\n4bo"), \
        \
        ("6yo\n6k\n2k 1k2tog 2k\n1k 1kmark 3k\n5k\n5bo", \
        "6yo\n6k\n6k\n1k 1kmark 3k 1bo\n5k\n5bo"), \
        \
        ("6yo\n6k\n2k 1k2tog 2k\n1k 1kmark 3k\n1k 1k2tog 2k\n4bo", \
        "6yo\n6k\n6k\n1k 1kmark 3k 1bo\n1k 1k2tog 2k\n4bo"), \
        \
        ("7yo\n3k 1k2tog 2k\n2k 1k2tog 2k\n1k 1kmark 3k\n5k\n5bo", \
        "7yo\n3k 1k2tog 2k\n6k\n1k 1kmark 3k 1bo\n5k\n5bo"), \
        )


if __name__=="__main__":
    filename, reversed = parse_arguments()
    oldtranslatorlist = []
    if filename:
        try:
            with open( filename, "r" ) as myfile:
                mytext = "".join( myfile.readlines() )
                myfile.close()
                try:
                    insertcolumn = strick_multiverbessererfromxml( mytext, \
                                                    graph_type=mygraphtype)
                    oldtranslatorlist = insertcolumn.verbessererlist
                except Exception:
                    oldtranslatorlist = []
                del( mytext, myfile )
        except FileNotFoundError:
            pass

    myersetzer = manstomulti( pairlist, reverse=reversed, side="right", \
                                oldtranslatorlist = oldtranslatorlist )

    
    if filename:

        myfile = open( filename, "w" )
        myfile.write( myersetzer.toxml_string() )
        myfile.close()

    else:
        print( myersetzer.toxml_string() )
        print( len( myersetzer.verbessererlist ) )
