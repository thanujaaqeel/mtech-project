from optimizer import Optimizer
from metric_status import status_store

TOTAL_EXECUTORS = 10
COMPONENTS = ["transaction", "mfp", "reporter"]

def optimizer_job():
  print "running optimizer_job"

  try:
    optimizer = Optimizer(total_executors=TOTAL_EXECUTORS, components=COMPONENTS)
    optimizer.optimize()
  except Exception as e:
    print "Error in optimize: ", e.message
    import traceback
    traceback.print_exc()

  status_store.clear() #TODO: do this only if rebalanced
