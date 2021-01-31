def myvis3d( graph ):
    x = netx.get_node_attributes( graph, "x" )
    y = netx.get_node_attributes( graph, "y" )
    z = netx.get_node_attributes( graph, "z" )
    myarray = []
    for node in x:
        myarray.append( [ x[node], y[node], z[node] ])
    myarray = np.array( myarray )
    myarray = myarray.T

    edgelist = []
    length = netx.get_edge_attributes( graph, "tension" )
    minima, maxima = length[ list(length)[0] ], length[ list(length)[0] ]
    for tmpedge in length:
        tmpxs = ( x[tmpedge[0]], x[tmpedge[1]] )
        tmpys = ( y[tmpedge[0]], y[tmpedge[1]] )
        tmpzs = ( z[tmpedge[0]], z[tmpedge[1]] )
        edgelist.append((tmpxs, tmpys, tmpzs, length[ tmpedge ]))
        minima = min( minima, length[ tmpedge ])
        maxima = max( maxima, length[ tmpedge ])



    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.cm as cm
    import matplotlib.colors as colors
    norm = colors.Normalize( vmin=minima, vmax =maxima, clip=True)
    mapper = cm.ScalarMappable( norm=norm, cmap=cm.coolwarm_r )
    fig = plt.figure()
    ax = fig.add_subplot( 111, projection='3d')
    #ax.scatter( myarray[0], myarray[1], myarray[2] )

    for tmpedge in edgelist:
        ax.plot( tmpedge[0], tmpedge[1], tmpedge[2], \
                        color=mapper.to_rgba(tmpedge[3]) )
    plt.show()

