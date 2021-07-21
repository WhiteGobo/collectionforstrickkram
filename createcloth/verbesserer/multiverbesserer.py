from extrasfornetworkx import multiverbesserer
from ..strickgraph.strickgraph_base import stricksubgraph
import itertools
import math

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


def strick_multiverbessererfromxml( xmlstr, graph_type=stricksubgraph, name=None ):
    multi = multiverbesserer.from_xml( xmlstr, graph_type=graph_type )
    return strick_multiverbesserer( multi, name )
