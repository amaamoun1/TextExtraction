# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:00:34 2020

@author: Asser.Maamoun
"""

import re
import random
import pandas as pd
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sn
import collections
from sklearn.feature_extraction.text import TfidfVectorizer

import datetime
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

from gensim.models import Phrases
from gensim import corpora

from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from pprint import pprint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import ShuffleSplit



#############################################################################
# create a sample of scorecard items to look at
#############################################################################

# load the data and subset rows with assigned topics
df_scorecard = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/clustering/scorecard_notes_edited.xlsx")

# add the topic encoding
df_types = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/clustering/scorecard_types.xlsx")
df_types = df_types.rename({'types':'topic_true', 'codes':'topic_true_code'}, axis=1)
df_scorecard = df_scorecard.merge(df_types, how='left')

###############################################################################
#      TEXT PREP: Remove stopwords, Stem, Vectorize, and Bigrams
###############################################################################


#select the stopwords and stemmer to use
stopwords = nltk.corpus.stopwords.words('english')
stopadditions = ["name", "u+27a2"]
stopwords = stopwords + stopadditions
drop_lemmas = ["e.g."]
#could add extra words to stopwords
lemmatizer = WordNetLemmatizer()

def wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
    
def get_lemmas(tokenized_text):
    lemmas = []
    for word, pos in nltk.pos_tag(tokenized_text):
        result_pos=wordnet_pos(pos)
        if result_pos != None:
            lemmas.append(lemmatizer.lemmatize(word, result_pos))
        else:
            lemmas.append(word)
    return lemmas

def tokenize_and_lemma(text):
    """Lowercase, remove stopwords, and lemmatize"""
    tokens = [word.lower() for word in nltk.word_tokenize(text)]
    # filter out any tokens that are stopwords or that do not contain letters (e.g., numeric tokens, raw punctuation)
    filtered_tokens = []
    for token in tokens:
        if (token not in stopwords) and ('u+' not in token):
            if (re.search('\\d', token)): 
                filtered_tokens.append("number")
            else:
                filtered_tokens.append(token)
    lemmas = get_lemmas(filtered_tokens)
    filtered_lemmas = []
    for lemma in lemmas:
        if lemma not in drop_lemmas:
            filtered_lemmas.append(lemma)
    return filtered_lemmas

def add_bigrams(bow):
    bigram = Phrases(bow, min_count=20) #finds bigrams that appear atleast 20 times in data
    bigrams_found = set()
    for idx in range(len(bow)):
        for token in bigram[bow[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                bigrams_found.add(token)
                bow[idx].append(token)
    return bow, bigrams_found

def prep_data(texts):
    bow = [tokenize_and_lemma(text) for text in texts]
    bow, bigrams = add_bigrams(bow)
    id2word = corpora.Dictionary(bow)
    id2word.filter_extremes(no_below=20, no_above=0.5)
    corpus = [id2word.doc2bow(doc) for doc in bow]
    return bow, id2word, corpus

def get_bow(texts):
    bow = [tokenize_and_lemma(text) for text in texts]
    bow, bigrams = add_bigrams(bow)
    return bow

#create the vectorized descriptions
print("lemming w/o tfidf", datetime.datetime.now().strftime('%H:%M:%S'))
df_scorecard['bow'] = [" ".join(x) for x in get_bow(list(df_scorecard['head']))]
print("ended", datetime.datetime.now().strftime('%H:%M:%S'))


###############################################################################
#      Feature Creation
###############################################################################

df_assigned = df_scorecard[pd.notnull(df_scorecard['topic_true'])]

bow_train = list(df_assigned[df_assigned['sample_train']==1]['bow'])
bow_test = list(df_assigned[df_assigned['sample_test']==1]['bow'])
bow_all = list(df_assigned['bow'])
y_train = list(df_assigned[df_assigned['sample_train']==1]['topic_true_code'])
y_test = list(df_assigned[df_assigned['sample_test']==1]['topic_true_code'])
y_all = list(df_assigned['topic_true_code'])

# Parameter election
ngram_range = (1,1)
min_df = 0.01
max_df = 0.30
max_features = None

tf = TfidfVectorizer(encoding='utf-8',
                        ngram_range=ngram_range,
                        stop_words=None,
                        lowercase=False,
                        max_df=max_df,
                        min_df=min_df,
                        max_features=max_features,
                        sublinear_tf=True,
                        use_idf=False)
   
#convert to feature vectors
X_train = tf.fit_transform(bow_train).toarray()
print(X_train.shape)

X_test = tf.transform(bow_test).toarray()
print(X_test.shape)

X_all = tf.fit_transform(bow_all).toarray()
print(X_all.shape)

###############################################################################
#      MOdel eval
###############################################################################

def model_eval(y_train, y_test, y_pred_train, y_pred_test):
    # Training accuracy
    print("The training accuracy is: ")
    print(accuracy_score(y_train, y_pred_train))
    
    # Test accuracy
    print("The test accuracy is: ")
    print(accuracy_score(y_test, y_pred_test))
    
    # Classification report
    print("Classification report")
    print(classification_report(y_test,y_pred_test))
    
    #confusion matrix
    dict_types = dict(zip(df_types.topic_true, df_types.topic_true_code))
    labs = [x for x in list(dict_types.keys()) if (dict_types[x] in y_test) or (dict_types[x] in y_pred_test)]
    
    confusion = confusion_matrix(y_test, y_pred_test) #true, pred
    confusion = pd.DataFrame(confusion, index = labs, columns = labs)
    
    sn.set(font_scale=1)
    plt.figure(figsize=(10,7))
    sn.heatmap(confusion, annot=True)
    
    plt.ylabel('True', fontsize=15)
    plt.xlabel('Predicted', fontsize=15)
    plt.title('Confusion matrix', fontsize=20)
    plt.show()
    

###############################################################################
#      Classify via Multinomial Bayes
###############################################################################

#classify
mnbc = MultinomialNB()
mnbc.fit(X_train, y_train)
y_pred_test = mnbc.predict(X_test)
y_pred_train = mnbc.predict(X_train)

model_eval(y_train, y_test, y_pred_train, y_pred_test)


###############################################################################
#      Classify via Nearest Neighbors
###############################################################################

#number of neighbors to check
n_neighbors = [int(x) for x in np.arange(5, 105, 5)]
param_grid = {'n_neighbors': n_neighbors}

# Create a base model
knnc = KNeighborsClassifier()

# Manually create the splits in CV in order to be able to fix a random_state (GridSearchCV doesn't have that argument)
cv_sets = ShuffleSplit(n_splits = 3, test_size = .33, random_state = 8)

# Instantiate the grid search model
grid_search = GridSearchCV(estimator=knnc, 
                           param_grid=param_grid,
                           scoring='accuracy',
                           cv=cv_sets,
                           verbose=1)

# Fit the grid search to the data
grid_search.fit(X_all, y_all)

print("The best hyperparameters from Grid Search are:")
print(grid_search.best_params_)

print("The mean accuracy of a model with these hyperparameters is:")
print(grid_search.best_score_)


###############################################################################
#      Classify via Logistic Regression
###############################################################################


lr_0 = LogisticRegression(random_state = 8)
print('Parameters currently in use:\n')
pprint(lr_0.get_params())

# Parameter grid
C = [float(x) for x in np.linspace(start = 0.1, stop = 1, num = 10)]
multi_class = ['multinomial']
solver = ['newton-cg', 'sag', 'saga', 'lbfgs']
class_weight = ['balanced', None]
penalty = ['l2']

random_grid = {'C': C,
               'multi_class': multi_class,
               'solver': solver,
               'class_weight': class_weight,
               'penalty': penalty}

pprint(random_grid)


# First create the base model to tune
lrc = LogisticRegression(random_state=8)
random_search = RandomizedSearchCV(estimator=lrc,
                                   param_distributions=random_grid,
                                   n_iter=100,
                                   scoring='accuracy',
                                   cv=3, 
                                   verbose=1, 
                                   random_state=8)

# Fit the random search model
random_search.fit(X_all, y_all)
best_lrc = random_search.best_estimator_
best_lrc.fit(X_train, y_train)

y_pred_test = best_lrc.predict(X_test)
y_pred_train = best_lrc.predict(X_train)

model_eval(y_train, y_test, y_pred_train, y_pred_test)




