import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from sklearn.externals import joblib

from data import Data

def train():
  data = Data("metrics/v2/metrics_grouped.csv", train_size=0.7)
  poly = PolynomialFeatures(degree=1)

  X_train = data.train_data("mfp")[['executors', 'arrival_count', 'population']]
  Y_train = data.train_data("mfp")[['sojourn_time']]

  X_test = data.test_data("mfp")[['executors', 'arrival_count', 'population']]
  Y_test = data.test_data("mfp")[['sojourn_time']]

  x_train = X_train.squeeze()
  y_train = Y_train.squeeze()
  x_train = poly.fit_transform(x_train)

  x_test = X_test.squeeze()
  y_test = Y_test.squeeze()
  x_test = poly.fit_transform(x_test)


  reg = linear_model.Ridge (alpha = .5)
  reg.fit(x_train, y_train)

  predicted_y = reg.predict(x_test)

  print "Mean squared error ", mean_squared_error(y_test, predicted_y)
  print 'Variance score: %.2f' % r2_score(y_test, predicted_y)

  return reg

def persist(model, filename):
  joblib.dump(model, 'models/%s.pkl' % filename)

def get_filename():
  if len(sys.argv) < 2:
    raise Exception("Filename not provided")
  return sys.argv[1]

if __name__ == "__main__":
  trained_model = train()
  persist(trained_model, get_filename())


