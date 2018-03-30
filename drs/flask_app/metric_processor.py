import re
from metric_logger import MetricLogger
from statsd import StatsClient
from storm_rest_api import ApiClient

class Metrics():
  def __init__(self, dictionary):
    self.dictionary = {}
    for metric in dictionary:
      attr_key = metric['name']
      attr_value = metric['value']
      self.dictionary[attr_key] = attr_value

  def __str__(self):
    return self.dictionary.__str__()

  def __getitem__(self, key):
    return self.dictionary[key]

  def __str__(self):
    return self.dictionary.__str__()

class Meta():
  def __init__(self, dictionary):
    self.dictionary = dictionary

  def __getitem__(self, key):
    return self.dictionary[key]

class MetricProcessor():
  BOLTS = ['mfp', 'reporter']
  SPOUTS = ['transaction']
  COMPONENTS = set(BOLTS + SPOUTS)
  DATA_POINTS = ['component_id', 'arrival_rate', 'executors', 'sojourn_time']

  def __init__(self, metric_dict):
    self.meta = Meta(metric_dict['meta'])
    self.metrics = Metrics(metric_dict['metrics'])
    self.logger = MetricLogger("metrics_4.csv", self.DATA_POINTS)
    self.statsd = StatsClient()
    self.api = ApiClient()

  @property
  def component_id(self):
    return self.meta['srcComponentId']

  @property
  def is_spout(self):
    return self.component_id in self.SPOUTS

  @property
  def is_bolt(self):
    return self.component_id in self.BOLTS

  @property
  def arrival_rate(self):
    return self.metrics['__receive']['arrival_rate_secs']

  @property
  def sojourn_time(self):
    return self.metrics['__receive']['sojourn_time_ms']

  @property
  def population(self):
    return self.metrics['__receive']['population']

  @property
  def execute_latency(self):
    return self.metrics['__execute-latency']

  @property
  def process_latency(self):
    return self.metrics['__process-latency']

  @property
  def dropped_messages(self):
    return self.metrics['__receive']['dropped_messages']

  @property
  def overflow(self):
    return self.metrics['__receive']['overflow']

  @property
  def executors(self):
    if self.is_spout:
      return self.executor_data.get_spout(self.component_id)['executors']
    else:
      return self.executor_data.get_bolt(self.component_id)['executors']

  def process(self):
    if not self.should_process():
      return

    self.collect_executor_data()

    self.log_to_file()
    # self.log_to_statsd()

    if self.is_bolt:
      print self

  def should_process(self):
    return self.component_id in self.COMPONENTS and int(self.arrival_rate) > 0

  def log_to_statsd(self):
    for point in self.DATA_POINTS[1:]:
      self.statsd.gauge('%s.arrival_rate' % self.component_id, getattr(self, point))

  def log_to_file(self):
    log_data = [getattr(self, point) for point in self.DATA_POINTS]
    self.logger.log(log_data)

  def collect_executor_data(self):
    topology_id = self.api.get_summary().topology_id
    self.executor_data = self.api.get_topology(topology_id)

  def __str__(self):
    return "%s. arrival_rate: %d, sojourn_time: %d, population: %d, execute_latency: %s, executors: %s" % (
            self.component_id, \
            self.arrival_rate, \
            self.sojourn_time, \
            self.population, \
            self.execute_latency, \
            self.executors)
