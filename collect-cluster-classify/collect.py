"""
collect.py
"""
import os
import sys
import time
import pathlib 
from TwitterAPI import TwitterAPI
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

data_base_directory  = "./data/"
tag = 'bitcoin' 
tag_file_name = 'bitcoin_tweets.txt'
tag_friends_file_name = 'bitcoin_tweets_friends.txt' 

access_token = '113696974-Qzz5hFq0ECZzgCvU6vrU088G32HyxGMokvfM7S6e'
access_token_secret = 'x1vumcNsfwrghcjI0BcGKzW042X1dIxqN6iq3NhqrgEAm' 
consumer_key = 'TJy2h0rj4OhWZo3md1IXgfJeD'
consumer_secret = '4ws0axGatFIK186yJmBqWcuFX8yvLDhN93X4nfhhN29HNqLmV2'

def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

class StreamCollectorListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def __init__(self):
        self.count = 1

    def on_data(self, data):
        if self.count > 100:
            return False
        jsonObj = json.loads(data)
        if 'text' in jsonObj:
            print(jsonObj['text'])
            if not jsonObj['text'].lower().startswith('rt'):
                self.write_to_file(data_base_directory + tag_file_name, data)
                self.count += 1
       
        return True
        
    def on_error(self, status):
        print(status)

    def write_to_file(self, file_name, data):
        """write twittes to file."""
        try:
            with open(file_name, 'a') as outfile:
                outfile.write(data)
        except BaseException as e:
            print("Error on_status: %s" % str(e))

def init():
    if not os.path.exists(data_base_directory):
        os.makedirs(data_base_directory)

    for file in os.listdir(data_base_directory):
        file_path_str = data_base_directory + file
        file_path = pathlib.Path(file_path_str)
        try:
            if file_path.is_file():
                os.remove(file_path)
        except Exception as e:
            print(e)

def collect_tweets(auth, stream_collector_listener):
    stream = Stream(auth, stream_collector_listener)
    stream.filter(track = [tag], languages = ['en']) 

def collect_friends_data():
    friends_list = list()
    file = open(data_base_directory + tag_file_name, 'r')
    for line in file:
        if len(line) > 1:
            friends_list.append(json.loads(line)['user']['screen_name'])

    for friend_screen_name in friends_list:
        req = robust_request(get_twitter(), 'friends/ids', {'screen_name': friend_screen_name, 'count': 5000})
        with open(data_base_directory + tag_friends_file_name, 'a') as f:
            friend_list = json.loads(req.text)["ids"][:5000]
            if len(friend_list) > 0:
                friend = dict()
                friend['screen_name'] = friend_screen_name
                friend['friend_ids'] = friend_list
                friend_str = json.dumps(friend)
                f.write(friend_str)
                f.write('\n')


if __name__ == '__main__':

    init()
    stream_collector_listener = StreamCollectorListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    collect_tweets(auth, stream_collector_listener)
    collect_friends_data()
       