import re
from metric_logger import MetricLogger
from statsd import StatsClient
from storm_rest_api import ApiClient
from metric_status import status_store, Status
from helper import handleMissingMetric

_arrival_count_ = 0

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
  DATA_POINTS = ['component_id', 'arrival_count', 'arrival_rate', 'executors', 'population', 'sojourn_time']

  def __init__(self, metric_dict):
    self.metric_dict = metric_dict
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
  @handleMissingMetric
  def arrival_rate(self):
    return self.metrics['__receive']['arrival_rate_secs']

  @property
  @handleMissingMetric
  def sojourn_time(self):
    return self.metrics['__receive']['sojourn_time_ms']

  @property
  @handleMissingMetric
  def population(self):
    return self.metrics['__receive']['population']

  @property
  @handleMissingMetric
  def execute_latency(self):
    latency_dict = self.metrics['__execute-latency']
    return latency_dict.values()[0]

  @property
  def processing_rate(self):
    if self.execute_latency <= 0:
      return -1
    return 1000.0/self.execute_latency

  @property
  @handleMissingMetric
  def process_latency(self):
    return self.metrics['__process-latency']

  @property
  @handleMissingMetric
  def dropped_messages(self):
    return self.metrics['__receive']['dropped_messages']

  @property
  @handleMissingMetric
  def overflow(self):
    return self.metrics['__receive']['overflow']

  @property
  @handleMissingMetric
  def backpressure(self):
    return self.metrics['__skipped-backpressure-ms']

  @property
  @handleMissingMetric
  def executors(self):
    if not hasattr(self, "_executors"):
      topology_id = self.api.get_summary().topology_id
      self._executors = self.api.get_component(self.component_id, topology_id).executors
    return self._executors

  @property
  @handleMissingMetric
  def current_arrival_count(self):
    return int(self.metrics['arrival_count'])

  @property
  def arrival_count(self):
    return _arrival_count_

  def process(self):
    self.update_global_arrival_count()

    if not self.should_process():
      return

    self.collect_executor_data()

    self.log_to_file()
    self.track_metric_status()
    # self.log_to_statsd()
    
    print "\n\n", self

  def track_metric_status(self):
    status = Status(component = self.component_id,
                    arrival_rate = self.arrival_count,
                    population = self.population,
                    executors = self.executors,
                    processing_rate = self.processing_rate)
    status_store.push(status)

  def update_global_arrival_count(self):
    if self.current_arrival_count >=0:
      global _arrival_count_
      _arrival_count_ = self.current_arrival_count

  def should_process(self):
    if self.is_spout:
      return self.should_process_spout()
    elif self.is_bolt:
      return self.should_process_bolt()
    return False
  
  def should_process_spout(self):
    return int(self.arrival_count) > 0

  def should_process_bolt(self):
    return int(self.processing_rate) > 0 

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
    return "%s. arrival_count: %s, arrival_rate: %s, sojourn_time: %s, population: %s, dropped_messages: %s, execute_latency: %s, processing_rate: %s, executors: %s" % (
            self.component_id, \
            self.arrival_count, \
            self.arrival_rate, \
            self.sojourn_time, \
            self.population, \
            self.dropped_messages, \
            self.execute_latency, \
            self.processing_rate, \
            self.executors)

