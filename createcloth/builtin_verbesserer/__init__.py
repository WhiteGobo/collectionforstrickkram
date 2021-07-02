from extrasfornetworkx import multiverbessererfromxml
import pkg_resources
from ..strickgraph.strickgraph_base import stricksubgraph as mygraphtype
from ..verbesserer import strick_multiverbessererfromxml

useddecoding = "utf-8"


def load_builtinverbesserer( savename ):
    tmpbytes = pkg_resources.resource_string( __name__, savename )
    myverb = strick_multiverbessererfromxml( \
                                            tmpbytes.decode( useddecoding ),\
                                            graph_type=mygraphtype, \
                                            name = savename )
    return myverb



def load_insertcolumn_right():
    tmpbytes = pkg_resources.resource_string( __name__,"insertcolumn_right.xml")
    insertcolumn = strick_multiverbessererfromxml( \
                                            tmpbytes.decode( useddecoding ),\
                                            graph_type=mygraphtype)
    return insertcolumn




def load_removecolumn_left():
    tmpbytes = pkg_resources.resource_string( __name__, "removecolumn_left.xml")
    removecolumn = strick_multiverbessererfromxml( tmpbytes.decode( useddecoding ),\
                                            graph_type=mygraphtype)
    return removecolumn
def load_removecolumn_right():
    tmpbytes = pkg_resources.resource_string(__name__, "removecolumn_right.xml")
    removecolumn = strick_multiverbessererfromxml( tmpbytes.decode( useddecoding ),\
                                            graph_type=mygraphtype)
    return removecolumn


try:
    removecolumn_left = load_builtinverbesserer( "removecolumn_left.xml" )
except Exception as err:
    print("Warning: couldnt load load_removecolumn_left" )
    pass
try:
    removecolumn_right = load_builtinverbesserer( "removecolumn_right.xml" )
except Exception as err:
    print("Warning: couldnt load load_removecolumn_right" )
    pass

try:
    insertcolumn_left = load_builtinverbesserer( "insertcolumn_left.xml" )
except Exception as err:
    print("Warning: couldnt load load_insercolumn_left" )
    pass

try:
    insertcolumn_right = load_builtinverbesserer( "insertcolumn_right.xml" )
except Exception:
    print("Warning: couldnt load load_insercolumn_right" )
    pass
    #insertcolumn = None

try:
    plain_extension_upperleft = load_builtinverbesserer( "plain_extension_upperleft.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    plain_extension_lowerleft = load_builtinverbesserer( "plain_extension_lowerleft.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    plain_extension_upperright = load_builtinverbesserer( "plain_extension_upperright.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    plain_extension_lowerright = load_builtinverbesserer( "plain_extension_lowerright.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    eaves_extension_lowerleft = load_builtinverbesserer( "eaves_extension_lowerleft.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    eaves_extension_lowerright = load_builtinverbesserer( "eaves_extension_lowerright.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass
try:
    eaves_extension_upperleft = load_builtinverbesserer( "eaves_extension_upperleft.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

try:
    eaves_extension_upperright = load_builtinverbesserer( "eaves_extension_upperright.xml" )
except Exception:
    print("Warning couldnt load plain_extension" )
    pass

