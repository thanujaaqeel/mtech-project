from predictor import predictor

class AssignProcessors(object):
  def __init__(self, total_executors, statuses):
    self.total_executors = total_executors #Kmax
    self.statuses = statuses

  def sojourn_time_for(arrival_rate, population, executors):
    return predictor.predict(arrival_rate, population, executors)

  def process(self):
    _executors = []
    for status in self.statuses:
      status = self.statuses[i]
      executors_i = status.arrival_rate[i] / status.processing_rate #ki
      _executors.append(executors_i)

    if sum(_executors) > self.total_executors:
      raise Exception("Number of executors available are not enough")

    while sum(_executors) < self.total_executors:
      j = 0
      max_sojourn_time_diff = 0

      for index, status in enumerate(self.statuses):
        sojourn_time_diff = self.sojourn_time_for(status.arrival_rate, status.population, _executors[index] + 1) - \
                              self.sojourn_time_for(status.arrival_rate, status.population, _executors[index])
        if sojourn_time_diff > max_sojourn_time_diff:
          j = index
          max_sojourn_time_diff = sojourn_time_diff

      _executors[j] += 1
