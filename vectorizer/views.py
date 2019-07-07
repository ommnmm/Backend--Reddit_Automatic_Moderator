from django.shortcuts import render
from extractor.views import commentExtractor

import re
import nltk
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import punkt
from nltk.tokenize import RegexpTokenizer


path = "/Users/superpooh/Desktop/data_science_project/Insight/iama/revised_query/reddit_NLP_automoderator/"
# trained from iama_modeling.ipynb
count_vectorizer =  pickle.load(open(path+'count_vectorizer.txt', 'rb'))
tfidf_vectorizer =  pickle.load(open(path+'tfidf_vectorizer.txt', 'rb'))
lrmodel =  pickle.load(open(path+'lrmodel.txt', 'rb'))
lrmodel_tfidf =  pickle.load(open(path+'lrmodel_tfidf.txt', 'rb'))
rfmodel_tfidf =  pickle.load(open(path+'rfmodel_tfidf.txt', 'rb'))

nltk.download('punkt')
tokenizer = RegexpTokenizer(r'\w+')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
set2 = ['im','youre','hes','shes','theyre','thats','whats','theres','therere','dont','didnt','don','didn','cant','couldnt','couldn','youve','ive','could','would','id','youd','shed','hed','theyd','itll','shell','hell','ill','youll','theyll']
stop_words.update(set2)

def rm_stop(df):
    df2 = df.copy()
    ran = int(df2['body'].shape[0])
    for i in range (0, ran):
        word_tokens = word_tokenize(df2['body'].iloc[i])
        filtered_sentence = []

        for w in word_tokens:
            if w not in stop_words:
                filtered_sentence.append(w)
        df2['body'].iloc[i] = filtered_sentence
    df2['body'] = df2['body'].apply(' '.join)

    return df2

def tfidf_vectorize(s):
    # s: pandas series
    vec_tfidf = tfidf_vectorizer.transform(s)
    return vec_tfidf

# 0: bad  1:good.  prob = [prob_is_bad, prob_is_good]
def lr_tfidf(s):
    # s: vectorized test set
    y_predicted = lrmodel_tfidf.predict(s)
    y_prob_predicted =  lrmodel_tfidf.predict_proba(s)
    return y_predicted, y_prob_predicted


# def doc2tag(text):
#
#     sentences = nltk.sent_tokenize(text)
#     noun_list = []
#     for s in sentences:
#         tokens = nltk.word_tokenize(s)
#         text_tagged = nltk.pos_tag(tokens)
#         pair = [(word, pos) for (word, pos) in text_tagged]
#         noun_list.extend(pair)
#
#     return noun_list
#
#
# def nnp_nn(text):
#
#     patterns = "NNP_NN: {<NNP>+(<NNS>|<NN>+)}"  # at least one NNP followed by NNS or at least one NN
#     parser = nltk.RegexpParser(patterns)
#     p = parser.parse(doc2tag(text))
#     phrase = []
#     for node in p:
#         if type(node) is nltk.Tree:
#             phrase_str = ''
#             for w in node:
#                 phrase_str += w[0]
#                 phrase_str += ' '
#             phrase_str = phrase_str.strip()
#             phrase.append(phrase_str)
#     return phrase
#
#
# def jj_nn(text):
#
#     patterns = "NNP_NN: {<JJ>+(<NN>+)}"  #
#     parser = nltk.RegexpParser(patterns)
#     p = parser.parse(doc2tag(text))
#     phrase = []
#     for node in p:
#         if type(node) is nltk.Tree:
#             phrase_str = ''
#             for w in node:
#                 phrase_str += w[0]
#                 phrase_str += ' '
#             phrase_str = phrase_str.strip()
#             phrase.append(phrase_str)
#     return phrase
#
#
# def tf_idf(text, key_tokens, idf_dict, ngram=3):
#     tf_idf_dict = defaultdict(int)
#
#     # tokens been used for tf-idf
#     text = text.lower()
#
#     tokens = nltk.word_tokenize(text)
#
#     token_list = []
#     for i in range(1, ngram + 1):
#         token_list.extend(nltk.ngrams(tokens, i))
#     token_list = [' '.join(token) for token in token_list]
#
#     # lemmatize the tokens
#     for i, token in enumerate(token_list):
#         token_list[i] = lemmatizer.lemmatize(token)
#
#     # initialize to full dimension
#     for token in key_tokens:
#         tf_idf_dict[token] = 0
#
#     # count
#     for token in token_list:
#         if token in key_tokens:
#             tf_idf_dict[token] += 1
#
#     for key in tf_idf_dict.keys():
#         tf_idf_dict[key] = tf_idf_dict[key] * idf_dict[key]
#
#     tf_idf_vec = np.zeros((len(key_tokens),))
#     for i, key in enumerate(key_tokens):
#         tf_idf_vec[i] = tf_idf_dict[key]
#
#     # returns a normalized 1d np array
#     tf_idf_vec = tf_idf_vec / np.linalg.norm(tf_idf_vec)
#
#     return tf_idf_vec
#
#
