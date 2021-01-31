import pkg_resources
from ..verbesserer import verbessererfromxml

def iterable_from_resources( resources_list ):
    for resource in resources_list:
        tmpstream = pkg_resources.resource_stream( __name__, \
                                        resource )
        myverb = verbessererfromxml( tmpstream )
        tmpstream.close()
        yield myverb
        


_insertcolumn_resources = [\
        "verbesserer/insertcolumn/columnstartleft.xml", \
        "verbesserer/insertcolumn/columnstartright.xml", \
        "verbesserer/insertcolumn/continuationleft.xml", \
        "verbesserer/insertcolumn/continuationright.xml", \
        "verbesserer/insertcolumn/columnstart_strickbottomleft.xml", \
        "verbesserer/insertcolumn/columnstart_strickbottomright.xml", \
        ]

insertcolumn_rowforrow = \
            list( iterable_from_resources( _insertcolumn_resources ) )

