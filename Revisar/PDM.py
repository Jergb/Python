import pandas as pd
import scipy as sp
from scipy.spatial.distance import mahalanobis
import matplotlib.pylab as plt

datadict = {
    'country': ['Argentina', 'Bolivia', 'Brazil'],
    'd1': [0.34, -0.19, 0.37],
    'd2': [-0.57, -0.69, -0.28],
    'd3': [-0.02, -0.55, 0.07],
    'd4': [-0.69, -0.18, 0.05],
    'd5': [-0.83, -0.69, -0.39],
    'd6': [-0.45, -0.77, 0.05]}



pairsdict = {
    'country1': ['Argentina', 'Bolivia', 'Brazil'],
    'country2': ['Bolivia', 'Brazil', 'Argentina']}

# DataFrame that contains the data for each country
df = pd.DataFrame(datadict)

# DataFrame that contains the pairs for which we calculate the Mahalanobis distance
pairs = pd.DataFrame(pairsdict)

# Add data to the country pairs
pairs = pairs.merge(df, how='left', left_on=['country1'], right_on=['country'])


pairs = pairs.merge(df, how='left', left_on=['country2'], right_on=['country'])

# Convert data columns to list in a single cell
pairs['vector1'] = pairs[['d1_x', 'd2_x', 'd3_x', 'd4_x', 'd5_x', 'd6_x']].values.tolist()
pairs['vector2'] = pairs[['d1_y', 'd2_y', 'd3_y', 'd4_y', 'd5_y', 'd6_y']].values.tolist()


mahala = pairs[['country1', 'country2', 'vector1', 'vector2']]
dfT=df
dfT=dfT.transpose()
dfT=dfT.drop(['country'])
# Calculate covariance matrix

covmx = df.cov()
invcovmx = sp.linalg.inv(covmx)

covmxT = dfT.cov()
invcovmxT = sp.linalg.inv(covmxT)

# Calculate Mahalanobis distance
mahala['mahala_dist'] = mahala.apply(lambda x: (mahalanobis(x['vector1'], x['vector2'], invcovmx)), axis=1)
mahala['mahala_T'] = mahala.apply(lambda x: (mahalanobis(x['vector1'], x['vector2'], invcovmxT)), axis=1)
mahalo = mahala[['country1', 'country2', 'mahala_dist']]
print(mahalo)

for pos in range(len(pairs['vector2'])):
    if mahalo['mahala_dist'][pos]<3:
        plt.scatter(pairs['vector1'][pos],pairs['vector2'][pos],color='b')
    else:
        plt.scatter(pairs['vector1'][pos],pairs['vector2'][pos],color='r')
