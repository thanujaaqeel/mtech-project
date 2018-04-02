import redis
import time
import datetime
import sys

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


def publish_for_training_data(channel, file):
  publisher = Publisher(channel)
  duration = 1 #mins
  for rate in range(100, 1001, 50):
    print "Starting publish at rate %d for duration: %d seconds" % (rate, duration*30)
    publisher.start_constant_rate_publishing(file, rate, duration*30)

def publish_realtime(channel, file):
  rates_and_duration = [(100, 1), (200, 1), (400, 3), (600, 3), (400, 2), (600, 2)]
  publisher = Publisher(channel)
  for rate, duration in rates_and_duration:
    print "Starting publish at rate %d for duration: %d seconds" % (rate, duration*60)
    publisher.start_constant_rate_publishing(file, rate, duration*60)

def publish_at_rate(channel, file, rate):
  publisher = Publisher(channel)
  print "Starting publish at rate %d" % rate
  publisher.start_constant_rate_publishing(file, rate, 6000000000)

CHANNEL = "MFP_STREAM"
FILE = "samples.txt"

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "training":
    print "TRAINING DATA SIMULATION..."
    publish_for_training_data(CHANNEL, FILE)
  elif len(sys.argv) > 2 and sys.argv[1] == "rate":
    publish_at_rate(CHANNEL, FILE, int(sys.argv[2]))
  else:
    print "REALTIME DATA SIMULATION..."
    publish_realtime(CHANNEL, FILE)

