import redis
import time
import datetime
import sys

class Publisher():
  def __init__(self, channel, source_file, window_size, delay=10):
    self.channel = channel
    self.redis_cli = redis.Redis()
    self.source_file = source_file
    self.window_size = window_size
    self.delay = str(delay)

  def publish(self, messages):
    messages = [self.delay] + messages #first item in list is the delay
    self.redis_cli.publish(self.channel, "\t".join(messages))

  def start_constant_rate_publishing(self, rate, duration):
    start_time = datetime.datetime.now()
    should_publish = True
    window = []
    while should_publish:
      with open(self.source_file, "r") as fp:
        for line in fp:
          window.append(line.strip())
          if len(window) == self.window_size:
            self.publish(window)
            window = []
            time.sleep(1.0/rate)

            now = datetime.datetime.now()
            time_diff = (now - start_time).total_seconds()
            if time_diff > duration:
              should_publish = False
              break

CHANNEL = "MFP_STREAM"
FILE = "samples.txt"
WINDOW_SIZE = 25

def publish_for_training_data():
  publisher = Publisher(CHANNEL, FILE, WINDOW_SIZE)
  duration = 1 #mins
  for rate in range(100, 1001, 50):
    print "Starting publish at rate %d for duration: %d seconds" % (rate, duration*30)
    publisher.start_constant_rate_publishing(rate, duration*30)

def publish_realtime():
  rates_and_duration = [(100, 1), (200, 1), (400, 3), (600, 3), (400, 2), (600, 2)]
  publisher = Publisher(CHANNEL, FILE, WINDOW_SIZE)
  for rate, duration in rates_and_duration:
    print "Starting publish at rate %d for duration: %d seconds" % (rate, duration*60)
    publisher.start_constant_rate_publishing(rate, duration*60)

def publish_at_rate(rate):
  publisher = Publisher(CHANNEL, FILE, WINDOW_SIZE)
  print "Starting publish at rate %d" % rate
  publisher.start_constant_rate_publishing(rate, 6000000000)



if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "training":
    print "TRAINING DATA SIMULATION..."
    publish_for_training_data()
  elif len(sys.argv) > 2 and sys.argv[1] == "rate":
    rate = int(sys.argv[2])
    publish_at_rate(rate)
  else:
    print "REALTIME DATA SIMULATION..."
    publish_realtime()

