from extrasfornetworkx import multiverbesserer
from ..strickgraph.strickgraph_base import stricksubgraph
import itertools
import math
from .verbesserer_class import strickalterator

class StrickgraphVerbessererException( Exception ):
    def __init__( self, mymultiverbesserer, mystrickgraph, markednode, *args ):
        super().__init__( mymultiverbesserer, mystrickgraph, markednode, *args )
        self.usedverbesserer = mymultiverbesserer
        self.usedstrickgraph = mystrickgraph
        self.markednodeinstrickgraph = markednode

try:
    import matplotlib.pyplot as plt
    from ..visualizer.graph_2d import easygraph
    IMPORTEDMATPLOTLIB = True
except ModuleNotFoundError as err:
    IMPORTEDMATPLOTLIB = False
    #i want here to make import optional
    raise err


class strick_multiverbesserer( multiverbesserer ):
    def __init__( self, verbessererlist, name=None ):
        if isinstance( verbessererlist, multiverbesserer ):
            isintruth_a_multiverbesserer = verbessererlist
            super().__init__( isintruth_a_multiverbesserer.verbessererlist )
        else:
            super().__init__( verbessererlist )
        self.name = name

    def print_with_matplotlib( self, show = True, useoldgraph=True, \
                                                        tmpplotinfo=None ):
        """visualize with matplot"""
        import matplotlib.pyplot as plt
        from ..visualizer.graph_2d import easygraph
        nrows = math.ceil( math.sqrt(len( self.verbessererlist)+1) )
        nrows = max( 2, nrows )
        fig, axs = plt.subplots( nrows=nrows, ncols=nrows )
        fig.suptitle( self.name )
        axs =iter(itertools.chain( *axs ))
        for verbesserer in self.verbessererlist:
            if useoldgraph:
                usedgraph = verbesserer.oldgraph
            else:
                usedgraph = verbesserer.newgraph
            tmpplotinfo = easygraph( usedgraph, \
                            myplotinfo = tmpplotinfo, \
                            show = False, ax = axs.__next__(), \
                            marked_nodes=["0"] )#?
        self.__plot_legend( tmpplotinfo, axs.__next__() )
        if show:
            plt.show()
        return tmpplotinfo

    def replace_in_graph_with_exception( self, mystrickgraph, markednode ):
        """replace in graph

        :raises: StrickgraphVerbessererException
        """
        suc, info = self.replace_in_graph_withinfo( mystrickgraph, markednode ) 
        if not suc:
            raise StrickgraphVerbessererException( self, mystrickgraph, \
                                                            markednode)#, info )

    def __plot_legend( self, myplotinfo, axis ):
        for stitchname, mystyle in myplotinfo.stitchstyle.items():
            axis.scatter(tuple(),tuple(), label=stitchname, \
                            color = mystyle["node_color"], \
                            marker= mystyle["node_shape"] )
        axis.legend()

    def print_compare_to_graph_at_position( self, graph, marknode ):
        """plot helping to understand problems"""
        tmpplotinfo = self.print_with_matplotlib( show = False )
        easygraph( graph, marked_nodes =[ marknode ], \
                            myplotinfo = tmpplotinfo )
    @classmethod
    def from_xmlstring( cls, xmlstr: str,graph_type=stricksubgraph, name=None ):
        """Create multiverbesserer from xml string"""
        multi = multiverbesserer.from_xml( xmlstr, graph_type=graph_type )
        return cls( multi, name )


    @classmethod
    def from_manuals( cls, pairlist, reverse=False, side="both", \
                        oldtranslatorlist=[] ):
        if side == "both":
            usedsides = ("left", "right")
        elif side == "right":
            usedsides = ("right", )
        elif side == "left":
            usedsides = ("left", )
        else:
            raise KeyError( "'side' must be 'both', 'right' or 'left'." )

        from importlib.resources import read_text
        from .. import verbesserer as main
        from ..strickgraph.load_stitchinfo import myasd as stitchinfo
        xml_string = read_text( main, "markstitches.xml" )
        stitchinfo.add_additional_resources( xml_string )
        ersetzerlist = []
        for old_manual_str, new_manual_str in pairlist:
            for myside in usedsides:
                try:
                    if oldtranslatorlist:
                        foundtranslator = _tryoldtranslator( oldtranslatorlist,\
                                                myside,\
                                                old_manual_str, new_manual_str,\
                                                stitchinfo, reverse=reverse )
                    else:
                        foundtranslator = None
                    if foundtranslator:
                        ersetzerlist.append( foundtranslator )
                    else:
                        ersetzerlist.append(\
                                strickalterator.from_manuals( \
                                old_manual_str, new_manual_str, \
                                stitchinfo, \
                                startside=myside, reversed = reverse )
                                )
                except Exception as err:
                    print( err.args )
                    raise Exception("happend at %s" %( repr((old_manual_str, \
                                        new_manual_str)) ) ) from err

        return cls( ersetzerlist )


def _tryoldtranslator( translatorlist, startside, oldmanstr, newmanstr, \
                                        stitchinfo, reverse=False ):
    trystrick = frommanual( oldmanstr, stitchinfo, manual_type="machine", \
                                startside = startside, reversed=reverse )
    startpoint = _start_at_marked( trystrick )
    targetstrick = frommanual( newmanstr, stitchinfo, manual_type="machine", \
                                startside = startside, reversed=reverse )
    _start_at_marked( targetstrick ) #just to replace marked stitches
    for trans in translatorlist:
        asd = copy.deepcopy( trystrick )
        succ, info = trans.replace_in_graph_withinfo( asd, startpoint )
        if succ:
            if asd == targetstrick:
                return trans
    return None














def strick_multiverbessererfromxml( xmlstr, graph_type=stricksubgraph, name=None ):
    multi = multiverbesserer.from_xml( xmlstr, graph_type=graph_type )
    return strick_multiverbesserer( multi, name )
