import twitter
import signal
import sys
import io
import re

class TweetsDownloader():
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, file_name):
        self.api = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret)
        self.file_name = file_name

    def write(self, text):
        self.file.write(text)
        self.file.write(unicode("\n"))

    def clean(self, text):
        if not text:
            return ''
        non_ascii_removed = self.remove_non_ascii(text)
        retweet_removed = self.remove_RT_prefix(non_ascii_removed)
        whitespace_removed = self.remove_extra_whitespace(retweet_removed)
        return whitespace_removed.strip()
    
    def remove_extra_whitespace(self, text):
        if not text:
            return text
        return re.sub('\s+', ' ', text)

    def remove_RT_prefix(self, text):
        if not text:
            return text

        return re.sub(r'^RT @.+:', '', text)

    def remove_non_ascii(self, text):
        if not text:
            return text

        removed_string = re.sub(r'[^\x00-\x7F]+','', text)
        chars_removed = len(text) - len(removed_string)
        if chars_removed >= 5:
            return ''
        return removed_string

    def process(self, tweet):
        text = self.get_text(tweet)

        cleaned_text = self.clean(text)

        if cleaned_text:
            self.write(cleaned_text)
    
    def get_text(self, tweet):
        try:
            return tweet['text']
        except KeyError:
            pass

    def start(self):
        signal.signal(signal.SIGINT, self.handle_sig_int)
        stream = self.api.GetStreamSample()
        self.file = io.open(self.file_name, 'a') 

        for tweet in stream:
            self.process(tweet)
        
        self.file.close()
        self.file = None

    def handle_sig_int(self, signal, frame):
        if self.file:
            self.file.close()
        sys.exit(0)

ACCESS_TOKEN = '703922350706659328-kJ41SmLhakxrEiavQxshunPFQsYbxC8'
ACCESS_SECRET = 'ccXywOKQooQrq1JEIq9vUBvovvTa1MUw7WdCMVi4uMgBQ'
CONSUMER_KEY = '6JaksxydkUZYog0v4r5Xf8saC'
CONSUMER_SECRET = 'kmHlaxlqKxuvreD4aDya3QJPT431qFhwuJCIkBmr6O9M7FLEO2'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage python client.py <output_file>"
        exit(0)

    output_file = sys.argv[1]
    
    downloader = TweetsDownloader(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET, output_file)
    downloader.start()
    

