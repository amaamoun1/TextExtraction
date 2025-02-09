# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 08:53:32 2020

@author: -
"""


import datetime
import re
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet
from nltk import everygrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from gensim.models import Phrases
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel


###############################################################################
#      Important Paths
###############################################################################

path_onedrive = "C:/Users/amaamoun/OneDrive - ghSMART/ghSMART_project/"
path_out = "C:/Users/amaamoun/Desktop/Kaplan/TextExtractionOutput/"
path_data = path_onedrive + "extractions_merged_anonymized_deduplicated.xlsx" 

###############################################################################
#      Grab data from most common competencies
###############################################################################

#load data
data = pd.read_excel(path_data)
data = data[['doc_id_old', 'doc_id_new', 'title_clean'] + [x for x in data.columns if re.match("^comp_merged", x)] ]

#keep ceos
data = data[data['title_clean']=="ceo"]
data = data.drop('title_clean', axis=1)

#keep competencies with enough data
def numAllCol(df, columns):
    temp = df.copy()
    temp = temp[columns]
    num_null = list(temp.apply(lambda x: x.isnull().sum(), axis='columns'))
    total_obs = num_null.count(0)
    return total_obs

dataCounts = pd.DataFrame(len(data) - data.apply(lambda x: x.isnull().sum(), axis='rows'))
dataCounts = dataCounts.reset_index()
dataCounts.columns = ['variable', 'count']

comp1000 = list(dataCounts[dataCounts['count']>1000]['variable'])
comp1100 = list(dataCounts[dataCounts['count']>1100]['variable'])
comp1200 = list(dataCounts[dataCounts['count']>1200]['variable'])


print(len(comp1000), "comps above 1000;", numAllCol(data, comp1000), "docs with all") #5,359
print(len(comp1100), "comps above 1100;", numAllCol(data, comp1100), "docs with all") #5,359
print(len(comp1200), "comps above 1200;", numAllCol(data, comp1200), "docs with all") #5,359

data = data[comp1200]
num_null = list(data.apply(lambda x: x.isnull().sum(), axis='columns'))
data = data[[x==0 for x in num_null]]


#convert all ratings to scores
letter_score = {"a+": 4.3, "a":4, "a-":3.7, "b+":3.3,"b":3, "b-":2.7, "c+":2.3, "c":2, "c-":1.7}
def convert_rating(rating):
    return letter_score[rating]

for x in data.columns:
    if "comp_merged" not in x:
        continue
    data[x] = data[x].apply(convert_rating)


#apply LDA clustering
    
#convert the documents to id2word ie dictionary of id - competency mappings
curr_id = 0
id2word = {}
for x in data.columns:
    if "comp_merged" in x:
        id2word[curr_id] = x
        curr_id += 1
    
#convert the documents to corpus i.e. lists of [(comp_id, comp_score)...]
corpus = []
for i, row in data.iterrows():
    curr_corpus = []
    curr_total = 0
    for curr_id in id2word.keys():
        curr_comp = id2word[curr_id]
        curr_comp_score = row[curr_comp]
        curr_total += curr_comp_score
    for curr_id in id2word.keys():
        curr_comp = id2word[curr_id]
        curr_comp_score = row[curr_comp]
        curr_corpus.append((curr_id, curr_comp_score/curr_total))
    corpus.append(curr_corpus)



###############################################################################
#      Cluster via LDA
###############################################################################


def get_topTopics(model, corpus, id2word, coherence):
    tt = model.top_topics(corpus=corpus, dictionary=id2word, coherence=coherence)
    c_umass = [x[1] for x in tt] #grabs the c_v score for the cluster
    tt = [x[0] for x in tt] #grabs lists of coef-word for each topic
    tt = [[w[1] for w in x] for x in tt] #grabs word from coef-word
    tt = [", ".join(l) for l in tt]
    return tt, c_umass

def eval_model(model, corpus, df):
    outcomes = []
    for i in range(len(corpus)):
        topics_vec = model.get_document_topics(corpus[i], minimum_probability=0.0)
        topics_dict = {}
        for x in topics_vec:
            topics_dict['topic_' + str(x[0])] = x[1]
        topics_probs = [x[1] for x in topics_vec]
        topics_dict['doc_id_old'] = list(df['doc_id_old'])[i]
        topics_dict['doc_id_new'] = list(df['doc_id_new'])[i]
        topics_dict['max_prob'] = max(topics_probs)
        topics_dict['max_topic'] = topics_probs.index(max(topics_probs))
        outcomes.append(topics_dict)
    return pd.DataFrame(outcomes)

ntopics = []
models = []
coherences_umass = []
top_topics = []
file_name = "lda_rationale_filter5" 

for num_topics in range(2, 6):
    print("starting", num_topics, datetime.datetime.now().strftime('%H:%M:%S'))

    ntopics.append(num_topics)
    
    #run model
    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=20,
        random_state=100,
        alpha='auto',
        eta='auto',
        iterations=400,
        num_topics=num_topics,
        passes=80,
        eval_every=None, # Don't evaluate model perplexity, takes too much time.
        update_every=1
    )
    models.append(model)
    
    # Compute Coherence Score U_mass
    coherence_model = CoherenceModel(model=model, corpus=corpus, coherence='u_mass')
    coherence_umass = coherence_model.get_coherence()
    coherences_umass.append(coherence_umass)
    print('U_mass Score: ', coherence_umass)
    
    #print each topics top coefficients
    tt, c_umass = get_topTopics(model, corpus, id2word, 'u_mass')
    i=1
    for cluster in tt:
        top_topics.append({'num_clusters':num_topics, 'total_umass':coherence_umass, 'cluster':i,'cluster_umass':c_umass[i-1], 'words':cluster})
        i+=1
    del num_topics, model, coherence_model, coherence_umass, tt, c_umass, i

print("ended", datetime.datetime.now().strftime('%H:%M:%S'))
top_topics = pd.DataFrame(top_topics)


#plot coherence versus num_topics U_mass
plt.plot(ntopics, coherences_umass, linewidth=2)
plt.title("coherence scores per n.clusters")
plt.xlabel("number of clusters")
plt.ylabel("coherence score u_mass")
plt.show()


#create dataframe with description - cluster number ... only after we decided on a model!!!
with pd.ExcelWriter(path_out + "LDA_topics.xlsx") as writer:
    for selected_clusters in range(2, 6): #select the number of clusters we want
        model = models[ntopics.index(selected_clusters)] #grabs the model
        topic_coefficients = pd.DataFrame(model.get_topics(), columns=[id2word[x].replace("comp_merged_", "") for x in range(0, len(id2word))])
        topic_coefficients = topic_coefficients.T
        topic_coefficients.to_excel(writer, sheet_name=str(selected_clusters) + "clusters")


model = models[ntopics.index(4)] #grabs the model
df_outcomes = eval_model(model, corpus, data)
df_outcomes.to_excel(path_out + file_name + "_evalt" + str(selected_clusters) + ".xlsx", index=False)
del selected_clusters, model, temp



