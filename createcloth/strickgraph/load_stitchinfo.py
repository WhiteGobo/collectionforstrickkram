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
import xml.etree.ElementTree as _ET
import xml.etree.ElementTree as brubru
import pkg_resources
import io as __io
def __sum_all_edges( stitchtype ):
    return 2+ int( stitchtype.get( "upedges" ) ) \
            + int( stitchtype.get( "downedges" ) )

namespace = "whitegobosstitchtypes"

class stitchdata():
    def __init__( self, stitchelement ):
        self.stitchelement = stitchelement

    def _get_name( self ):
        return self.stitchelement.get( "name" )
    name = property( fget = _get_name )

    def _get_symbol( self ):
        return self.stitchelement.get( "manualchar" )
    symbol = property( fget = _get_symbol )

    def _get_downedges( self ):
        return int( self.stitchelement.get( "downedges" ) )
    downedges = property( fget = _get_downedges )

    def _get_upedges( self ):
        return int( self.stitchelement.get( "upedges" ) )
    upedges = property( fget = _get_upedges )

    def _get_sumedges( self ):
        return 2 + self._get_upedges() + self._get_downedges()
    sumedges = property( fget = _get_sumedges )

    def _get_extrainfo( self ):
        tmpextras = self.stitchelement.findall("{" + namespace + "}extraoption")
        tmpstitchextras = {}
        for extra in tmpextras:
            tmpstitchextras.update({ extra.get("key"): extra.get("value")})
        return tmpstitchextras
    extrainfo = property( fget = _get_extrainfo )


class stitchdatacontainer():
    def __init__( self, myresources ):

        if myresources == None:
            myresources = _ET.Element("myresources")
        self.myresources = myresources
        #self._symbol = symbol
        #self._types = types
        #self._upedges = upedges
        #self._downedges = downedges
        #self._extrainfo = extrainfo

    def get_symbol( self ):
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
        mylist = [ stitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.symbol for stdata in mylist }
        return mydict
        #return self._symbol
    symbol = property( fget = get_symbol )

    def get_types( self ):
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
        mylist = tuple(stitchdata( stelement ).name for stelement in stitchinfo)
        return mylist
        #return self._types
    types = property( fget = get_types )

    def get_upedges( self ):
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
        mylist = [ stitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.upedges for stdata in mylist }
        return mydict
        #return self._upedges
    upedges = property( fget = get_upedges )

    def get_downedges( self ):
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
        mylist = [ stitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.downedges for stdata in mylist }
        return mydict
        #return self._downedges
    downedges = property( fget = get_downedges )

    def get_extrainfo( self ):
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ) )
        mylist = [ stitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.extrainfo for stdata in mylist }
        return mydict
        #return self._extrainfo
    extrainfo = property( fget = get_extrainfo )


    def add_additional_xmlresources( self, xmlstring ):
        self.myresources.append( _ET.parse( xmlstring ).getroot() )

    def _update_resources():
        raise Exception()
        stitchinfo = list( myresources.iter( "{" + namespace + "}stitchtype" ))

        types = [ stitchtype.get( "name" ) for stitchtype in __stitchinfo ]
        edges = { stitchtype.get( "name" ): \
                        __sum_all_edges(stitchtype) \
                        for stitchtype in __stitchinfo }
        upedges = { stitchtype.get( "name" ): \
                        int( stitchtype.get( "upedges" ) )
                        for stitchtype in __stitchinfo }
        downedges = { stitchtype.get( "name" ): \
                        int( stitchtype.get( "downedges" ) )
                        for stitchtype in __stitchinfo }
        symbol = { stitchtype.get( "name" ):stitchtype.get( "manualchar" )
                        for stitchtype in __stitchinfo }
        extrainfo = {}
        for stitchinfo in __stitchinfo:
            tmpextras = stitchinfo.findall("{" + namespace + "}extraoption")
            tmpstitchextras = {}
            for extra in tmpextras:
                tmpstitchextras.update({ extra.get("key"): extra.get("value")})
            extrainfo.update({ stitchinfo.get("name"): tmpstitchextras })
        self.extrainfo = extrainfo
        self.upedges = upedges
        self.downedges = downedges
        self.symbol = symbol
        self.types = types
        self.edges = edges

    def add_additional_resources( self, xml_string ):
        self.myresources.append(_ET.fromstring( xml_string ))


def main():
    global namespace
    global myresources
    global __stitchinfo

    myresources = _ET.Element("myresources")

    stream = pkg_resources.resource_stream( __name__,"stitchdata/stitches.xml")
    #__stitchinfo = _ET.parse( stream ).getroot()
    #myresources.append(_ET.parse( stream ).getroot())

    add_additional_resources( stream )
    stream.close()
    #__stitchinfo = _ET.parse("stitches.xml").getroot()

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
    myresources.append(_ET.parse( xml ).getroot())
_addition_resources_functiondict={ \
                __io.BufferedReader:_add_additional_resources_bufferedReader }
def _add_additional_resources_TextIOWrapper( xml ):
    """
    :type xml: __io.TextIOWrapper
    """
    myresources.append(_ET.parse( xml ).getroot())
_addition_resources_functiondict.update({ \
                __io.TextIOWrapper:_add_additional_resources_TextIOWrapper })

def _add_additional_resources_string( xml ):
    """
    :type xml: str
    """
    myresources.append( _ET.fromstring( xml ) )
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


myasd = stitchdatacontainer( myresources )
