import py_trees as pyt
from py_trees.common import Status
from ..strickgraph import tomanual
from ..visualizer import myvis3d
from ..visualizer import easygraph

from ..builtin_verbesserer import insertcolumn_left as verb_insertcolumn_left
from ..builtin_verbesserer import insertcolumn_right as verb_insertcolumn_right
from ..builtin_verbesserer import removecolumn_left as verb_removecolumn_left
from ..builtin_verbesserer import removecolumn_right as verb_removecolumn_right

from . import work_relax
from .work_relax import find_outerline_tension_symmetry, \
        add_column_left_side, \
        add_column_right_side, \
        check_border_type1, \
        border_type1_expansionplaces, \
        find_outerline_lowtension_symmetry, \
        remove_column_both_sides

mygrid = None
mysurfacemap = None
shortcolumn_bottom, shortcolumn_top = None, None


def main( grid, surfacemap ):
    global mygrid
    mygrid = grid
    global mysurfacemap
    mysurfacemap = surfacemap

    mybrain = simpleangepasst_behatree()

    def mumu( tree ):
        tree.display( show_status=True )
        print( tomanual( mygrid , manual_type="machine") )
    try:
        mybrain.tick_tock( \
                    period_ms = 500, \
                    #number_of_iterations = pyt.trees.CONTINUOUS_TICK_TOCK, \
                    number_of_iterations = 7,\
                    pre_tick_handler = None, \
                    post_tick_handler = mumu, \
                    )
    except Exception as err:
        mybrain.display( show_status=True )
        print( tomanual( mygrid , manual_type="machine") )
        print( err.args )
        raise err
        pass
    print( tomanual( mygrid , manual_type="machine" ))
    myvis3d( mygrid )


    #mybrain.display()





class simpleangepasst_behatree( pyt.trees.BehaviourTree ):
    def __init__( self ):
        self.myroot = pyt.composites.Sequence( name="asd" )
        relaxator = pyt.composites.Selector( name="relaxed" )
        optimiser = pyt.composites.Selector( name="optimisegrid" )
        qwe = plotdings( name = "plot" )
        self.myroot.add_children([ relaxator, optimiser ])

        plusshower = pyt.composites.Sequence( name="qq" )
        plusshower.add_children([ \
                relax( name = "relax..." ), \
                #qwe, \
                ])

        relaxator.add_children([
                isrelaxed( name = "isrelaxed" ), \
                plusshower, \
                ])


        #shortcolumn_seq = pyt.composites.Sequence( name="shortcolumn_remove" )
        #shortcolumn_seq.add_children([ 
        #        find_shortcolumn( name="removercontroller" ), \
        #        remove_shortcolumn( name="remover 1"), \
        #    ])
        #optimiser.add_children([ shortcolumn_seq ])

        shortcolumn_seq = pyt.composites.Sequence( name="shortcolumn_adder" )
        shortcolumn_seq.add_children([ 
                find_shortcolumn( name="addercontroller" ), \
                add_shortcolumn( name="adder 1"), \
            ])

        shortcolumnremover_seq = pyt.composites.Sequence( name="shortcolumn_remover" )
        shortcolumnremover_seq.add_children([ 
                find_rowonbothsidetensiontoolow( name="find too low tension" ),\
                remove_shortcolumn( name="remover 1"), \
            ])

        optimiser.add_children([ shortcolumn_seq, shortcolumnremover_seq ])
        super().__init__( root = self.myroot )

        self.myroot.setup_with_descendants()

    def display( self, show_status=False ):
        print( pyt.display.unicode_tree( root=self.myroot, \
                                        show_status=show_status))

class passingtime( pyt.behaviour.Behaviour ):
    def update( self ):
        return Status.SUCCESS


class plotdings( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        try:
            myvis3d( mygrid )
        except Exception as err:
            raise err
            print( err.args )
        return Status.SUCCESS


class relax( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        global mysurfacemap

        try:
            work_relax.relaxgrid( mygrid, mysurfacemap )
        except Exception as err:
            err.args = ( *err.args, mygrid.nodes() )
            raise err

        return Status.SUCCESS

class isrelaxed( pyt.behaviour.Behaviour ):
    def setup( self ):
        self.isrelaxed = False

    def update( self ):
        if self.isrelaxed:
            return Status.SUCCESS
        else:
            #self.isrelaxed = True
            return Status.FAILURE

        return
        grid = None
        if work_relax.isrelaxedenough( grid ):
            return Status.SUCCESS
        else:
            return Status.FAILURE


class remove_shortcolumn( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        global shortcolumn_bottom, shortcolumn_top
        shortcolumn_top = min( shortcolumn_top, len( mygrid.get_rows() )-1 )
        if remove_column_both_sides( mygrid, shortcolumn_bottom, shortcolumn_top ):
            return Status.SUCCESS
        else:
            raise Exception( "This shouldnt happen" )
            return Status.FAILURE

class add_shortcolumn( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        global shortcolumn_bottom, shortcolumn_top
        shortcolumn_top = min( shortcolumn_top, len( mygrid.get_rows() )-1 )
        if not add_column_right_side( mygrid, shortcolumn_bottom, \
                                        shortcolumn_top ):
            raise Exception( "This shouldnt happen, right" )
            return Status.FAILURE
        if not add_column_left_side( mygrid, shortcolumn_bottom, \
                                        shortcolumn_top ):
            raise Exception( "This shouldnt happen, left" )
            return Status.FAILURE


        return Status.SUCCESS


class find_rowonbothsidetensiontoolow( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        global shortcolumn_bottom, shortcolumn_top
        try:
            shortcolumn_bottom, shortcolumn_top \
                    = find_outerline_lowtension_symmetry( mygrid )
        except KeyError:
            return Status.FAILURE
        if shortcolumn_bottom == None:
            return Status.FAILURE
        else:
            if check_border_type1( mygrid, shortcolumn_bottom, shortcolumn_top):
                if border_type1_expansionplaces( mygrid )[shortcolumn_top] \
                            != "decrease":
                    return Status.SUCCESS
        return Status.FAILURE


class find_shortcolumn( pyt.behaviour.Behaviour ):
    def update( self ):
        global mygrid
        global shortcolumn_bottom, shortcolumn_top
        try:
            shortcolumn_bottom, shortcolumn_top \
                    = find_outerline_tension_symmetry( mygrid )
            print( shortcolumn_bottom, shortcolumn_top )
        except KeyError:
            return Status.FAILURE
        if shortcolumn_bottom == None:
            return Status.FAILURE
        else:
            if check_border_type1( mygrid, shortcolumn_bottom, shortcolumn_top):
                row_status = border_type1_expansionplaces( mygrid )
                print( row_status, shortcolumn_bottom, shortcolumn_top )
                if row_status[shortcolumn_top] != "decrease"\
                        and row_status[shortcolumn_bottom] != "increase":
                    return Status.SUCCESS
        return Status.FAILURE

if __name__=="__main__":
    main()
