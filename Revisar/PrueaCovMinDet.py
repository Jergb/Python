# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:17:02 2018

@author: Jergb
"""


import numpy as np
import matplotlib.pyplot as plt

from sklearn.covariance import MinCovDet
n_samples = 4
n_outliers = 1
n_features = 2

# generate data
gen_cov = np.eye(n_features)
#gen_cov[0, 0] = 2.
X = np.dot(np.random.randn(n_samples, n_features), gen_cov)
print('cov:', X)

inlier_plot =plt.scatter(X[:, 0], X[:, 1],
                              color='black', label='inliers')
outlier_plot =plt.scatter(X[:, 0][-n_outliers:], X[:, 1][-n_outliers:],
                               color='red', label='outliers')
plt.xlim(plt.xlim()[0], 11.)
plt.legend()
plt.title("Mahalanobis distances of a contaminated data set:")

xx, yy = np.meshgrid(np.linspace(plt.xlim()[0], plt.xlim()[1], 2),
                     np.linspace(plt.ylim()[0], plt.ylim()[1], 2))
zz = np.c_[xx.ravel(), yy.ravel()]

robust_cov = MinCovDet().fit(X)
mahal_robust_cov = robust_cov.mahalanobis(zz)
mahal_robust_cov = mahal_robust_cov.reshape(xx.shape)
print('covR: ', mahal_robust_cov)
robust_contour = plt.contour(xx, yy, np.sqrt(mahal_robust_cov),
cmap=plt.cm.YlOrBr_r, linestyles='dotted')