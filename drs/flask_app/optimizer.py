from predictor import predictor
from metric_status import status_store
import math

class ExecutorAssigner(object):
  "AssignProcesses"
  def __init__(self, total_executors, statuses):
    self.total_executors = total_executors #Kmax
    self.statuses = statuses

  def sojourn_time_for(self, component, arrival_rate, population, executors):
    if component == "mfp":
      return predictor.predict_sojourn_time(arrival_rate=arrival_rate, population=population, executors=executors)
    return 0

  def process(self):
    _executors = []
    for status in self.statuses:
      executors_i = int(math.ceil(status.arrival_rate / status.processing_rate)) #k_i
      _executors.append(max(executors_i, 1))

    # print "initial _executors", _executors

    if sum(_executors) > self.total_executors:
      raise Exception("Number of executors available are not enough")

    while sum(_executors) < self.total_executors:
      j = -1
      max_sojourn_time_diff = 0

      for index, status in enumerate(self.statuses):
        sojourn_time_1 = self.sojourn_time_for(status.component, status.arrival_rate, status.population, _executors[index])
        sojourn_time_2 = self.sojourn_time_for(status.component, status.arrival_rate, status.population, _executors[index] + 1)
        sojourn_time_diff = sojourn_time_1 - sojourn_time_2

        # print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
        #   status.component, status.arrival_rate, status.population, _executors[index], sojourn_time_1
        # )
        # print "component: %s, arrival_rate: %s, population: %s, executors: %s, sojourn_time: %s" % (
        #   status.component, status.arrival_rate, status.population, _executors[index]+1, sojourn_time_2
        # )
        # print "sojourn_time_diff", sojourn_time_diff

        if sojourn_time_diff > max_sojourn_time_diff:
          j = index
          max_sojourn_time_diff = sojourn_time_diff

      if j >= 0:
        _executors[j] += 1
      else: #no improvement found in increasing executors
        break
  
    return _executors


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

    executor_assigner = ExecutorAssigner(self.total_executors, statuses)
    result = executor_assigner.process()
    print "RESULT ", result
