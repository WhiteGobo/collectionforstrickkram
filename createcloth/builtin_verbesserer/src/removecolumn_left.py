import pkg_resources
from ...verbesserer import manualtoersetzer, verbesserungtoxml, \
                        verbessererfromxml
from ...strickgraph import load_stitchinfo as stitchinfo
from extrasfornetworkx import multiverbesserer

a1 = "6yo\n6k\n1k 1kmark 4k\n6k\n6k\n6bo"
a2 = "6yo\n6k\n1k 1kmark 1k2tog 2k\n2k 1yo 3k\n6k\n6bo"

b1 = "6yo\n6k\n2k 1k2tog 2k\n1k 1kmark 1yo 3k\n6k\n6k\n6bo"
b2 = "6yo\n6k\n2k 1k2tog 2k\n1k 1kmark 3k\n2k 1yo 3k\n6k\n6bo"

c1 = "6yo\n6k\n2k 1k2tog 2k\n2k 3k\n1k 1kmark 1yo 3k\n6k\n6bo"
c2 = "6yo\n6k\n2k 1k2tog 2k\n2k 3k\n1k 1kmark 3k\n2k 1yo 3k\n6bo"

d1 = "6yo\n6k\n2k 1k2tog 2k\n5k\n5k\n1k 1kmark 1yo 3k\n6bo"
d2 = "6yo\n6k\n2k 1k2tog 2k\n5k\n5k\n1k 1kmark 3k\n5bo"

e1 = "1yo 1yomark 4yo\n6k\n6k\n6bo"
e2 = "1yo 1yomark 3yo\n2k 1yo 3k\n6k\n6bo"

f1 = "5yo\n1k 1kmark 1yo 3k\n6k\n6k\n6bo"
f2 = "5yo\n1k 1kmark 3k\n2k 1yo 3k\n6k\n6bo"

g1 = "6yo\n1k 1kmark 4k\n6k\n6k\n6bo"
g2 = "6yo\n1k 1kmark 1k2tog 2k\n2k 1yo 3k\n6k\n6bo"

pairlist = ((a1, a2), (b1, b2), (c1, c2), (d1, d2), (e1, e2), \
            (f1, f2), (g1, g2),)


if __name__=="__main__":
    markedstitches_file = pkg_resources.resource_stream( __name__, \
                                "insertcolumn/markstitches.xml" )
    stitchinfo.add_additional_resources( markedstitches_file )
    markedstitches_file.close()
    ersetzerlist = []
    for old_manual_str, new_manual_str in pairlist:
        try:
            ersetzerlist.append(\
                    manualtoersetzer( old_manual_str, new_manual_str,\
                    startside="left" )
                    )
            ersetzerlist.append(\
                    manualtoersetzer( old_manual_str, new_manual_str,\
                    startside="right")
                    )
        except Exception as err:
            err.args = ( *err.args, "happend at %s" %( \
                        repr((old_manual_str, new_manual_str)) ) )
            raise err

    myersetzer = multiverbesserer( ersetzerlist )
    print( myersetzer.toxml_string() )
