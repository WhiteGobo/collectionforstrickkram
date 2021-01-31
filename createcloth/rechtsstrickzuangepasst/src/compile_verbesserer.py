import sys
sys.path.append("../../..")
from pippackage.verbesserer import manualtoverbesserung, verbesserungtoxml
from pippackage.strickgraph import stitchinfo


verbessererresources = [\
	    ("manuals/insertcolumn_columncontinuation_id.knitmanual", \
        "manuals/insertcolumn_columncontinuation_target.knitmanual", \
        "insertcolumn/continuation"),\
        ("manuals/insertcolumn_columnstart_id.knitmanual", \
        "manuals/insertcolumn_columnstart_target.knitmanual", \
        "insertcolumn/columnstart"),\
        ("manuals/insertcolumn_columnstartstrickbottom_id.knitmanual", \
        "manuals/insertcolumn_columnstartstrickbottom_target.knitmanual", \
        "insertcolumn/columnstart_strickbottom"),\
	]

def main():
    savedir = "../verbesserer/"
    for idname, targetname, savelocation in verbessererresources:
        startside = "right"
        for startside in ["left", "right" ]:
            verbesserer = create_verbesserer( idname, targetname )
            qwe = verbesserungtoxml( verbesserer )
            savefile = open( savedir + savelocation + startside + ".xml", "w" )
            savefile.write( qwe )
            savefile.close()
        



def create_verbesserer( idname, targetname ):
    extrainfo = open( "markstitches.xml", "r" )
    stitchinfo.add_additional_resources( extrainfo )
    extrainfo.close()
    old_manual_file = open( idname )
    new_manual_file = open( targetname )
    #old_manual = [x[:-1].decode("utf-8") for x in old_manual_file]
    #new_manual = [x[:-1].decode("utf-8") for x in new_manual_file]
    old_manual = [x for x in old_manual_file]
    new_manual = [x for x in new_manual_file]
    return manualtoverbesserung( old_manual, new_manual, start_at="marked",\
                                    manual_type="thread", startside="right")


if __name__=="__main__":
	main()
