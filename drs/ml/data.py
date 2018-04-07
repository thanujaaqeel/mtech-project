import os
import pandas as pd
from sklearn.model_selection import train_test_split

class Data():
  def __init__(self, filename, train_size=0.8):
    self.file_path = self.file_path_from(filename)
    self.train_size = train_size
    self.load_data()

  def file_path_from(self, filename):
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, filename))

  def load_data(self):
    self._dataframe = pd.read_csv(self.file_path)
    self._train_data, self._test_data = train_test_split(self._dataframe,
                                                      train_size=self.train_size,
                                                      test_size=1-self.train_size)
  def test_data(self, component_id=None):
    _test_data = self._test_data

    if component_id:
      _test_data = _test_data[(_test_data.component_id == component_id)]
    return _test_data

  def train_data(self, component_id=None):
    _train_data = self._train_data

    if component_id:
      _train_data = _train_data[(_train_data.component_id == component_id)]

    return _train_data
#data.test_data[(data.test_data.component_id == "transaction")]
