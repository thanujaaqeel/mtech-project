from flask import Flask
from flask import request

from metric_processor import MetricProcessor

app = Flask(__name__)

@app.route('/metric', methods=['POST'])
def metric():
  MetricProcessor(request.json).process()
  return "success"

def optimizer_job():
  print "running optimizer_job"

@app.before_first_request
def schedule_optimizer_job():
  print "scheduling optimizer_job"
  from apscheduler.schedulers.background import BackgroundScheduler as JobRunner
  job_runner = JobRunner()
  job_runner.add_job(optimizer_job, 'interval', seconds=2)
  job_runner.start()


