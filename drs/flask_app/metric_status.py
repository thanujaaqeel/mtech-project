import numpy
from collections import deque
from collections import defaultdict

class Status(object):
  def __init__(self, component, arrival_rate, population, executors, processing_rate):
    self.component = component
    self.arrival_rate = arrival_rate
    self.population = population
    self.executors = executors
    self.processing_rate = processing_rate

class StatusStore(object):
  def __init__(self, max_q_length=100):
    self.store = defaultdict(lambda : deque(maxlen=max_q_length))

  def push(self, status):
    self.store[status.component].append(status)

  def mean_for(self, component, attribute):
    q = self.store[component]
    return numpy.mean([getattr(x, attribute)  for x in q])

  def arrival_rate_for(self, component):
    self.mean_for(component, "arrival_rate")

  def population_for(self, component):
    self.mean_for(component, "population")

  def processing_rate_for(self, component):
    self.mean_for(component, "processing_rate")

  def executors_for(self, component):
    self.mean_for(component, "executors")

status_store = StatusStore()
