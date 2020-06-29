from tweepy import OAuthHandler
import numpy as np
import secrets
import tweepy
from datetime import date
import datetime
import pandas as pd
import os
import cv2
import io
import requests
from PIL import Image
with open('input.txt', 'r') as f:
    name = f.read()
    f.close()
auth = OAuthHandler(secrets.CONSUMER_KEY,secrets.CONSUMER_SECRET)
auth.set_access_token(secrets.ACCESS_TOKEN,secrets.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
today = date.today()
account_count = 1
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

def face_recognition(photo):
    face_cascade = cv2.CascadeClassifier(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python38\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
    filename = photo.split('/')[-1]
    r = requests.get(photo, allow_redirects=True)
    open("photos/" + filename, 'wb').write(r.content)
    img = cv2.imread("photos/" + filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 1)
    for (x,y,w,h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
    if len(faces) > 0:
        return "Has A Face"
    else:
        return "No Face"
    

try:
    
    usernames = []
    follow_c = []
    friends = []
    location = []
    creation_date = []
    num_of_tweets = []
    retweet_num = []
    profile_pic = []
    final_bot_score = []
    names = name.split()
    for name in names:
        user = api.get_user(name)
        retweet_count = 0
        outtweets = get_all_tweets(name)
        for tweet in outtweets:
            for i in tweet:
                if i.find("RT"):
                    retweet_count += 1
        retweet_ratio = retweet_count / len(outtweets)
        retweet_ratio = 1 - retweet_ratio
        usernames.append(name)
        follow_c.append(user.followers_count)
        friends.append(user.friends_count)
        location.append(user.location)
        creation_date.append(user.created_at)
        num_of_tweets.append(user.statuses_count)
        retweet_num.append(retweet_ratio)
        profile_pic.append(face_recognition(user.profile_image_url))
        bot_score = 0
        filename = user.profile_image_url.split('/')[-1]
        time_create = str(user.created_at)
        if user.followers_count / user.friends_count > .5 and user.followers_count / user.friends_count < 2:
            bot_score += 2
        if user.friends_count > 5000:
            bot_score += 3
        elif user.friends_count > 1000:
            bot_score += 2
        if retweet_ratio > .7:
            bot_score += 5
        if time_create.find("2016") or time_create.find("2017") or time_create.find("2018") or time_create.find("2019") or time_create.find("2020"):
            bot_score += 3
        if False: 
            bot_score += 2
        elif False:
            bot_score += 5
        if filename == "default_profile_normal.png":
            bot_score += 3
        elif face_recognition(user.profile_image_url) == "No Face":
            bot_score += 2
        final_bot_score.append(bot_score)
        account_count += 1
        print("Account No.")
        print(account_count)
    data = {'username' : usernames,
            'followers': follow_c,
            'follwing' : friends,
            'location' : location,
            'creation date' : creation_date,
            'number of tweets' : num_of_tweets,
            'Retweet Ratio' : retweet_num,
            'Profile Picture' : profile_pic,
            'Bot Score' : final_bot_score}
    df = pd.DataFrame(data)
    if os.path.exists('output.csv'):
        os.remove('output.csv')
    df.to_csv('output.csv', index = False)
except:
    raise Exception("Username does not exist")







