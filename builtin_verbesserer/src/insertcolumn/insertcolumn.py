import pkg_resources
from ....verbesserer import manualtoersetzer, verbesserungtoxml, \
                        verbessererfromxml
from ....strickgraph import load_stitchinfo as stitchinfo
from extrasfornetworkx import multiverbesserer

doublefilelist=[\
    ("columncontinuation.knitmanual", \
    "columncontinuation_target.knitmanual"),\
    ("columncontinuation_bottom.knitmanual", \
    "columncontinuation_bottom_target.knitmanual"),\
    ("columnstart_bottom.knitmanual", \
    "columnstart_bottom_target.knitmanual"),\
    ("columnstart_middle.knitmanual", \
    "columnstart_middle_target.knitmanual"),\
    ("columncontin_further.knitmanual", \
    "columncontin_further_target.knitmanual"), \
    ]

markedstitches_file = pkg_resources.resource_stream( __name__, \
                            "markstitches.xml" )
stitchinfo.add_additional_resources( markedstitches_file )
markedstitches_file.close()


ersetzerlist = []
for pair in doublefilelist:
    try:
        new_manual_str = pkg_resources.resource_string( __name__, \
                        pair[1],\
                        ).decode("utf-8")
        old_manual_str = pkg_resources.resource_string( __name__, \
                        pair[0],\
                        ).decode("utf-8")

        ersetzerlist.append(\
                manualtoersetzer( old_manual_str, new_manual_str,\
                startside="left" )
                )
        ersetzerlist.append(\
                manualtoersetzer( old_manual_str, new_manual_str,\
                startside="right")
                )
    except Exception as err:
        err.args = ( *err.args, "happend at %s" %( repr(pair) ) )
        raise err

myersetzer = multiverbesserer( ersetzerlist )
print( myersetzer.toxml_string() )
