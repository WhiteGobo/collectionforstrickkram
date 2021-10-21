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
from typing import Dict, List, Tuple

namespace = "whitegobosstitchtypes"

def translate_elementtree_to_strickdata( myresources: _ET.ElementTree ):
    _ET.register_namespace( "stitchdata", namespace )
    stitchinfo =list( myresources.iter( "{"+namespace +"}strickdata"))
    strickstitch = { a.get('name'): a.get('stitch') for a in stitchinfo }
    strickstart = { a.get('name'): a.get('startrow') for a in stitchinfo }
    strickend = { a.get('name'): a.get('endrow') for a in stitchinfo }

    def get_extraoptions( elem ):
        return {a.get("key"): a.get("value") for a in elem.findall( "{%s}extraoption"% (namespace) )}
    stitchinfo =list( myresources.iter( "{"+namespace +"}stitchtype"))
    stitchsymbol = { a.get('name'): a.get('manualchar') for a in stitchinfo }
    upedges = { a.get('name'): a.get('upedges') for a in stitchinfo }
    downedges = { a.get('name'): a.get('downedges') for a in stitchinfo }
    extraoptions = { a.get('name'): get_extraoptions(a) for a in stitchinfo }

    return strickstitch, strickstart, strickend, \
            stitchsymbol, upedges, downedges, extraoptions


def translate_strickdata_to_elementtree( strickstitch, strickstart, strickend, \
                                stitchsymbol, upedges, downedges, extraoptions):
    assert stitchsymbol.keys() == upedges.keys() == downedges.keys() == extraoptions.keys(), "not every entry has all needed info"
    assert strickstitch.keys() == strickstart.keys() == strickend.keys(), "not every stricktype has all needed info"

    _ET.register_namespace( "stitchdata", namespace )
    root = _ET.Element( "{%s}stitches"%(namespace) )# xmlns='whitegobosstitchtypes'>
    for name in strickstitch.keys():
        stitch = strickstitch[ name ]
        start = strickstart[ name ]
        end = strickend[ name ]
        tmp = _ET.SubElement( root, "{%s}strickdata"%(namespace) )
        tmp.set( "name", name )
        tmp.set( "stitch", stitch )
        tmp.set( "startrow", start )
        tmp.set( "endrow", end )

    for name in stitchsymbol.keys():
        symbol = stitchsymbol[ name ]
        up = str( upedges[ name ] )
        down = str( downedges[ name ] )
        extras = extraoptions[ name ]
        tmp = _ET.SubElement( root, "{%s}stitchtype"%(namespace) )
        tmp.set( "name", name )
        tmp.set( "manualchar", symbol )
        tmp.set( "upedges", up )
        tmp.set( "downedges", down )
        for key, value in extras.items():
            extratmp = _ET.SubElement( tmp, "{%s}extraoption"%(namespace) )
            extratmp.set( "key", key )
            extratmp.set( "value", value )
    return root


class stitchdatacontainer():
    """Object tostore information about stitchtypes

    :ivar stricksymbol: dictionary for name of stitch to corresponding symbol
    :ivar upedges: name of stitch to number upedges
    :ivar downedges: name of stitch to number downedges
    :ivar extraoptions: name to extras
    :ivar strickstitch:
    :ivar strickstart:
    :ivar strickend:
    """
    def __init__( self, strickstitch:Dict[str,str], strickstart:Dict[str,str], \
                    strickend:Dict[str,str], stitchsymbol:Dict[str,str], \
                    upedges:Dict[str,int], downedges:Dict[str,int], \
                    extraoptions:Dict[str,str]):
        assert stitchsymbol.keys() == upedges.keys() == downedges.keys() == extraoptions.keys(), "not every entry has all needed info"
        assert strickstitch.keys() == strickstart.keys() == strickend.keys(), "not every stricktype has all needed info"
        self.strickstitch = strickstitch
        self.strickstart = strickstart
        self.strickend = strickend
        self.stitchsymbol = stitchsymbol
        self.upedges = upedges
        self.downedges = downedges
        self.extraoptions = extraoptions

    def _stitchsymbol_to_name( self ) -> Dict[ str, str ]:
        return { b:a for a,b in self.stitchsymbol }
    stitchsymbol_to_stitchid = property( fget=_stitchsymbol_to_name )
    """Holds dictionary from stitchsymbol zo stitchname"""

    def _get_stitchtypes( self ) -> Tuple[ str ]:
        return tuple( self.stitchsymbol.keys() )
    stitchtypes = property( fget=_get_stitchtypes )
    """Returns all availables stitchtypes"""

    @classmethod
    def from_xmlfile( cls, filepath ):
        """Generator from xmlfile"""
        root = _ET.parse( filepath )#.getroot()

        strickstitch, strickstart, strickend, stitchsymbol, \
                upedges, downedges, extraoptions \
                = translate_elementtree_to_strickdata( root )

        return cls( strickstitch, strickstart, strickend, stitchsymbol, \
                                        upedges, downedges, extraoptions )

    def to_xmlfile( self, filepath ):
        """Saver to xmlfile"""
        _ET.register_namespace( "stitchdata", namespace )
        myelement: _ET.Element = translate_strickdata_to_elementtree( \
                            self.strickstitch, self.strickstart, self.strickend, \
                                self.stitchsymbol, self.upedges, \
                                self.downedges, self.extraoptions )
        root = _ET.ElementTree( myelement )
        root.write( filepath )

    def to_xmlbytes( self ) -> bytes:
        """Saver to xmlbytes"""
        _ET.register_namespace( "stitchdata", namespace )
        myelement: _ET.Element = translate_strickdata_to_elementtree( \
                            self.strickstitch, self.strickstart, self.strickend, \
                                self.stitchsymbol, self.upedges, \
                                self.downedges, self.extraoptions )
        mybytes = myelement.asdf
        return mybytes

