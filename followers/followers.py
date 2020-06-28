from tweepy import OAuthHandler
import secrets
import tweepy
from datetime import date
import pandas as pd
import os
with open('input.txt', 'r') as f:
    name = f.read()
    f.close()
auth = OAuthHandler(secrets.CONSUMER_KEY,secrets.CONSUMER_SECRET)
auth.set_access_token(secrets.ACCESS_TOKEN,secrets.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
today = date.today()
def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method 
    #initialize a list to hold all the tweepy Tweets
    alltweets = []  
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)
    
    #save most recent tweets
    alltweets.extend(new_tweets)
    
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")
        
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
        print(f"...{len(alltweets)} tweets downloaded so far")
    
    #transform the tweepy tweets into a 2D array that will populate the csv 
    outtweets = [[tweet.text] for tweet in alltweets]
    return outtweets
try:
    usernames = []
    follow_c = []
    friends = []
    location = []
    creation_date = []
    num_of_tweets = []
    retweet_num = []
    names = name.split()
    for name in names:
        user = api.get_user(name)
        retweet_count = 0
        tweets_found = 0
        outtweets = get_all_tweets(name)
        for tweet in outtweets:
            tweets_found += 1
            if "RT" in tweet == True:
                retweet_count += 1
        retweet_ratio = retweet_count / tweets_found
        follow_c.append(user.followers_count)
        usernames.append(name)
        friends.append(user.friends_count)
        location.append(user.location)
        creation_date.append(user.created_at)
        num_of_tweets.append(user.statuses_count)
        retweet_num.append(retweet_ratio)
    data = {'username' : usernames,
            'followers': follow_c,
            'follwing' : friends,
            'location' : location,
            'creation date' : creation_date,
            'number of tweets' : num_of_tweets,
            'Retweet Ratio' : retweet_num}
    df = pd.DataFrame(data)
    if os.path.exists('output.csv'):
        os.remove('output.csv')
    df.to_csv('output.csv', index = False)
except:
    raise Exception("Username does not exist")







