from optimizer import Optimizer
from metric_status import status_store
from resource_scheduler import StormResourceScheduler
from helper import handleAndLogException
import time

TOPOLOGY_NAME = "mfp"
TOTAL_EXECUTORS = 10
COMPONENTS = ["transaction", "mfp", "reporter"]

@handleAndLogException
def optimizer_job():
  print "running optimizer_job"

  optimizer = Optimizer(total_executors=TOTAL_EXECUTORS, components=COMPONENTS)

  print "current allocation", optimizer.current_allocation
  print "optimized allocation", optimizer.optimized_allocation


  if optimizer.should_optimize():
    optimized_allocation = optimizer.optimized_allocation

    scheduler = StormResourceScheduler(TOPOLOGY_NAME, optimized_allocation)
    result = scheduler.schedule_allocation()
    
    if result == 0:
      status_store.clear() #TODO: do this only if rebalanced
    
    print "schedule_allocation result", result
    
    time.sleep(20)
  else:
    print "already running under optimum allocation!"
