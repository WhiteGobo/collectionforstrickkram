import pkg_resources
from ...verbesserer import manualtoersetzer, verbesserungtoxml, \
                        verbessererfromxml
from ...strickgraph import load_stitchinfo as stitchinfo
from extrasfornetworkx import multiverbesserer
import argparse

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
        "6yo\n6k\n4k 1yo 1kmark 1k\n3k 1k2tog 2k\n6k\n6bo"), \
        \
        ("6yo\n6k\n4k 1yo 2k\n3k 1k2tog 1kmark 1k\n6k\n6bo", \
        "6yo\n6k\n4k 1yo 2k\n5k 1kmark 1k\n3k 1k2tog 2k\n6bo"), \
        \
        ("6yo\n6k\n4k 1yo 2k\n7k\n3k 1k2tog 1kmark 1k\n6bo", \
        "6yo\n6k\n4k 1yo 2k\n7k\n5k 1kmark 1k\n7bo"), \
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
        )




if __name__=="__main__":

    filename, reversed = parse_arguments()

    markedstitches_file = pkg_resources.resource_stream( __name__, \
                                "insertcolumn/markstitches.xml" )
    stitchinfo.add_additional_resources( markedstitches_file )
    markedstitches_file.close()
    ersetzerlist = []
    for old_manual_str, new_manual_str in pairlist:
        try:
            ersetzerlist.append(\
                    manualtoersetzer( old_manual_str, new_manual_str,\
                    startside="left", reversed = reversed )
                    )
            ersetzerlist.append(\
                    manualtoersetzer( old_manual_str, new_manual_str,\
                    startside="right", reversed = reversed)
                    )
        except Exception as err:
            err.args = ( *err.args, "happend at %s" %( \
                        repr((old_manual_str, new_manual_str)) ) )
            raise err

    myersetzer = multiverbesserer( ersetzerlist )
    print( len(myersetzer.verbessererlist ))
    if filename:
        myfile = open( filename, "w" )
        myfile.write( myersetzer.toxml_string() )
        myfile.close()

    else:
        print( myersetzer.toxml_string() )
        print( len( myersetzer.verbessererlist ) )
