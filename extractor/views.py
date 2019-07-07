from django.shortcuts import render
import requests
import json
import pandas as pd
import numpy as np
import praw
import datetime as dt
import psaw
from psaw import PushshiftAPI




def standardize_text(df, text_field):
    df[text_field] = df[text_field].str.replace(r"\\n", "")
    df[text_field] = df[text_field].str.replace(r"\\n\\n", "")
    df[text_field] = df[text_field].str.replace(r"[", "")
    df[text_field] = df[text_field].str.replace(r"\']", "")
    df[text_field] = df[text_field].str.replace(r"\\\',", "")
    df[text_field] = df[text_field].str.replace(r"\'\"\\\'", "")
    df[text_field] = df[text_field].str.replace(r"\'\\\'\"", " ")
    df[text_field] = df[text_field].str.replace(r"\"\",", "")
    df[text_field] = df[text_field].str.replace(r"\'\\\'\"", "")
    df[text_field] = df[text_field].str.replace(r"\\", " ")
    df[text_field] = df[text_field].str.replace(r"http\S+", "")
    df[text_field] = df[text_field].str.replace(r"http", "")
    df[text_field] = df[text_field].str.replace(r"@\S+", "")
    df[text_field] = df[text_field].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
    df[text_field] = df[text_field].str.replace(r"@", "at")
    df[text_field] = df[text_field].str.replace(r"\"", "")
    df[text_field] = df[text_field].str.replace(r"[0-9]", "")
    df[text_field] = df[text_field].str.replace(r"\'", "")
    df[text_field] = df[text_field].str.replace(r"\,\ \"", "")
    df[text_field] = df[text_field].str.replace("\"", "")
    df[text_field] = df[text_field].str.replace(r",", "")
    df[text_field] = df[text_field].str.replace(r"?", "")
    df[text_field] = df[text_field].str.replace(r"(", "")
    df[text_field] = df[text_field].str.replace(r")", "")
    df[text_field] = df[text_field].str.replace(r"!", "")
    df[text_field] = df[text_field].str.lower()
    return df

def commentExtractor(period):


    reddit = praw.Reddit(client_id='8Bh6NinWBjtCJg', client_secret='ZxmDqTuP6wyyPCGhe6NF5ZH0eZY',
                         user_agent='Stella Li')
    api = PushshiftAPI()

    ## extract post info from pushshift (btw start time and end time)
    tmp = str(period)
    starttime = tmp[0:8]
    endtime = tmp[8:16]


    yr = int(starttime[0:4])
    m = int(starttime[4:6])
    d = int(starttime[6:8])
    start_epoch = int(dt.datetime(yr, m, d).timestamp())
    yr = int(endtime[0:4])
    m = int(endtime[4:6])
    d = int(endtime[6:8])
    end_epoch = int(dt.datetime(yr, m, d).timestamp())

    kk = list(api.search_submissions(before=end_epoch, after=start_epoch, subreddit='IAmA', limit=20000))

    strs = [''] * len(kk)

    for i in range(1, len(kk) - 1):
        strs[i] = kk[i]

    data = np.array(strs)

    for i in range(0, len(data) - 1):
        data[i] = str(data[i])
        s = pd.Series(data)

    df = pd.DataFrame()
    df = s.str.split(',', expand=True)

    # extract columns of post info that contains post id
    cache1 = pd.Series([])
    cache2 = pd.Series([])

    for i in range(0, 50):
        df.dropna(inplace=True, subset=[i])
        dftmp = df[i][df[i].str.contains("id=")]

        cache1 = cache2.append(dftmp)
        cache2 = cache1

    cache1 = cache2[~cache2.str.contains("subreddit_id")]

    # clean pd series of post id

    s2 = cache1.str.split('=\'', expand=True)
    s3 = s2[1].str.split('\'', expand=True)
    s3.dropna(inplace=True)
    s4 = s3[0]
    s4.dropna(inplace=True)
    s4.reset_index(inplace=True, drop=True)
    s5 = s4.tolist()
     # exclude removed posts
    for i in range(0, s4.shape[0]):
        submission = reddit.submission(id=s5[i])
        if submission.author is None:
            s4.drop(labels=i, inplace=True)

    s4.reset_index(inplace=True, drop=True)
    s4 = s4.loc[s4.str.len() == 6]
    s5 = s4.tolist()
    # add later:s5 = s5.loc[s5['id'].str.len()==6]
    # extract comment id of "all" posts (perhaps exclude removed posts later)
    ran1 = 0
    ran2 = s4.shape[0]
    commentlist = []

    for i in range(ran1, ran2):
        submission = reddit.submission(id=s5[i])
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if comment.author != 'AutoModerator' and comment.author is not None:
                commentlist.append([comment.id, comment.permalink, comment.body, comment.author])
    headers = ['id','link','body','author']
    df = pd.DataFrame(commentlist,columns=headers)
    df = standardize_text(df,'body')
    df.sort_index(inplace=True)
    df.reset_index(inplace=True)
    df.pop('index')

    return df
# test complete :)