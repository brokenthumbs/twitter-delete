from datetime import datetime, timedelta
import json
import os
import re
import sys
import time
import tweepy

cutoff_date = datetime.now() - timedelta(weeks=int(os.environ.get("WEEKS_CUTOFF", 12)))
favorite_cutoff = int(os.environ.get("FAVORITE_CUTOFF", 10))
retweet_cutoff = int(os.environ.get("RETWEET_CUTOFF", 10))

auth = tweepy.OAuthHandler(os.environ.get("TWITTER_CONSUMER_KEY"), os.environ.get("TWITTER_CONSUMER_SECRET"))
auth.set_access_token(os.environ.get("TWITTER_ACCESS_TOKEN"), os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"))
api = tweepy.API(auth)

def print_tweet(status):

  retweeted = status._json["retweeted"] or status.text.startswith("RT @")
  favorite_count = status._json["favorite_count"]
  retweet_count = status._json["retweet_count"]

  print(status.id_str)
  print(status.created_at)
  print(status.text)
  print("Retweeted: {}".format(retweeted))
  print("Favorites: {}".format(favorite_count))
  print("Retweets: {}".format(retweet_count))
  print("")

  # the tweet is older than the cutoff_date
  # check to see if this tweet can be deleted
  if re.match("Verifying myself: I am .* on", status.text) is not None:
    print("Do not delete Keybase proof.")
  elif status.created_at < cutoff_date:
    if retweeted:
      print("Deleting Retweet ...")
      api.destroy_status(id = status.id)
    elif favorite_count < favorite_cutoff:
      print("Deleting old tweet, less than {} favorites ...".format(favorite_cutoff))
      api.destroy_status(id = status.id)
    elif retweet_count < retweet_cutoff:
      print("Deleting old tweet, less than {} retweets ...".format(retweet_cutoff))
      api.destroy_status(id = status.id)

  print("----------\n")

def fetch_old_tweets(max_id):
  time.sleep(5)

  if max_id > 0:
    tweets = api.user_timeline(max_id=max_id, count=200)
  else:
    tweets = api.user_timeline(count=200)

  total = 0
  oldest_id = 0

  for status in tweets:
    total = total + 1
    print_tweet(status)
    oldest_id = status.id

  return total, oldest_id

max_id = 0
if len(sys.argv) >= 2:
  max_id = int(sys.argv[1])

oldest_id = 0
total = 0
eof = False
api_calls = 0

try:
  while True:
    api_calls = api_calls + 1
    local_total, oldest_id = fetch_old_tweets(max_id)
    total = total + local_total
    if oldest_id > 0:
      max_id = oldest_id - 1
    elif oldest_id == 0:
      break
    else:
      max_id = max_id - 200

finally:
  print("")
  print("Total tweets:", total)
  print("Total api calls:", api_calls)
  print("Max ID:", max_id)
  print("")
