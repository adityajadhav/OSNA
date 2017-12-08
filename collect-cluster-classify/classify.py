from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from collections import defaultdict
import json
import re

neg_words = set()
pos_words = set()

data_base_directory  = "./data/"
tag_file_name = 'bitcoin_tweets.txt'
tag_friends_file_name = 'bitcoin_tweets_friends.txt'
output_file_name = 'classify_result.txt'

def download_afinn():
    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    f = zipfile.open('AFINN/AFINN-111.txt')
    afinn = dict()
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])
    return afinn

def afinn_sentiment(afinn):
    for a, b in afinn.items():
        if b > 0:
            pos_words.add(a)
        else:
            neg_words.add(a)
    return pos_words, neg_words

def remove_links(text):
    return re.sub('http\S+', ' ', text) 

def real_tweets(t):
    text = t.lower()
    text = re.sub('http\S+', ' ', text) 
    text = re.sub('@\S+', ' ', text) 
    return re.findall('[A-Za-z]+', text)

def read_tweets(file_path):
    tweets = list()
    f = open(file_path, 'r', encoding='utf-8')
    for line in f:
        result = dict()
        if len(line) > 1:
            tweet = json.loads(line)['text']
            result['tokens'] = real_tweets(tweet)
            result['tweet'] = remove_links(tweet)
            tweets.append(result)
    f.close()
    return tweets

def sentiment(tweet):
    pos = 0
    neg = 0
    for token in tweet['tokens']:
        if token in neg_words:
            neg += 1
        if token in pos_words:
            pos += 1
    return pos, neg
    
def clasify(tweets):
    positives = []
    negatives = []
    neutral = []
    for tweet in tweets:
        pos, neg = sentiment(tweet)
        if pos > neg:
            positives.append((tweet['tweet'], pos, neg))
        elif neg > pos:
            negatives.append((tweet['tweet'], pos, neg))
        else:
            neutral.append((tweet['tweet'],pos, neg))
    with open(output_file_name, 'w', encoding='utf-8') as f:
        f.write('Classify results: ')
        f.write('\n\nNumber of messages collected: '+ str(len(tweets)))
        f.write('\n\nNumber of Positive instances found: '+ str(len(positives)))
        f.write("\nOne example of Positive class: "+ str(sorted(positives, key=lambda x: x[1], reverse=True)[:1][0][0]))
        f.write('\n\nNumber of Negative instances found:'+ str(len(negatives)))
        f.write("\nOne example of Negative Class: "+ str(sorted(negatives, key=lambda x: x[2], reverse=True)[:1][0][0]))
        f.write('\n\nNumber of Neutral instances found:'+ str(len(neutral)))
        f.write("\nOne example of Neutral Class: "+ str(sorted(neutral, key=lambda x: x[2], reverse=True)[:1][0][0]))
def main():
    afinn = download_afinn()
    afinn_sentiment(afinn)
    tweets = read_tweets(data_base_directory + tag_file_name)
    clasify(tweets)

if __name__ == '__main__':
    main()