from extrasfornetworkx import multiverbessererfromxml
import pkg_resources
from ..strickgraph.strickgraph_base import stricksubgraph as mygraphtype
from ..verbesserer import strick_multiverbessererfromxml

useddecoding = "utf-8"


def load_insertcolumn_left():
    tmpbytes = pkg_resources.resource_string( __name__, "insertcolumn_left.xml")
    insertcolumn = strick_multiverbessererfromxml( \
                                            tmpbytes.decode( useddecoding ),\
                                            graph_type=mygraphtype)
    return insertcolumn


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
    removecolumn_left = load_removecolumn_left()
except Exception as err:
    print("Warning: couldnt load load_removecolumn_left" )
    pass
try:
    removecolumn_right = load_removecolumn_right()
except Exception as err:
    print("Warning: couldnt load load_removecolumn_right" )
    pass

try:
    insertcolumn_left = load_insertcolumn_left()
except Exception as err:
    print("Warning: couldnt load load_insercolumn_left" )
    pass
try:
    insertcolumn_right = load_insertcolumn_right()
except Exception:
    print("Warning: couldnt load load_insercolumn_right" )
    pass
    #insertcolumn = None
