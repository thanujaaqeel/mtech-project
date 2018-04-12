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

  def __str__(self):
    return "%s. component: %s, arrival_rate: %s, population: %s, processing_rate: %s, executors: %s" % (
            self.component, \
            self.arrival_rate, \
            self.population, \
            self.processing_rate, \
            self.executors)

class StatusStore(object):
  def __init__(self, max_q_length=100):
    self.store = defaultdict(lambda : deque(maxlen=max_q_length))

  def push(self, status):
    self.store[status.component].append(status)

  def mean_for(self, component, attribute):
    q = self.store[component]
    return numpy.mean([getattr(x, attribute)  for x in q])

  def arrival_rate_for(self, component):
    return self.mean_for(component, "arrival_rate")

  def population_for(self, component):
    return self.mean_for(component, "population")

  def processing_rate_for(self, component):
    return self.mean_for(component, "processing_rate")

  def executors_for(self, component):
    return self.mean_for(component, "executors")

  def status_for(self, component):
    return {
      "arrival_rate": self.arrival_rate_for(component),
      "population": self.population_for(component),
      "processing_rate": self.processing_rate_for(component),
      "executors": self.executors_for(component)
    }

  def components(self):
    return self.store.keys()

  def print_status(self):
    for c in self.components():
      print "status for", c, self.status_for(c)

status_store = StatusStore()
