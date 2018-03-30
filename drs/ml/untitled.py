import matplotlib.pyplot as plt
from ml.data import Data
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import linear_model
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn import preprocessing
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import numpy as np

data = Data("metrics_remote_1.csv")

X = data.train_data("mfp")[['arrival_rate']]
Y = data.train_data("mfp")[['sojourn_time']]

x = X.values.squeeze()
y = Y.values.squeeze()

xx = np.linspace(x.min(),x.max(), len(x))
itp = interp1d(x,y, kind='linear')
window_size, poly_order = 501, 2
yy_sg = savgol_filter(itp(xx), window_size, poly_order)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, y, 'r.', label= 'Unsmoothed curve')
ax.plot(xx, yy_sg, 'k', label= "Smoothed curve")
plt.legend(loc='best')
plt.show()






from matplotlib.pyplot import *
from scikits import datasmooth as ds

d = 4
Nhat = 200
xmin = np.min(x)
xmax = np.max(x)
xh = np.linspace(xmin-0.1,xmax+0.1,Nhat)

yh,lmbd = ds.smooth_data(x,y,d,xhat=xh)

yht = np.sin(xh)

print('scaled regularization parameter =', lmbd)

cla()
plot(x,y,'ow',xh,yh,'-b',xh,yht,'-r')
legend(['scattered','smoothed','true'],loc='best',numpoints=1)
show()
