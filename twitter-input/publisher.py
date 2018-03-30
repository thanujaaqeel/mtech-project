import redis
import time
import datetime

class Publisher():
  def __init__(self, channel):
    self.channel = channel
    self.redis_cli = redis.Redis()

  def publish(self, message):
    self.redis_cli.publish(self.channel, message)

  def start_constant_rate_publishing(self, source_file, rate, duration):
    start_time = datetime.datetime.now()
    should_publish = True
    while should_publish:
      with open(source_file, "r") as fp:
        for line in fp:
          self.publish(line)

          time.sleep(1.0/rate)

          now = datetime.datetime.now()
          time_diff = (now - start_time).total_seconds()
          if time_diff > duration:
            should_publish = False
            break


CHANNEL = "MFP_STREAM"
FILE = "samples.txt"

RATES = [(100, 1), (200, 1), (400, 3), (600, 3), (400, 2), (600, 2)]

if __name__ == "__main__":
  publisher = Publisher(CHANNEL)
  for rate, duration in RATES:
    print "Starting publish at rate %d for duration: %d seconds" % (rate, duration*60)
    publisher.start_constant_rate_publishing(FILE, rate, duration*60)

