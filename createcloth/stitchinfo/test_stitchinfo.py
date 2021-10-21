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


if __name__=="__main__":
    unittest.main()
