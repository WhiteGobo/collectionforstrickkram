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


pairlist1 = ( \
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

pairlist2 = (\
        ("5yo\n5k\n5k\n3k 1kmark 1k 2yo\n7k\n7bo", \
        "5yo\n5k\n3k 1yo 2k\n3k 1kmark 1yo 2k\n7k\n7bo"), \
        ("5yo\n5k\n5k\n4k 1kmark 3yo\n8k\n8bo", \
        "5yo\n5k\n5k\n4k 1kmark 2yo\n5k 1yo 2k\n8bo"), \
        ("5yo\n5k\n5k\n4k 1kmark 3yo\n4k 1k2tog 2k\n7bo", \
        "5yo\n5k\n5k\n4k 1kmark 2yo\n7k\n7bo"), \
        ("3yo\n3k\n3k\n3k 1yomark 3yo\n7k\n7bo", \
        "3yo\n3k\n3k\n3k 1yomark 2yo\n4k 1yo 2k\n7bo"), \
        ("3yo\n3k\n3k\n3k 1yomark 3yo\n3k 1k2tog 2k\n6bo", \
        "3yo\n3k\n3k\n3k 1yomark 2yo\n6k\n6bo"), \
        ("2yo\n2k\n2k\n2k 1yo 1yomark 3yo\n7k\n7bo", \
        "2yo\n2k\n2k\n2k 1yo 1yomark 2yo\n4k 1yo 2k\n7bo"), \
        ("2yo\n2k\n2k\n2k 1yo 1yomark 3yo\n3k 1k2tog 2k\n6bo", \
        "2yo\n2k\n2k\n2k 1yo 1yomark 2yo\n6k\n6bo"), \
        )

pairlist = pairlist1 + pairlist2

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
