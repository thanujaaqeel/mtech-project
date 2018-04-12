from flask import Flask
from flask import request

from metric_processor import MetricProcessor
from optimizer import Optimizer

from metric_status import status_store

app = Flask(__name__)

TOTAL_EXECUTORS = 6
COMPONENTS = ["mfp"]
OPTIMIZE_INTERVAL = 5

@app.route('/metric', methods=['POST'])
def metric():
  MetricProcessor(request.json).process()
  return "success"

def optimizer_job():
  print "running optimizer_job"

  optimizer = Optimizer(total_executors=TOTAL_EXECUTORS, components=COMPONENTS)

  try:
    optimizer.optimize()
  except Exception as e:
    print "Error in optimize: ", e.message
    import traceback
    traceback.print_exc()

  status_store.clear() #TODO: do this only if rebalanced

@app.before_first_request
def schedule_optimizer_job():
  from apscheduler.schedulers.background import BackgroundScheduler as JobRunner
  job_runner = JobRunner()
  job_runner.add_job(optimizer_job, 'interval', seconds=OPTIMIZE_INTERVAL)
  job_runner.start()


