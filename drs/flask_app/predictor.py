from sklearn.externals import joblib

class Predictor(object):
  def __init__(self, model_file_name):
    self.model_file_name = model_file_name
    self._model = None

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

predictor = Predictor("ridge_model.pkl")
