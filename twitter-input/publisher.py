import redis
import time
import datetime

class Publisher():
  def __init__(self, channel, rate_range, rate_step, rate_interval):
    self.channel = channel
    self.redis_cli = redis.Redis()
    self.rate_range = rate_range
    self.rate_step = rate_step
    self.rate_interval = rate_interval
    self.count = 0
    self.start_time = None

  def publish(self, message):
    self.redis_cli.publish(self.channel, message)

  def start_constant_rate_publishing(self, source_file, rate, duration):
    self.start_time = datetime.datetime.now()
    should_publish = True
    while should_publish:
      with open(source_file, "r") as fp:
        for line in fp:
          self.publish(line)

          self.count += 1
          time.sleep(1.0/rate)
          now = datetime.datetime.now()
          time_diff = (now - self.start_time).total_seconds()
          if time_diff > duration:
            should_publish = False
            break


  def start_publishing_from(self, source_file):
    start_rate, end_rate = self.rate_range
    current_rate = start_rate
    self.start_time = datetime.datetime.now()

    while True:
      with open(source_file, "r") as fp:
        for line in fp:
            self.publish(line)

            self.count += 1
            time.sleep(1.0/current_rate)
            now = datetime.datetime.now()
            time_diff = (now - self.start_time).total_seconds()
            if time_diff >= self.rate_interval:
              current_rate += self.rate_step
              self.start_time = now
              self.count = 0
              print "current_rate: %s" % current_rate
              if current_rate > end_rate or current_rate <= start_rate:
                self.rate_step = self.rate_step*-1


CHANNEL = "MFP_STREAM"
FILE = "samples.txt"

RATE_RANGE = (100, 3500)
RATE_STEP = 50
RATE_INTERVAL_SECONDS = 10

if __name__ == "__main__":
  publisher = Publisher(CHANNEL, RATE_RANGE, RATE_STEP, RATE_INTERVAL_SECONDS)

  print "Starting publish..."
  publisher.start_constant_rate_publishing(FILE, 100, 6000000)
  #publisher.start_publishing_from(FILE)
