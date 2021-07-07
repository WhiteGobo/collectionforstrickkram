import pkg_resources
import os.path
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
        ("3yo 1yomark 1yo\n3k 1yo 2k\n6k\n6bo", \
        "4yo 1yomark 1yo\n6k\n6k\n6bo"), \
        \
        ("4yo 1yomark 1yo\n6k\n6k\n6bo", \
        "5yo 1yomark 1yo\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n6k\n6k\n2bo 1b2o 1bomark 1bo", \
        "6yo\n6k\n6k\n4bo 1bomark 1bo"), \
        \
        ("6yo\n6k\n6k\n4k 1kmark 1k\n6bo", \
        "6yo\n6k\n6k\n4k 1yo 1kmark 1k\n3bo 1b2o 2bo"), \
        \
        ("5yo\n5k\n3k 1yo 2k\n4k 1kmark 1k\n6bo", \
        "5yo\n5k\n3k 1yo 2k\n4k 1yo 1kmark 1k\n3bo 1b2o 2bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 2k\n4k 1kmark 1k\n6bo", \
        "7yo\n7k\n3k 1k2tog 2k\n4k 1yo 1kmark 1k\n3bo 1b2o 2bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 2k\n2k 1k2tog 1kmark 1k\n5bo", \
        "7yo\n7k\n3k 1k2tog 2k\n4k 1kmark 1k\n2bo 1b2o 2bo"), \
        \
        ("8yo\n4k 1k2tog 2k\n3k 1k2tog 2k\n4k 1kmark 1k\n6k\n6bo", \
        "8yo\n4k 1k2tog 2k\n3k 1k2tog 2k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 2k\n2bo 1b2o 1bomark 1bo", \
        "7yo\n7k\n3k 1k2tog 2k\n4bo 1bomark 1bo"), \
        ("6yo\n6k\n6k\n2bo 1b2o 1bomark 1bo", \
        "6yo\n6k\n6k\n4bo 1bomark 1bo"), \
        ("5yo\n5k\n3k 1yo 2k\n2bo 1b2o 1bomark 1bo", \
        "5yo\n5k\n3k 1yo 2k\n4bo 1bomark 1bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n6k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5bo"), \
        ("6yo\n6k\n6k\n4k 1kmark 1k\n6k\n2k 1k2tog 2k\n5k\n5bo", \
        "6yo\n6k\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5k\n5bo"), \
        \
        ("7yo\n3k 1k2tog 2k\n4k 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "7yo\n3k 1k2tog 2k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5bo"), \
        ("6yo\n6k\n4k 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5bo"), \
        \
        ("8yo\n4k 1k2tog 2k\n3k 1k2tog 1kmark 1k\n6k\n6bo", \
        "8yo\n4k 1k2tog 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "7yo\n7k\n5k 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5bo"), \
        \
        ("8yo\n4k 1k2tog 2k\n3k 1k2tog 1kmark 1k\n6k\n6k\n6bo", \
        "8yo\n4k 1k2tog 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 2k\n2k 1k2tog 1kmark 1k\n5k\n1k 1k2tog 2k\n4bo", \
        "7yo\n7k\n3k 1k2tog 2k\n4k 1kmark 1k\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 1kmark 1k\n6k\n6bo", \
        "7yo\n7k\n5k 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n4k 1yo 2k\n7k\n7bo", \
        "6yo\n4k 1yo 2k\n5k 1kmark 1k\n7k\n7k\n7bo"), \
        ("6yo\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6bo", \
        "6yo\n4k 1yo 2k\n5k 1kmark 1k\n7k\n3k 1k2tog 2k\n6bo"), \
        ("7yo\n7k\n3k 1k2tog 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6bo", \
        "7yo\n7k\n5k 1kmark 1k\n7k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n6k\n2k 1k2tog 2k\n5bo", \
        "6yo\n4k 1yo 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n2k 1k2tog 2k\n5bo"), \
        \
        ("6yo\n6k\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n6k\n2bo 1b2o 2bo", \
        "6yo\n6k\n4k 1yo 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n2bo 1b2o 2bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 1kmark 1k\n6k\n2bo 1b2o 2bo", \
        "7yo\n7k\n5k 1kmark 1k\n3k 1k2tog 2k\n2bo 1b2o 2bo"), \
        \
        ("6yo\n6k\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n4k 1yo 2k\n7k\n3k 1k2tog 1kmark 1k\n6bo", \
        "6yo\n4k 1yo 2k\n7k\n5k 1kmark 1k\n3bo 1b2o 2bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n4k 1kmark 1k\n6k\n6k\n6bo", \
        "6yo\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("4yo 1yomark 1yo\n6k\n6k\n6k\n6bo", \
        "5yo 1yomark 1yo\n3k 1k2tog 2k\n6k\n6k\n6bo"), \
        \
        ("7yo\n3k 1k2tog 1kmark 1k\n6k\n6k\n6bo", \
        "7yo\n5k 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n6k\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n6k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n4k 1yo 2k\n7k\n3k 1k2tog 1kmark 1k\n6k\n6k\n6bo", \
        "6yo\n4k 1yo 2k\n7k\n5k 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n4k 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6bo", \
        "6yo\n4k 1yo 1kmark 1k\n4k 1k 2k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n4k 1k 2k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n4k 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6k\n6bo", \
        "6yo\n4k 1yo 1kmark 1k\n4k 1k 2k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n4k 1yo 2k\n3k 1k2tog 2k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n4k 1k 2k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n4k 1kmark 1k\n4k 1yo 2k\n7k\n3k 1k2tog 2k\n6bo", \
        "6yo\n4k 1yo 1kmark 1k\n4k 1k 2k\n7k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n6k\n4k 1kmark 1k\n4k 1yo 2k\n7k\n3k 1k2tog 2k\n6bo", \
        "6yo\n6k\n4k 1yo 1kmark 1k\n4k 1k 2k\n7k\n3k 1k2tog 2k\n6bo"), \
        \
        ("5yo\n5k\n3k 1yo 2k\n2k 1k2tog 1kmark 1k\n5bo", \
        "5yo\n5k\n3k 1yo 2k\n4k 1kmark 1k\n2bo 1b2o 2bo"), \
        \
        ("7yo\n7k\n3k 1k2tog 1kmark 1k\n4k 1yo 2k\n7k\n7bo", \
        "7yo\n7k\n5k 1kmark 1k\n7k\n7k\n7bo"), \
        \
        )


#def tryoldtranslator( translatorlist, startside, oldmanstr, newmanstr, \
#                                        stitchinfo, reverse=False ):
#    trystrick = frommanual( oldmanstr, stitchinfo, manual_type="machine", \
#                                startside = startside, reversed=reverse )
#    startpoint = _start_at_marked( trystrick )
#    targetstrick = frommanual( newmanstr, stitchinfo, manual_type="machine", \
#                                startside = startside, reversed=reverse )
#    _start_at_marked( targetstrick ) #just to replace marked stitches
#    for trans in translatorlist:
#        asd = copy.deepcopy( trystrick )
#        succ, info = trans.replace_in_graph_withinfo( asd, startpoint )
#        if succ:
#            if asd == targetstrick:
#                return trans
#    return None


if __name__=="__main__":

    filename, reversed = parse_arguments()
    if os.path.isfile( filename ):
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
