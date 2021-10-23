"""This module should load the infos about the given stitchtypes
extra stitchtypes can be imported via xml(not implemented yet)

"""
import xml.etree.ElementTree as _ET
import pkg_resources
import importlib.resources
import io as __io
from typing import Dict, List, Tuple
from .. import stitchinfo as st

def translate_elementtree_to_strickdata( myresources: _ET.ElementTree ):
    _ET.register_namespace( "stitchdata", st.NAMESPACE )
    stitchinfo =list( myresources.iter( "{"+st.NAMESPACE +"}strickdata"))
    strickstitch = { a.get('name'): a.get('stitch') for a in stitchinfo }
    strickstart = { a.get('name'): a.get('startrow') for a in stitchinfo }
    strickend = { a.get('name'): a.get('endrow') for a in stitchinfo }

    def get_extraoptions( elem ):
        return {a.get("key"): a.get("value") for a in elem.findall( "{%s}extraoption"% (st.NAMESPACE) )}
    stitchinfo =list( myresources.iter( "{"+st.NAMESPACE +"}stitchtype"))
    stitchsymbol = { a.get('name'): a.get('manualchar') for a in stitchinfo }
    upedges = { a.get('name'): int(a.get('upedges')) for a in stitchinfo }
    downedges = { a.get('name'): int(a.get('downedges')) for a in stitchinfo }
    extraoptions = { a.get('name'): get_extraoptions(a) for a in stitchinfo }

    return strickstitch, strickstart, strickend, \
            stitchsymbol, upedges, downedges, extraoptions


def translate_strickdata_to_elementtree( strickstitch, strickstart, strickend, \
                                stitchsymbol, upedges, downedges, extraoptions):
    assert stitchsymbol.keys() == upedges.keys() == downedges.keys() == extraoptions.keys(), "not every entry has all needed info"
    assert strickstitch.keys() == strickstart.keys() == strickend.keys(), "not every stricktype has all needed info"

    _ET.register_namespace( "stitchdata", st.NAMESPACE )
    root = _ET.Element( "{%s}stitches"%(st.NAMESPACE) )# xmlns='whitegobosstitchtypes'>
    for name in strickstitch.keys():
        stitch = strickstitch[ name ]
        start = strickstart[ name ]
        end = strickend[ name ]
        tmp = _ET.SubElement( root, "{%s}strickdata"%(st.NAMESPACE) )
        tmp.set( "name", name )
        tmp.set( "stitch", stitch )
        tmp.set( "startrow", start )
        tmp.set( "endrow", end )

    for name in stitchsymbol.keys():
        symbol = stitchsymbol[ name ]
        up = str( upedges[ name ] )
        down = str( downedges[ name ] )
        extras = extraoptions[ name ]
        tmp = _ET.SubElement( root, "{%s}stitchtype"%(st.NAMESPACE) )
        tmp.set( "name", name )
        tmp.set( "manualchar", symbol )
        tmp.set( "upedges", up )
        tmp.set( "downedges", down )
        for key, value in extras.items():
            extratmp = _ET.SubElement( tmp, "{%s}extraoption"%(st.NAMESPACE) )
            extratmp.set( "key", key )
            extratmp.set( "value", value )
    return root


class stitchdatacontainer():
    """Object tostore information about stitchtypes

    :ivar stitchsymbol: dictionary for name of stitch to corresponding symbol
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
        tmpdict = { a:a for a in self.stitchsymbol.keys() }
        tmpdict.update( { b:a for a,b in self.stitchsymbol.items() } )
        return tmpdict
    stitchsymbol_to_stitchid = property( fget=_stitchsymbol_to_name )
    """Holds dictionary from stitchsymbol and stitchname to stitchname. Used
    for converting manuals to Normalform
    """

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
        _ET.register_namespace( "stitchdata", st.NAMESPACE )
        myelement: _ET.Element = translate_strickdata_to_elementtree( \
                            self.strickstitch, self.strickstart, self.strickend, \
                                self.stitchsymbol, self.upedges, \
                                self.downedges, self.extraoptions )
        root = _ET.ElementTree( myelement )
        root.write( filepath )

    def to_xmlbytes( self ) -> bytes:
        """Saver to xmlbytes"""
        _ET.register_namespace( "stitchdata", st.NAMESPACE )
        myelement: _ET.Element = translate_strickdata_to_elementtree( \
                            self.strickstitch, self.strickstart, self.strickend, \
                                self.stitchsymbol, self.upedges, \
                                self.downedges, self.extraoptions )
        mybytes = myelement.asdf
        return mybytes

