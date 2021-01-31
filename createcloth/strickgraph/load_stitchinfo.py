"""
This module should load the infos about the given stitchtypes
extra stitchtypes can be imported via xml(not implemented yet)
:vartype types: list:
:vartype edges: dictionary
:vartype upedges: dictionary
:vartype downedges: dictionary
:vartype symbol: dictionary
:ivar types: a list of all possible stitchtypes
:ivar edges: maps stitchtype on the number of edges
:ivar upedges: maps stitchtype on number of upedges
:ivar downedges: maps stitchtype on number of downedges
:ivar symbol: maps stitchtype on used char for manuals
:todo: importing stitches should possible contain prepacked and local files
"""
import xml.etree.ElementTree as __ET
import pkg_resources
import io as __io
def __sum_all_edges( stitchtype ):
    return 2+ int( stitchtype.get( "upedges" ) ) \
            + int( stitchtype.get( "downedges" ) )

namespace = "whitegobosstitchtypes"


def main():
    global namespace
    global myresources
    global __stitchinfo

    myresources = __ET.Element("myresources")

    stream = pkg_resources.resource_stream( __name__, "stitchdata/stitches.xml")
    #__stitchinfo = __ET.parse( stream ).getroot()
    #myresources.append(__ET.parse( stream ).getroot())

    add_additional_resources( stream )
    stream.close()
    #__stitchinfo = __ET.parse("stitches.xml").getroot()

    update_data()



def update_data():
    global types
    global edges
    global upedges
    global downedges
    global symbol
    global extrainfo

    types = [ stitchtype.get( "name" ) for stitchtype in __stitchinfo ]

    edges = { stitchtype.get( "name" ):__sum_all_edges(stitchtype) \
                    for stitchtype in __stitchinfo }
    upedges = { stitchtype.get( "name" ):int( stitchtype.get( "upedges" ) )
                    for stitchtype in __stitchinfo }
    downedges = { stitchtype.get( "name" ):int( stitchtype.get( "downedges" ) )
                    for stitchtype in __stitchinfo }
    symbol = { stitchtype.get( "name" ):stitchtype.get( "manualchar" )
                    for stitchtype in __stitchinfo }
    extrainfo = {}
    for stitchinfo in __stitchinfo:
        tmpextras = stitchinfo.findall("{" + namespace + "}extraoption")
        tmpstitchextras = {}
        for extra in tmpextras:
            tmpstitchextras.update({ extra.get("key"): extra.get("value") })
        extrainfo.update({ stitchinfo.get("name"): tmpstitchextras })


    #extrainfo = { stitchtype.get( "name" ):{}
    #                for stitchtype in __stitchinfo }

def add_additional_resources( xml ):
    """
    :type xml: see _addition_resources_functiondict.keys()
    """
    global __stitchinfo
    _addition_resources_functiondict[ type(xml) ]( xml )
    __stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
    update_data()


def _add_additional_resources_bufferedReader( xml ):
    """
    :type xml: __io.BufferedReader
    """
    myresources.append(__ET.parse( xml ).getroot())
_addition_resources_functiondict={ \
                __io.BufferedReader:_add_additional_resources_bufferedReader }
def _add_additional_resources_TextIOWrapper( xml ):
    """
    :type xml: __io.TextIOWrapper
    """
    myresources.append(__ET.parse( xml ).getroot())
_addition_resources_functiondict.update({ \
                __io.TextIOWrapper:_add_additional_resources_TextIOWrapper })

def _add_additional_resources_string( xml ):
    """
    :type xml: str
    """
    myresources.append( __ET.fromstring( xml ) )
_addition_resources_functiondict.update({\
                str: _add_additional_resources_string })

happendtest = False
try:
    happend
except NameError:
    happend = None
    happendtest = True
if happendtest:
    main()
