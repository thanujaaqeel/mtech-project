from flask import Flask
from flask import request

from metric_processor import MetricProcessor

app = Flask(__name__)

@app.route('/metric', methods=['POST'])
def metric():
  MetricProcessor(request.json).process()

  return "success"
