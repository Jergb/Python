from pylab import *
import numpy as np
import scipy as sp

Time = np.loadtxt('E:\Jergb\Documents\MATLAB\WSN\iob.txt')
t1 = Time[np.nonzero(Time <= 5101436)]
t2 = Time[np.nonzero(Time <= 5260701)][np.nonzero(Time[np.nonzero(Time <= 5260701)] > 5101436)]
t3 = Time[np.nonzero(Time <= 6091215)][np.nonzero(Time[np.nonzero(Time <= 6091215)] > 5260701)]

