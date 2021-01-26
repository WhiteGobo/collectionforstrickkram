import networkx as netx
import matplotlib.pyplot as plt

mysize = 50

def easygraph( mygrid, show=True, ax = None, marked_nodes=None ):
    if ax == None:
        plt.figure()
    plt.axis("off") # ?
    initpos = give_init_positions( mygrid )
    #initpos = netx.spring_layout( mygrid, k=.01, iterations=50, pos=initpos )
    #netx.draw( mygrid, initpos )
    draw_every_edgetype_different( mygrid, initpos, ax = ax )
    draw_every_stitchtype_different( mygrid, initpos, ax = ax )

    if None != marked_nodes:
        draw_marked_nodes( mygrid, initpos, marked_nodes, ax = ax )
    #netx.draw_networkx_edges( mygrid, initpos )
    plt.legend()
    if show:
        plt.show()


from matplotlib.colors import TABLEAU_COLORS as colorpalett

stitch_style=(\
        {"node_color":colorpalett["tab:blue"], "node_shape":"o"}, \
        {"node_color":colorpalett["tab:orange"], "node_shape":"v"}, \
        {"node_color":colorpalett["tab:green"], "node_shape":"^"}, \
        {"node_color":colorpalett["tab:red"], "node_shape":"<"}, \
        {"node_color":colorpalett["tab:purple"], "node_shape":">"}, \
        {"node_color":colorpalett["tab:brown"], "node_shape":"s"}, \
        {"node_color":colorpalett["tab:pink"], "node_shape":"p"}, \
        {"node_color":colorpalett["tab:gray"], "node_shape":"h"}, \
        {"node_color":colorpalett["tab:olive"], "node_shape":"H"}, \
        {"node_color":colorpalett["tab:cyan"], "node_shape":"D"}, \
        )

edge_style={ \
        "up":{"edge_color":colorpalett["tab:cyan"]}, \
        "next":{"edge_color":colorpalett["tab:olive"]}, \
        }

def draw_every_edgetype_different( mygrid, pos, ax = None ):
    edgetypes = netx.get_edge_attributes( mygrid, "edgetype" )
    asd = {}
    for edge in list( mygrid.edges( keys=True ) ):
        mylist = asd.setdefault( edgetypes[ edge ], list() )
        mylist.append( edge )
    keylist = list( asd.keys() )

    for i in range( len( asd )):
        netx.draw_networkx_edges( mygrid, pos, ax=ax, node_size=mysize,\
                                    edgelist = asd[keylist[i]], \
                                    **edge_style[keylist[i]] )
                                        


def draw_marked_nodes( mygrid, pos, marked_nodes, **argv ):
    netx.draw_networkx_nodes( mygrid, pos, **argv, node_size=2*mysize,\
                            nodelist = marked_nodes, \
                            node_shape="x", node_color=colorpalett["tab:cyan"])



def draw_every_stitchtype_different( mygrid, pos, ax=None ):
    asd = {}
    stitchtypes = netx.get_node_attributes( mygrid, "stitchtype" )
    stitchtypes.update({"start":"custom", "end":"custom"})
    for node in list( mygrid.nodes() ):
        mylist = asd.setdefault( stitchtypes[ node ], list() )
        mylist.append( node )
    keylist = list( asd.keys() )
    
    for i in range( len( asd )):
        netx.draw_networkx_nodes( mygrid, pos, ax=ax, node_size=mysize,\
                                nodelist = asd[ keylist[i] ], \
                                **stitch_style[i], label= keylist[i] )



def give_init_positions( mystrickgraph ):
    rows = mystrickgraph.get_rows( presentation_type="machine" )
    init_positions = {}
    y = 0.0
    dy = 1.0/len(rows)
    for i in range( len(rows) ):
        x = 0
        dx = 5.0/len( rows[i] )
        y = y + dy
        for node in rows[i]:
            init_positions.update({node:(x,y)})
            x = x+dx
    init_positions.update({"end":(x,y)})
    init_positions.update({"start":(-1.0,0.0)})
    return init_positions

