import os
from sklearn.externals import joblib
import numpy as np
from sklearn.preprocessing import PolynomialFeatures


class Predictor(object):
  def __init__(self, model_file_name):
    self.model_file_name = model_file_name
    self._model = None
    self.poly = PolynomialFeatures(degree=1)

  @property
  def model(self):
    if not self._model:
      self._model = self.load_model()
    return self._model

  def load_model(self):
    return joblib.load(self.build_model_file_path())

  def optimized_executors(self, arrival_rate, population, executors):
    return 1

  def build_model_file_path(self):
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, os.pardir, "ml", "models", self.model_file_name))

  def predict_input(self, executors, arrival_rate, population):
    input_array = np.asarray([executors, arrival_rate, population]).reshape(1, -1)
    return self.poly.fit_transform(input_array)

  def predict_sojourn_time(self, executors, arrival_rate, population):
    predicted_result = self.model.predict(self.predict_input(executors, arrival_rate, population))[0]
    return max(int(predicted_result), 0)


predictor = Predictor("ridge_model.pkl")
