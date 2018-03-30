import matplotlib.pyplot as plt
from ml.training import Data
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import linear_model
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn import preprocessing

data = Data("metrics_remote_1.csv")

# reg = linear_model.LinearRegression()
reg = linear_model.Ridge (alpha = .5)
# reg = linear_model.RidgeCV(alphas=[0.1, 1.0, 10.0])
# reg = linear_model.Lasso(alpha = 0.1)
# reg = linear_model.LassoLars(alpha=.1)
# reg = linear_model.BayesianRidge()

X = data.train_data("mfp")[['arrival_rate']]
Y = data.train_data("mfp")[['sojourn_time']]

X_scaled = preprocessing.robust_scale(X)

poly = PolynomialFeatures(degree=6)

X_ = poly.fit_transform(X_scaled)

reg.fit(X_, Y)

X_test = data.test_data("mfp")[['arrival_rate']]
X_test_scaled = preprocessing.robust_scale(X_test)
X_test_ = poly.fit_transform(X_test_scaled)

predicted_y = reg.predict(X_test_)

Y_test = data.test_data("mfp")[['sojourn_time']]

print "Mean squared error ", mean_squared_error(Y_test, predicted_y)
print 'Variance score: %.2f' % r2_score(Y_test, predicted_y)

plt.scatter(X_test, Y_test,  color='black')
plt.plot(X_test, predicted_y, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()



predicted_sj = pd.DataFrame(predicted_y, columns=['predicted_sj'])
pd.concat([X_test['arrival_rate'] , Y_test, predicted_sj], axis=1, join='inner').to_csv('prediction.csv')

