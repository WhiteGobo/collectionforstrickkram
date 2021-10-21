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
import pkg_resources
import importlib.resources
import io as __io

namespace = "whitegobosstitchtypes"

class _singlestitchdata():
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
        tmpextras = self.stitchelement.findall( "{%s}extraoption"% (namespace) )
        tmpstitchextras = {}
        for extra in tmpextras:
            tmpstitchextras.update({ extra.get("key"): extra.get("value")})
        return tmpstitchextras
    extrainfo = property( fget = _get_extrainfo )

class _strickdata():
    def __init__( self, strickresources ):
        self.strickresources = strickresources
        #strickresources.get

    def _get_name( self ):
        return self.strickresources.get( "name" )
    name = property( fget=_get_name )

    def keys( self ):
        return self.strickresources.keys()
    def __contains__( self, key ):
        return key in self.strickresources.keys()
        pass
    def __getitem__( self, key ):
        return self.strickresources.get( key )
    #def __setitem__( self, key, attribute ):
    #    pass


class stitchdatacontainer():
    def __init__( self, myresources ):
        if myresources == None:
            myresources = _ET.Element("myresources")
        self.myresources = myresources


    def _get_strickdata( self ):
        stitchinfo =list( self.myresources.iter( "{"+namespace +"}strickdata"))
        mylist = [ _strickdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata for stdata in mylist }
        return mydict
        #return self._symbol
    strickdata = property( fget = _get_strickdata )


    @classmethod
    def from_xmlfile( cls, filepath ):
        root = _ET.parse( filepath )#.getroot()
        #for i in root.findall( "{" + namespace + "}stitches" ):
            #print( "a",i)
        #for i in root.iter( "{" + namespace + "}stitchtype" ):
        #for i in root.findall( "{" + namespace + "}stitchtype" ):
        #    print( i.get("name"))
        return cls( root )

    def to_xmlfile( self, filepath ):
        _ET.register_namespace( "stitchdata", namespace )
        self.myresources.write( filepath )

    def _get_symbol( self ):
        stitchinfo =list( self.myresources.iter( "{"+namespace +"}stitchtype"))
        mylist = [ _singlestitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.symbol for stdata in mylist }
        return mydict
        #return self._symbol
    symbol = property( fget = _get_symbol )

    def _get_antisymbol( self ):
        antisymbol = dict()
        for stitchid, symbol in self.symbol.items():
            antisymbol[stitchid] = stitchid
            antisymbol[symbol] = stitchid
        return antisymbol
    symbol_to_stitchid = property( fget = _get_antisymbol )

    def _get_types( self ):
        stitchinfo = list( self.myresources.iter( "{"+namespace+"}stitchtype" ))
        mylist = tuple(_singlestitchdata( stelement ).name \
                        for stelement in stitchinfo)
        return mylist
        #return self._types
    types = property( fget = _get_types )

    def _get_upedges( self ):
        stitchinfo = list( self.myresources.iter( "{"+namespace+"}stitchtype" ))
        mylist = [ _singlestitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.upedges for stdata in mylist }
        return mydict
        #return self._upedges
    upedges = property( fget = _get_upedges )

    def _get_downedges( self ):
        stitchinfo = list( self.myresources.iter( "{"+namespace+"}stitchtype" ))
        mylist = [ _singlestitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.downedges for stdata in mylist }
        return mydict
        #return self._downedges
    downedges = property( fget = _get_downedges )

    def _get_extrainfo( self ):
        stitchinfo = list( self.myresources.iter( "{"+namespace+"}stitchtype" ))
        mylist = [ _singlestitchdata( stelement ) for stelement in stitchinfo ]
        mydict = { stdata.name: stdata.extrainfo for stdata in mylist }
        return mydict
        #return self._extrainfo
    extrainfo = property( fget = _get_extrainfo )


    def add_additional_xmlresources( self, xmlstring ):
        root = self.myresources.getroot()
        root.append( _ET.parse( xmlstring ).getroot() )

    def _update_resources():
        raise Exception()
        def __sum_all_edges( stitchtype ):
            return 2+ int( stitchtype.get( "upedges" ) ) \
                    + int( stitchtype.get( "downedges" ) )
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
            #tmpextras = stitchinfo.findall("{" + namespace + "}extraoption")
            tmpextras = stitchinfo.findall( "extraoption", namespace )
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
        root = self.myresources.getroot()
        root.append(_ET.fromstring( xml_string ))


#from . import stitchdata
#with importlib.resources.path( stitchdata, "stitches.xml" ) as filepath:
#    myasd = stitchdatacontainer.from_xmlfile( filepath )
