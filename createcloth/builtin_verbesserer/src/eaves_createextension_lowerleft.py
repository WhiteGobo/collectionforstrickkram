from ...strickgraph.strickgraph_base import stricksubgraph as mygraphtype
import argparse
from ...verbesserer.multifrommanuals import main as manstomulti
from ...verbesserer import strick_multiverbessererfromxml

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
        #("4yo\n4k\n4k\n1k 1kmark 1yo 2k\n3k 1yo 2k\n6bo", \
        #"4yo\n4k\n4k\n1k 1kmark 2k 2yo\n6k\n6bo"), \
        #("4yo\n4k\n4k\n1k 1kmark 1yo 2k\n3k 1yo 2k\n6k\n6bo", \
        #"4yo\n4k\n4k\n1k 1kmark 2k 2yo\n6k\n6k\n6bo"), \
        #("4yo\n4k\n4k\n1k 1kmark 1yo 2k\n3k 1yo 2k\n4k 1yo 2k\n7bo", \
        #"4yo\n4k\n4k\n1k 1kmark 2k 2yo\n6k\n4k 1yo 2k\n7bo"), \
        #("4yo\n1k 1kmark 1yo 2k\n3k 1yo 2k\n6k\n6bo", \
        #"4yo\n1k 1kmark 2k 2yo\n6k\n6k\n6bo"), \
        #("4yo\n1k 1kmark 1yo 2k\n3k 1yo 2k\n4k 1yo 2k\n7bo", \
        #"4yo\n1k 1kmark 2k 2yo\n6k\n4k 1yo 2k\n7bo"), \
        ("3yo\n3k\n1k 1yo 2k\n1k 1kmark 1yo 2k\n3k 1yo 2k\n6k\n6bo", \
        "3yo\n3k\n1k 1yo 2k\n1k 1kmark 2k 2yo\n6k\n6k\n6bo"), \
        \
        ("4yo\n1k 1kmark 1yo 2k\n3k 1yo 2k\n6k\n6k\n6bo", \
        "4yo\n1k 1kmark 2k 2yo\n6k\n6k\n6k\n6bo"), \
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
                except Exception as err:
                    oldtranslatorlist = []
                    raise err
                del( mytext, myfile )
        except FileNotFoundError as err:
            pass

    side = "right"
    if reversed:
        side = "left"
    reversed = not reversed

    
    myersetzer = manstomulti( pairlist, reverse=reversed, side=side, \
                                oldtranslatorlist = oldtranslatorlist )

    
    if filename:

        myfile = open( filename, "w" )
        myfile.write( myersetzer.toxml_string() )
        myfile.close()

    else:
        print( myersetzer.toxml_string() )
        print( len( myersetzer.verbessererlist ) )
