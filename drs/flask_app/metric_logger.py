import os

class MetricLogger():
  def __init__(self, filename, data_points):
    self.file_path = self.build_file_path(filename)
    self.data_points = data_points
    self.setup_headers()

  def build_file_path(self, filename):
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, os.pardir, filename))

  def setup_headers(self):
      header = self.get_header()
      if not header:
        self.write_headers()
      elif not self.is_valid_header(header):
        raise Exception("Invalid header already found")

  def is_valid_header(self, header):
    return self.build_header(self.data_points).strip() == header.strip()

  def get_header(self):
    header = ''
    try:
      with open(self.file_path, 'r+') as file:
        header = file.readline()
    except IOError:
      pass
    return header

  def write_headers(self):
    with open(self.file_path, 'w+') as file:
      file.write(self.build_header(self.data_points))
      file.write("\n")

  def build_header(self, data_points):
    return self.to_csv(data_points)

  def to_csv(self, values):
    return ",".join([str(v) for v in values])

  def log(self, metric):
    with open(self.file_path, 'a') as file:
      csv = self.to_csv(metric)
      file.write(csv)
      file.write("\n")
