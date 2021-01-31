from scipy.spatial.distance import cdist
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata as myinterp
from mpl_toolkits.mplot3d import Axes3D

def return_activation_map(self, data_vector):
    """Plot the activation map of a given data instance or a new data
    vector

    :param data_vector: Optional parameter for a new vector
    :type data_vector: numpy.array
    :param data_index: Optional parameter for the index of the data instance
    :type data_index: int.
    :param activation_map: Optional parameter to pass the an activation map
    :type activation_map: numpy.array
    """
    try:
        d1, _ = data_vector.shape
        w = data_vector.copy()
    except ValueError:
        d1, _ = data_vector.shape
        w = data_vector.reshape(1, d1)
    if w.shape[1] == 1:
        w = w.T
    matrix = cdist(self.codebook.reshape((self.codebook.shape[0] *
                                          self.codebook.shape[1],
                                          self.codebook.shape[2])),
                   w, 'euclidean').T
    matrix.shape = (self.codebook.shape[0], self.codebook.shape[1])
    return matrix

def find_best_position( self, point ):
    activation_matrix = return_activation_map( self, data_vector=point )
    argmin = activation_matrix.argmin()
    argmin = (int(argmin/activation_matrix.shape[1]), \
            argmin%activation_matrix.shape[1])
    return argmin

def draw_line_bestmatch( self, line ):
    line_xy = []
    argmin = None
    for point in line:
        position = find_best_position( self, np.matrix(point) )
        line_xy.append( position )
    matrix = np.matrix(line_xy).T
    plt.figure()
    x=np.array(matrix[0])[0]
    y=np.array(matrix[1])[0]
    plt.plot( x,y, 'bo-' )
    plt.xlim( 0,self._n_columns )
    plt.ylim( 0,self._n_rows )
    return plt



def _create_boundarycondition( up, down, left, \
                        right, updist, downdist, leftdist, rightdist,\
                        n_rows, n_columns ):
    """ This function return a method to reset a matrix for example the 
    som.codebook to a given boundary
    :param up,down,left,right: boundarypoints on a line
    :param *dist: distancelist of the points, distances adding up
    :return boundarycondition: method to exectue on a matrix, eg bound( matrix )
    """
    xi = np.linspace( updist[0], updist[-1], num=n_columns )
    uprow = np.float32( myinterp( updist, up, xi ) )
    xi = np.linspace( downdist[0], downdist[-1], num=n_columns )
    downrow = np.float32( myinterp( downdist, down, xi ) )
    xi = np.linspace( leftdist[0], leftdist[-1], num=n_rows )
    leftrow = np.float32( myinterp( leftdist, left, xi ) )
    xi = np.linspace( rightdist[0], rightdist[-1], num=n_rows )
    rightrow = np.float32( myinterp( rightdist, right, xi ) )

    def apply_boundarycondition( matrix ):
        for i in range(n_columns):
            matrix[0][i] = downrow[i]
            matrix[-1][i] = uprow[i]
        for i in range(n_rows):
            matrix[i][0] = leftrow[i]
            matrix[i][-1] = rightrow[i]

    return apply_boundarycondition
        

def boundary_train_som( som, data, \
            up, down, left, right, updist, downdist, leftdist, rightdist,\
            epochs = 5, tmax = 5, extrarand = 3,\
            radius0=None, radiusN=1, maxscale=0.08):
    """
    this trains a som but with a set boundary on the edges of the matrix
    :param up,down,left,right: boundarypoints on a line
    :param *dist: distancelist of the points, distances adding up
    """
    n_rows, n_columns = som._n_rows, som._n_columns
    boundarycondition = _create_boundarycondition( up, down, left, right, \
                                    updist, downdist, leftdist, rightdist, \
                                    n_rows, n_columns )
    if radius0==None:
        radius0 = min(n_rows, n_columns)/2
    radii = np.linspace( radius0, radiusN, tmax+1 )
    for i in range( extrarand ):
        data = np.concatenate( (data, np.array(up), np.array(down), np.array(left), np.array(right)) )
    data = np.float32(data)

    som.train( data, epochs=epochs, scale0=0.0, scaleN=0.0 )
    for t in range(tmax):
        boundarycondition( som.codebook )
        som.train( data, epochs=epochs, scale0 =maxscale*t/tmax, \
                scaleN =maxscale*(t+1)/tmax,\
                radius0=radii[t], radiusN=radii[t])
    boundarycondition( som.codebook )

def abbildung_auf_somoclu( som, vector ):
    position = find_best_position( som, point )
    vectorarray, gewichtarray = [], []
    shape = np.array( [som._n_columns, som._n_rows] )
    gesamtgewicht = 0
    abbildung = np.zeros( vector.shape )
    for dv in [np.array([1,0]), np.array([0,1]), np.array([0,0]), \
                    np.array([-1,0]), np.array([0,-1])]:
        tmppos = tuple( (position + dv)%shape )
        vectorarray.append( som.codebook[tmppos] )
        tmpgewicht = np.linalg.norm( vector- som.codebook[tmppos] )**-3
        gewichtarray.append(tmpgewicht)
        gesamtgewicht = gesamtgewicht + tmpgewicht
        abbildung = abbildung + som.codebook[tmppos] * tmpgewicht

    abbildung = abbildung/gesamtgewicht

