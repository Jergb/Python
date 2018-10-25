import numpy as np
from ggplot import *
import matplotlib.pyplot as plt
import pandas as pd

np.random.seed(59)
# as column vectors
x = np.random.poisson(5,10)
y = np.random.poisson(5,10)


plt.close('all')

# examine the shape of the numpy arrays

covariance_xy = np.cov(x,y, rowvar=0)
inv_covariance_xy = np.linalg.inv(covariance_xy)

# Examine inverse covariance matrix and shape

xy_mean = np.mean(x),np.mean(y)

x_diff = np.array([(x_i - xy_mean[0])/x.std() for x_i in x])
y_diff = np.array([(y_i - xy_mean[1])/y.std() for y_i in y])
#x_diff = np.array([(x_i - xy_mean[0]) for x_i in x])
#y_diff = np.array([(y_i - xy_mean[1]) for y_i in y])

diff_xy = np.transpose([x_diff, y_diff])
diff_xy.shape, diff_xy

md = []
for i in range(len(diff_xy)):
    md.append(np.sqrt(np.dot(np.dot(np.transpose(diff_xy[i]),inv_covariance_xy),diff_xy[i])))
md


def MahalanobisDist(x, y):
    covariance_xy = np.cov(x, y, rowvar=0)
    inv_covariance_xy = np.linalg.inv(covariance_xy)
    xy_mean = np.mean(x), np.mean(y) # Obtiene las medias de x y de y
    x_diff = np.array([x_i - xy_mean[0] for x_i in x]) #Crea un vector con la diferencia de cada valor de x             respecto a la media de x
    y_diff = np.array([y_i - xy_mean[1] for y_i in y]) #Crea un vector con la diferencia de cada valor de y        respecto a la media de y
    diff_xy = np.transpose([x_diff, y_diff])

    md = []
    for i in range(len(diff_xy)):
        md.append(np.sqrt(np.dot(np.dot(np.transpose(diff_xy[i]), inv_covariance_xy), diff_xy[i])))
    return md

MahalanobisDist(x,y)

def pintar(x,y):
    MD = MahalanobisDist(x, y)
    threshold = np.mean(MD) * 1.5 # adjust 1.5 accordingly
    outliersx, outliersy, p = [], [], []
    for i in range(len(MD)):
        if MD[i] > threshold:
            outliersx.append(x[i])
            outliersy.append(y[i])
            p.append(i)
    return (np.array(outliersx), np.array(outliersy), np.array(p))
pinte=pintar(x,y)
p1,p2,p=pinte[0],pinte[1],pinte[2]
#print('p1: ',p1,'p2: ', p2)
p1=list(p1)
p2=list(p2)

def MD_removeOutliers(x, y):
    MD = MahalanobisDist(x, y)
    threshold = np.mean(MD) * 1.5 # adjust 1.5 accordingly
    nx, ny = [], []
    for i in range(len(MD)):
        if MD[i] <= threshold:
            nx.append(x[i])
            ny.append(y[i])
    return (np.array(nx), np.array(ny),threshold)

valos={'x':list(x),'y':list(y)}
valo=pd.DataFrame(valos)
#print('x:', x)
#print('y:', y)
ddd=MD_removeOutliers(x, y)

d1=ddd[0]
d2=ddd[1]
t=ddd[2]

lx=list(x_diff[p])
ly=list(y_diff[p])
Lxy=pd.DataFrame({'X':lx,'Y':ly})
#plt.figure()
#plt.subplot(1, 2, 1)
#plt.plot(x, 'ro')
#plt.plot(p,p1,'ko')
#plt.plot(y, 'bo')
#plt.plot(p,p2,'ko')
#plt.subplot(1, 2, 2)
#plt.plot(d1, 'ro')
#plt.plot(d2, 'bo')

import pandas as pd

DF_diff_xy = pd.DataFrame(diff_xy)
DF_diff_xy.rename(columns = lambda x: str(x), inplace=True)
DF_diff_xy.rename(columns={"0": "X"}, inplace=True) # rename a dfcolumn   
DF_diff_xy.rename(columns={"1": "Y"}, inplace=True) # rename a dfcolumn 
DF_diff_xy
plt.figure()
#%load_ext rmagic
#%reload_ext rmagic
plo=ggplot(DF_diff_xy, aes(x = 'X', y ='Y')) + \
    geom_point(alpha=1, size=100, color='dodgerblue') + \
    geom_point(data = Lxy,alpha=1, size = 100, color='red')
plo.show()
