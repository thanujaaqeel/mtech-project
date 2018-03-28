import pandas as pd
import numpy as np
from ml.data import Data
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

def smoothen(x, y, window_size=501, poly_order=2):
  xx = np.linspace(x.min(),x.max(), len(x))
  itp = interp1d(x,y, kind='linear')
  return (xx, savgol_filter(itp(xx), window_size, poly_order))

data = Data("metrics_remote_1.csv", train_size=0.5)
poly = PolynomialFeatures(degree=6)

X_train = data.train_data("mfp")[['arrival_rate']]
Y_train = data.train_data("mfp")[['sojourn_time']]

X_test = data.test_data("mfp")[['arrival_rate']]
Y_test = data.test_data("mfp")[['sojourn_time']]

x_train = X_train.squeeze()
y_train = Y_train.squeeze()
xx_train, y_train = smoothen(x_train, y_train)
x_train_poly_transform = poly.fit_transform(xx_train.reshape(-1, 1))

x_test = X_test.squeeze()
y_test = Y_test.squeeze()
xx_test, y_test = smoothen(x_test, y_test)
x_test_poly_transform = poly.fit_transform(x_test.values.reshape(-1, 1))


z = np.poly1d(np.polyfit(xx_test,y_test,25))
# predicted_y = np.asarray([z(x) for x in x_test])
x_test = np.linspace(1500, 3000, 1500)
predicted_y = np.asarray([z(x) for x in x_test])

# reg = linear_model.Ridge (alpha = .5)
# reg.fit(x_train_poly_transform, y_train)
# predicted_y = reg.predict(x_test_poly_transform)

print "Mean squared error ", mean_squared_error(y_test, predicted_y)
print 'Variance score: %.2f' % r2_score(y_test, predicted_y)



_Y_predicted = pd.DataFrame(predicted_y, columns=['predicted_sj'])
_X_test = pd.DataFrame(x_test, columns=['arrival_rate'])
_Y_test = pd.DataFrame(y_test, columns=['sojourn_time'])
op = pd.concat([_X_test , _Y_test, _Y_predicted], axis=1, join='inner')
sorted_op = op.sort_values(['arrival_rate'])
# op.to_csv('prediction.csv')

z = np.poly1d(np.polyfit(xx_test,y_test,8))
x_test = np.linspace(-500, 4020, 1500)
predicted_y = np.asarray([z(x) for x in x_test])


fig, ax = plt.subplots(figsize=(7, 4))
# ax.plot(xx_test, y_test, 'g.', label= 'Test curve')
ax.plot(xx_train, y_train, 'r.', label= 'Training curve')
ax.plot(x_test, predicted_y, 'b.', label= "Prediction curve")
plt.legend(loc='best')
plt.show()


