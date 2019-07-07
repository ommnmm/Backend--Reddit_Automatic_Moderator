from django.shortcuts import render
from vectorizer.views import rm_stop, tfidf_vectorize, lr_tfidf
from extractor.views import commentExtractor

#
# from extract import commentExtractor
# from vectorize import rm_stop
# from vectorize import tfidf_vectorize
# from vectorize import lr_tfidf

from django.http import HttpResponse
import json
import numpy as np
from time import time
import pandas as pd



def recommender(request):


    # 0.5 is classifier default
    threshold3 = 0.75
    threshold2 = 0.5
    threshold1 = 0.25


    period = request.GET['period']
    #request = 2019020320190204
    #endtime = request.GET['endtime']

    df_extracted = commentExtractor(period)

    df = rm_stop(df_extracted)

    tfidf_vec = tfidf_vectorize(df['body'])

    y_pre, y_prob = lr_tfidf(tfidf_vec)
    df ['proba_bad'] = y_prob[:,0]
    print('proba_bad',df ['proba_bad'])

    df['label'] = None
    df['label'].loc[(df['proba_bad'] >= threshold3)] = 'red'
    df['label'].loc[(df['proba_bad'] >= threshold2) & (df['proba_bad'] < threshold3)] = 'yellow'
    df['label'].loc[(df['proba_bad'] >= threshold1) & (df['proba_bad'] < threshold2)] = 'green'
    df.dropna(subset=['label'], inplace=True)
    tic = time()

    found = False

    if len(y_prob) != 0:
        found = True

    #df = pd.DataFrame([1,2],[3,4])

    print("Time lapse {}".format(time() - tic))
    df = df.astype(str) # resolve df.to_json seg fault
    response_dict = {
        'found': found,
        'comments': df.to_dict(orient='record')
    }

    response = json.dumps(response_dict)
    print('response',response)
    return HttpResponse(response)
