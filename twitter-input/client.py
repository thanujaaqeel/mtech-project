import twitter
import signal
import sys
import io

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


ACCESS_TOKEN = '703922350706659328-kJ41SmLhakxrEiavQxshunPFQsYbxC8'
ACCESS_SECRET = 'ccXywOKQooQrq1JEIq9vUBvovvTa1MUw7WdCMVi4uMgBQ'
CONSUMER_KEY = '6JaksxydkUZYog0v4r5Xf8saC'
CONSUMER_SECRET = 'kmHlaxlqKxuvreD4aDya3QJPT431qFhwuJCIkBmr6O9M7FLEO2'



api = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET)

stream = api.GetStreamSample()
file = io.open('tweets.txt', 'w') 


for tweet in stream:
    try:
       file.write(tweet['text'])
       
    except KeyError:
        pass
file.close()