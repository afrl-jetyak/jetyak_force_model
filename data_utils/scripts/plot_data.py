"""
    This script contains several functions that performs plottig of data
    both for testing and also for the final result generation

    File name: plot_data.py
    Author: Nare Karapetyan
    License:
    Date Create: June 14 2019
    Date Last Modified: June 14 2019

"""

#!/bin/python

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


import pandas as pd
import sys



print(sys.version_info)

def plot_3D(x, y, z, labels, plot_type = "scatter"):
    """
    Test function for the general project_name module

    Parametes
    ---------
        x, y, z: are numpy arrays for each of the coordinates
        labels: list of labels for plots

    Examples:
    --------
	FIXME make the lists numpy arrays
    >>> ploy_3D([1, 2], [3, 4], [5, 6], ['x', 'y', 'z']) 

    """

    fig = plt.figure()
    plt.autoscale(False)
    ax = fig.add_subplot(111, projection='3d')

    if plot_type == "scatter":
	ax.scatter(x, y, z)
    if plot_type == "plot":
	ax.plot(x, y, z)
    
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])
    
    plt.show()



#-----
def read_data(fileName):
    df = pd.read_csv(fileName, sep=',')
   # data = df.values#.T
    #print(data)
    #return data
    return df

def plot_vectors(xs, ys, zs, r, p, y):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.quiver(xs, ys, zs, r, p, y)

#filename = raw_input("Please enter the filename:")
if len(sys.argv) > 1 : 
    filename = str(sys.argv[1])
else:
    print("the default file is used:" + str(filename))
data = read_data(filename)
labels = ['Latitude', 'Longitude', 'depth']
xs = data[labels[0]]
xs = map(float,xs.values)
ys = data[labels[1]]
ys = map(float,ys.values)
zs = data[labels[2]]
zs = map(float,zs.values)


plot_3D(xs, ys, zs, labels)
#plot_3D([1.3,2], [1.6,2], [1,2], labels)

