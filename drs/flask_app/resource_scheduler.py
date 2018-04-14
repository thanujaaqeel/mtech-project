from subprocess import call

class StormResourceScheduler(object):
  """rebalances storm with given configuration"""

  STORM_BINARY = "storm"
  REBALANCE_COMMAND = "rebalance"

  def __init__(self, topology_name, resource_allocation):
    self.resource_allocation = resource_allocation or {}
    self.topology_name = topology_name

  def has_valid_allocation(self):
    return bool(self.resource_allocation)

  def build_storm_allocation(self):
    allocation_options = []

    for component, executors in self.resource_allocation.items():
      component_option = "-e %s=%d" % (component, executors)
      allocation_options.append(component_option)
    return " ".join(allocation_options)

  def build_storm_rebalance_command(self):
    return "%s %s %s %s" % (self.STORM_BINARY, self.REBALANCE_COMMAND, self.topology_name, self.build_storm_allocation())

  def schedule_allocation(self):
    if self.has_valid_allocation():
      rebalance_command = self.build_storm_rebalance_command().split(" ")
      print "rebalance command", rebalance_command
      return call(rebalance_command)
    else:
      print "No valid allocation available"
      return 0