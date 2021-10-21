import unittest
import tempfile
import os.path

from .load_stitchinfo import stitchdatacontainer
from .. import stitchinfo as stinfo

class TestStitchinfo( unittest.TestCase ):
    def test_saveload_stitchdata( self ):
        stitchinfo = stinfo.basic_stitchdata
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "tmpfile.xml" )
            stitchinfo.to_xmlfile( myfilepath )
            loadedstinfo = stitchdatacontainer.from_xmlfile( myfilepath )

        self.assertEqual( stitchinfo.stitchsymbol, loadedstinfo.stitchsymbol )
        self.assertEqual( stitchinfo.upedges, loadedstinfo.upedges )
        self.assertEqual( stitchinfo.downedges, loadedstinfo.downedges )
        self.assertEqual( stitchinfo.extraoptions, loadedstinfo.extraoptions )

    def test_minimalstitchtypes( self ):
        """
        testing if minimal stitchtype collection is supported
        """
        stitchinfo = stinfo.basic_stitchdata
        for stitchtype in ["knit", "yarnover", "bindoff", "k2tog"]:
            self.assertEqual( True, stitchtype in stitchinfo.stitchtypes )

        strdat = stitchinfo.strickdata["plainknit"]
        self.assertEqual( strdat["stitch"], "knit" )
        self.assertEqual( strdat["startrow"], "yarnover" )
        self.assertEqual( strdat["endrow"], "bindoff" )

        for stitchtype, symbol, up, down, extrainfo in [\
                            ("knit", "k", 1,1,{}), \
                            ("yarnover", "yo",1,0,{}), \
                            ("bindoff", "bo", 0,1,{}), \
                            ("k2tog","k2tog",1,2,{}) ]:
            self.assertEqual( symbol, stitchinfo.symbol[ stitchtype ] )
            self.assertEqual( up, stitchinfo.upedges[ stitchtype ] )
            self.assertEqual( down, stitchinfo.downedges[ stitchtype ] )
            self.assertEqual( extrainfo, stitchinfo.extrainfo[stitchtype])


    @unittest.skip("not implemented yet")
    def test_extrastitchtypes( self ):
        """
        test if i can add succesfully new stitchtypes via xml-file
        :todo: write this method
        """
        myman = "6yo\n1k 1kmark 1k2tog 2k\n1k 1k2tog 2k\n4bo"
        from copy import deepcopy
        stitchinfo = deepcopy( self.stitchinfo )
        from . import stitchdata
        from importlib.resources import read_text
        xml_string = read_text( stitchdata, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )

        asd = strickgraph.strickgraph.from_manual( myman, stitchinfo )
        self.assertEqual( asd.get_alternative_stitchtypes(), {(1, 1): 'knit'} )
        newmanual = asd.copy_with_alternative_stitchtype()\
                        .to_manual( self.stitchinfo)
        brubru = "6yo\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo".splitlines()
        self.assertEqual( newmanual.splitlines(), brubru )

if __name__=="__main__":
    unittest.main()
