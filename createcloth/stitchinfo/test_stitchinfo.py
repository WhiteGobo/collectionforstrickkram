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

        self.assertEqual( stitchinfo.strickstitch["plainknit"], "knit" )
        self.assertEqual( stitchinfo.strickstart["plainknit"], "yarnover" )
        self.assertEqual( stitchinfo.strickend["plainknit"], "bindoff" )

        for stitchtype, symbol, up, down, extrainfo in [\
                            ("knit", "k", 1,1,{}), \
                            ("yarnover", "yo",1,0,{}), \
                            ("bindoff", "bo", 0,1,{}), \
                            ("k2tog","k2tog",1,2,{}) ]:
            self.assertEqual( symbol, stitchinfo.stitchsymbol[ stitchtype ] )
            self.assertEqual( up, stitchinfo.upedges[ stitchtype ] )
            self.assertEqual( down, stitchinfo.downedges[ stitchtype ] )
            self.assertEqual( extrainfo, stitchinfo.extraoptions[stitchtype])


    @unittest.skip("not implemented yet")
    def test_extrastitchtypes( self ):
        """test if i can add succesfully new stitchtypes via xml-file

        :todo: write this method
        """
        pass

if __name__=="__main__":
    unittest.main()
