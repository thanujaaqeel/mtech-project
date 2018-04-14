from flask import Flask
from flask import request

from metric_processor import MetricProcessor
from jobs import optimizer_job

OPTIMIZER_JOB_INTERVAL = 5

app = Flask(__name__)

@app.route('/metric', methods=['POST'])
def metric():
  MetricProcessor(request.json).process()
  return "success"

@app.before_first_request
def schedule_optimizer_job():
  from apscheduler.schedulers.background import BackgroundScheduler as JobRunner
  job_runner = JobRunner()
  job_runner.add_job(optimizer_job, 'interval', seconds=OPTIMIZER_JOB_INTERVAL)
  job_runner.start()


