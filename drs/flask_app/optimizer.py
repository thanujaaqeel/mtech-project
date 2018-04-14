from predictor import predictor
from metric_status import status_store
import math

class OptimizeError(Exception): pass

class ExecutorOptimizer(object):
  """implements AssignProcesses algorithm"""

  def __init__(self, total_executors, statuses):
    self.total_executors = total_executors #Kmax
    self.statuses = statuses

  def sojourn_time_for(self, component, arrival_rate, population, executors):
    if component == "mfp":
      return predictor.predict_sojourn_time(arrival_rate=arrival_rate, population=population, executors=executors)
    return 0

  def calulate_initial_executors_allocation(self):
    executors_allocation = {}

    for status in self.statuses:
      executors = int(math.ceil(status.arrival_rate / status.processing_rate)) #k_i
      executors_allocation[status.component] = max(executors, 1)

    return executors_allocation

  def calulate_optimum_executors_allocation(self):
    executors_allocation = self.calulate_initial_executors_allocation()
    # print "initial executors_allocation", executors_allocation

    if sum(executors_allocation.values()) > self.total_executors:
      raise OptimizeError("Number of executors available are not enough")

    while sum(executors_allocation.values()) < self.total_executors:
      optimized_component = None
      max_sojourn_time_diff = 0

      for status in self.statuses:
        sojourn_time_1 = self.sojourn_time_for(status.component, status.arrival_rate, status.population, executors_allocation[status.component])
        sojourn_time_2 = self.sojourn_time_for(status.component, status.arrival_rate, status.population, executors_allocation[status.component] + 1)
        sojourn_time_diff = sojourn_time_1 - sojourn_time_2

        # print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
        #   status.component, status.arrival_rate, status.population, executors_allocation[status.component], sojourn_time_1
        # )
        # print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
        #   status.component, status.arrival_rate, status.population, executors_allocation[status.component]+1, sojourn_time_2
        # )
        # print "sojourn_time_diff", sojourn_time_diff

        if sojourn_time_diff > max_sojourn_time_diff:
          optimized_component = status.component
          max_sojourn_time_diff = sojourn_time_diff

      if optimized_component:
        executors_allocation[optimized_component] += 1
      else: #no improvement found in increasing executors
        break
  
    return executors_allocation


class Optimizer(object):
  def __init__(self, total_executors, components):
    self.total_executors = total_executors
    self.components = components

  @property
  def statuses(self):
    if not hasattr(self, "_statuses"):
      statuses = [status_store.status_for(component) for component in self.components]
      self._statuses = [status for status in statuses if status]
    return self._statuses

  def calculate_current_allocation(self):
    executors_allocation = {}

    for status in self.statuses:
      executors_allocation[status.component] = status.executors

    return executors_allocation

  def calculate_optimized_allocation(self):
    if not self.statuses:
      return {}

    executor_optimizer = ExecutorOptimizer(self.total_executors, self.statuses)
    return executor_optimizer.calulate_optimum_executors_allocation()

  @property
  def current_allocation(self):
    if not hasattr(self, "_current_allocation"):
      self._current_allocation = self.calculate_current_allocation()
    return self._current_allocation

  @property
  def optimized_allocation(self):
    if not hasattr(self, "_optimized_allocation"):
      self._optimized_allocation = self.calculate_optimized_allocation()
    return self._optimized_allocation

  def should_optimize(self):
    return self.optimized_allocation != self.current_allocation
