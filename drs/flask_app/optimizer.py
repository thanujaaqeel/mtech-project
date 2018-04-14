from predictor import predictor
from metric_status import status_store
import math

class OptimizeError(Exception): pass

class ExecutorOptimizer(object):
  "AssignProcesses"
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

        print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
          status.component, status.arrival_rate, status.population, executors_allocation[status.component], sojourn_time_1
        )
        print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
          status.component, status.arrival_rate, status.population, executors_allocation[status.component]+1, sojourn_time_2
        )
        print "sojourn_time_diff", sojourn_time_diff

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

  def statuses(self):
    statuses = [status_store.status_for(component) for component in self.components]
    return [status for status in statuses if status]

  def optimize(self):
    statuses = self.statuses()

    if not statuses:
      return

    for status in statuses:
      print "got status", status

    executor_optimizer = ExecutorOptimizer(self.total_executors, statuses)
    result = executor_optimizer.calulate_optimum_executors_allocation()
    print "RESULT ", result
