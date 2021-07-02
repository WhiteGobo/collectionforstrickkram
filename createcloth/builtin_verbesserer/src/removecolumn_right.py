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

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",dest="filename", help="outputfile", \
                            type=str, default="")
    parser.add_argument("--reversed",dest="reversed", \
                        help="reverse the manual",\
                        action='store_true')
    args = parser.parse_args()
    return args.filename, args.reversed

pairlist = (\
        ("6yo\n6k\n4k 1kmark 1k\n6k\n6k\n6bo", \
        "6yo\n6k\n2k 1k2tog 1kmark 1k\n2k 1yo 3k\n6k\n6bo"), \
        ("7yo\n3k 1k2tog 2k\n4k 1kmark 1k\n6k\n6k\n6bo", \
        "7yo\n3k 1k2tog 2k\n2k 1k2tog 1kmark 1k\n2k 1yo 3k\n6k\n6bo"), \
        ("6yo\n6k\n4k 1kmark 1k\n2k 1k2tog 2k\n5k\n5bo", \
        "6yo\n6k\n2k 1k2tog 1kmark 1k\n5k\n5k\n5bo"), \
        ("7yo\n3k 1k2tog 2k\n4k 1kmark 1k\n2k 1k2tog 2k\n5k\n5bo", \
        "7yo\n3k 1k2tog 2k\n2k 1k2tog 1kmark 1k\n5k\n5k\n5bo"), \
        ("6yo\n6k\n4k 1kmark 1k\n2k 1k2tog 2k\n5bo", \
        "6yo\n6k\n2k 1k2tog 1kmark 1k\n5k\n5bo"), \
        ("6yo\n6k\n4k 1kmark 1k\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo", \
        "6yo\n6k\n2k 1k2tog 1kmark 1k\n5k\n1k 1k2tog 2k\n4bo"), \
        ("7yo\n3k 1k2tog 2k\n4k 1kmark 1k\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo", \
        "7yo\n3k 1k2tog 2k\n2k 1k2tog 1kmark 1k\n5k\n1k 1k2tog 2k\n4bo"), \
        ("5yo\n3k 1yo 2k\n4k 1kmark 1k\n6k\n6k\n6bo", \
        "5yo\n3k 1yo 2k\n2k 1k2tog 1kmark 1k\n3k 1yo 2k\n6k\n6bo"), \
        ("5yo\n3k 1yo 2k\n4k 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "5yo\n3k 1yo 2k\n2k 1k2tog 1kmark 1k\n2k 1yo 3k\n2k 1k2tog 2k\n5bo"), \
        ("5yo\n3k 1yo 2k\n4k 1kmark 1k\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo", \
        "5yo\n3k 1yo 2k\n2k 1k2tog 1kmark 1k\n5k\n1k 1k2tog 2k\n4bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n6k\n6bo", \
        "6yo\n6k\n2k 1k2tog 1kmark 1k\n3k 1yo 2k\n6bo"), \
        ("6yo\n6k\n2k 1k2tog 2k\n3k 1yo 1kmark 1k\n2bo 1b2o 2bo", \
        "6yo\n6k\n2k 1k2tog 2k\n3k 1kmark 1k\n5bo"), \
        \
        ("4yo 1yomark 1yo\n6k\n6k\n6bo", \
        "3yo 1yomark 1yo\n3k 1yo 2k\n6k\n6bo"), \
        ("6yo\n4k 1kmark 1k\n6k\n6bo", \
        "6yo\n2k 1k2tog 1kmark 1k\n3k 1yo 2k\n6bo"), \
        \
        ("5yo\n3k 1yo 1kmark 1k\n6k\n6bo", \
        "5yo\n3k 1kmark 1k\n3k 1yo 2k\n6bo"), \
        ("5yo\n3k 1yo 1kmark 1k\n6k\n6k\n6bo", \
        "5yo\n3k 1kmark 1k\n3k 1yo 2k\n6k\n6bo"), \
        ("5yo\n5k\n3k 1yo 1kmark 1k\n6k\n6bo", \
        "5yo\n5k\n3k 1kmark 1k\n3k 1yo 2k\n6bo"), \
        ("5yo\n5k\n3k 1yo 1kmark 1k\n6k\n6k\n6bo", \
        "5yo\n5k\n3k 1kmark 1k\n3k 1yo 2k\n6k\n6bo"), \
        ("5yo\n5k\n3k 1yo 1kmark 1k\n4k 1kmark 1k\n6k\n6bo", \
        "5yo\n5k\n3k 1yo 1kmark 1k\n2k 1k2tog 1kmark 1k\n3k 1yo 2k\n6bo"), \
        )


if __name__=="__main__":

    filename, reversed = parse_arguments()
    try:
        if filename:
            myfile = open( filename, "r" )
            mytext = "".join( myfile.readlines() )
            myfile.close()
            try:
                insertcolumn = strick_multiverbessererfromxml( mytext, \
                                                graph_type=mygraphtype)
                oldtranslatorlist = insertcolumn.verbessererlist
            except Exception:
                oldtranslatorlist = []
            del( mytext, myfile )
        else:
            oldtranslatorlist = []
    except FileNotFoundError:
        oldtranslatorlist = []

    from ...verbesserer.multifrommanuals import main as manstomulti
    myersetzer = manstomulti( pairlist, reverse=reversed, side="both", \
                                oldtranslatorlist = oldtranslatorlist )

    if filename:
        myfile = open( filename, "w" )
        myfile.write( myersetzer.toxml_string() )
        myfile.close()

    else:
        print( myersetzer.toxml_string() )
        print( len( myersetzer.verbessererlist ) )

