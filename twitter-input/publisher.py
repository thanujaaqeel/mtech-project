import redis
import time
import datetime

class Publisher():
  def __init__(self, channel, rate_key):
    self.channel = channel
    self.redis_cli = redis.Redis()
    self.rate_key = rate_key
    self.count = 0
    self.start_time = None

  def publish(self, message):
    self.redis_cli.publish(self.channel, message)

  def start_publishing_from(self, source_file):
    with open(source_file, "r") as fp:
      for line in fp:
          self.publish(line)
          self.count += 1
          time.sleep(1.0/self.rate())
          self.measure_rate()

  def rate(self):
    return int(self.redis_cli.get(self.rate_key) or 10)

  def measure_rate(self):
    if self.start_time == None:
      self.start_time = datetime.datetime.now()

    measure_after = 1000
    if self.count == measure_after:
      time_diff = datetime.datetime.now() - self.start_time

      print "Total tweets in 1 second ", float(measure_after)/time_diff.total_seconds()

      self.count = 0
      self.start_time = datetime.datetime.now()

CHANNEL = "MFP_STREAM"
FILE = "samples.txt"
RATE_KEY = "MFP_STREAM_RATE"

if __name__ == "__main__":
  publisher = Publisher(CHANNEL, RATE_KEY)

  print "Starting publish..."
  while True:
    publisher.start_publishing_from(FILE)
