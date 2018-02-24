import redis
import time

class Publisher():
  def __init__(self, channel, rate):
    self.channel = channel
    self.redis_cli = redis.Redis()
    self.rate = rate

  def publish(self, message):
    self.redis_cli.publish(self.channel, message)

  def start_publishing_from(self, source_file):
    with open(source_file, "r") as fp:
      for line in fp:
          self.publish(line)
          time.sleep(1.0/self.rate)

CHANNEL = "MFP_STREAM"
FILE = "tweets.txt"
RATE = 1000

if __name__ == "__main__":
  publisher = Publisher(CHANNEL, RATE)

  print "Starting publish..."
  while True:
    publisher.start_publishing_from(FILE)
