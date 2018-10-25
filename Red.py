# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 17:41:18 2018

@author: Jergb
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

asa=pd.DataFrame({'a':[1,2,3,1,3,3,1,1],'b':[3,6,2,1,1,1,4,2],'c':['1','1','2','2','2','1','1','2']})

g = sns.PairGrid(asa, hue="c")
g = g.map_diag(plt.hist)
g = g.map_offdiag(plt.scatter)
#g = g.add_legend()
plt.show()