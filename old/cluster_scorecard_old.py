# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:00:34 2020

@author: Asser.Maamoun
"""

import re
import random
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.metrics import confusion_matrix


import datetime
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

from gensim.models import Phrases
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim

#############################################################################
# create a sample of scorecard items to look at
#############################################################################

# load the data and subset the scorecard descriptions
df = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/allCleaned.xlsx")
mycols = ['doc_id'] + [x for x in df.columns if re.match("^sc_\\d{1,2}_desc$", x)]
df_scorecard = df[mycols]
del df, mycols

# give each description its own row
df_scorecard = pd.melt(frame=df_scorecard, id_vars=['doc_id'], var_name='number', value_name='desc')
df_scorecard['number'] = df_scorecard['number'].apply(lambda x: int(re.search('\\d+', x).group(0)))
df_scorecard = df_scorecard[pd.notnull(df_scorecard['desc'])]
df_scorecard = df_scorecard.sort_values(['doc_id', 'number'])

# take a random sample of 50 docs and indicate them in a new column
doc_ids = list(set(df_scorecard['doc_id']))
random.seed(1234)
sample_ids = sorted(random.sample(doc_ids, 50))
df_scorecard['sample'] = df_scorecard['doc_id'].apply(lambda x: int(x in sample_ids))
df_scorecard = df_scorecard[['doc_id', 'sample', 'number', 'desc']]
del sample_ids, doc_ids

#grab the first part of the scorecard item i.e. everything before first bullet
def grab_headline(text):
    find_headline = re.search(".*?<", text)
    if find_headline:
        text = text[:(find_headline.end()-1)]
    return text
df_scorecard['head'] = df_scorecard['desc'].apply(grab_headline)


# save
file_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/scorecard_notes.xlsx"
df_scorecard.to_excel(file_path, sheet_name= "sc_descriptions", index=False)
del file_path


###############################################################################
#      Manual Dictionaries
###############################################################################


#create an empty topic counts dict
def create_topic_dict():
    topic_counts = {}
    for x in topics:
        topic_counts[x] = 0
    return topic_counts

#function to assign topics
def assign_topic(text):
    text = text.replace(",","")
    text = text.replace("/"," ")
    topic_counts = create_topic_dict()
    for topic in keywords:
        for word in keywords[topic]:
            word_count = len(re.findall("\\b" + word + "\\b", text))
            topic_counts[topic] += word_count
    max_counts = max(topic_counts.values())
    if max_counts == 0:
        return 'none'
    elif topic_counts["exit"] > 0:
        return "exit"
    
    selected = []
    for topic in topic_counts:
        if topic_counts[topic] == max_counts:
            selected.append(topic)
    if "branding" in selected:
        return "branding"
    elif "deals" in selected:
        return "deals"
    elif "culture" in selected:
        return "culture"
    elif "staffing" in selected:
        return "staffing"
    elif "relations int" in selected:
        return "relations int"
    return ', '.join(selected)


#read in the edited notes files
df_notes = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/scorecard_notes_edited.xlsx")
# df_notes = df_notes[pd.notnull(df_notes['type1'])]
topics = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/scorecard_types.xlsx")
topics = list(topics.types)

#create dictionary of keywords
keywords = {}
for x in topics:
    keywords[x] = set()
del x

#topic counts in the sample
sample_counts = {}
for x in topics:
    sample_counts[x] = 0
del x

#add to the dictionary and topic counts
for index, row in df_notes.iterrows():
    typ = row['type1']
    words = row['key1']
    if pd.notnull(words):
        words=words.split(", ")
    else:
        continue
    sample_counts[typ] += 1
    for word in words:
        keywords[typ].add(word)
del typ, words, index, row, word

df_keywords = []
for x in keywords.keys():
    for i in keywords[x]:
        df_keywords.append({"key": x, "item": i})
df_keywords = pd.DataFrame(df_keywords)
del x, i

df_keywords.to_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/manual_keywords.xlsx")

df_keywords_primary = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/manual_keywords_edits.xlsx")
df_keywords_primary = df_keywords_primary[df_keywords_primary['primary']==1]
keywords_primary = {}
for x in topics:
    keywords_primary[x] = set()
del x
for index, row in df_keywords_primary.iterrows():
    typ = row['key']
    word = row['item']
    keywords_primary[typ].add(word)
del typ, index, row, word

def select_primary(r):
    if pd.isnull(r['key1']):
        return []
    else:
        words=r['key1'].split(", ")
        return ', '.join([x for x in words if x in keywords_primary[r['type1']]])
def select_secondary(r):
    if pd.isnull(r['key1']):
        return []
    else:
        words=r['key1'].split(", ")
        return ', '.join([x for x in words if x not in keywords_primary[r['type1']]])
df_notes['primary'] = df_notes.apply(select_primary, axis=1)
df_notes['secondary'] = df_notes.apply(select_secondary, axis=1)





#evaluate the sample
df_notes['topic'] = df_notes['head'].apply(assign_topic)
df_notes['topic_full'] = df_notes['desc'].apply(assign_topic)

df_notes['correct'] = [int(x) for x in df_notes['type1'] == df_notes['topic']]
df_notes['correct_full'] = [int(x) for x in df_notes['type1'] == df_notes['topic_full']]

df_notes['multiple'] = [int("," in x) for x in df_notes['topic']]
df_notes['multiple_full'] = [int("," in x) for x in df_notes['topic_full']]

print(sum(df_notes['correct'])/len(df_notes))
print(sum(df_notes['multiple'])/len(df_notes))
print(sum(df_notes['correct_full'])/len(df_notes))
print(sum(df_notes['multiple_full'])/len(df_notes))



#plot confusion
confusion = confusion_matrix(list(df_notes['type1']), list(df_notes['topic']), labels=topics)
confusion = pd.DataFrame(confusion, index = topics, columns = topics)
plt.figure(figsize=(10,7))
sn.set(font_scale=1.4)
sn.heatmap(confusion, annot=True)

###############################################################################
#      LDA PREP: Remove stopwords, Stem, Vectorize, and Bigrams
###############################################################################


#select the stopwords and stemmer to use
stopwords = nltk.corpus.stopwords.words('english')
stopadditions = ["name"]
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
        if (re.search('[a-zA-Z]', token)) and (token not in stopwords):
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

#create the vectorized articles
print("lemming w/o tfidf", datetime.datetime.now().strftime('%H:%M:%S'))
scorecard_bow, id2word, corpus = prep_data(list(df_scorecard['desc']))
headline_bow, id2wordH, corpusH = prep_data(list(df_scorecard['head']))
print("ended", datetime.datetime.now().strftime('%H:%M:%S'))


###############################################################################
#      Cluster via LDA
###############################################################################


def get_topTopics(model, corpus, bow, id2word, coherence):
    tt = model.top_topics(corpus=corpus, texts=bow, dictionary=id2word, coherence=coherence)
    c_vs = [x[1] for x in tt] #grabs the c_v score for the cluster
    tt = [x[0] for x in tt] #grabs lists of coef-word for each topic
    tt = [[w[1] for w in x] for x in tt] #grabs word from coef-word
    tt = [", ".join(l) for l in tt]
    return tt, c_vs

def eval_model(model, corpus, df):
    outcomes = []
    for i in range(len(corpus)):
        topics_vec = model.get_document_topics(corpus[i], minimum_probability=0.0)
        topics_dict = {}
        for x in topics_vec:
            topics_dict['topic_' + str(x[0])] = x[1]
        topics_probs = [x[1] for x in topics_vec]
        topics_dict['doc_id'] = list(df['doc_id'])[i]
        topics_dict['number'] = list(df['number'])[i]
        topics_dict['max_prob'] = max(topics_probs)
        topics_dict['max_topic'] = topics_probs.index(max(topics_probs))
        outcomes.append(topics_dict)
    return pd.DataFrame(outcomes)
    

###########
###########
    
corpus_selected = corpusH
bow_selected = headline_bow
id2word_selected = id2wordH
file_name = "lda_head"
    
ntopics = []
models = []
coherences = []
top_topics = []

for num_topics in range(5,25):
    print("starting", num_topics, datetime.datetime.now().strftime('%H:%M:%S'))

    ntopics.append(num_topics)
    
    #run model
    model = LdaModel(
        corpus=corpus_selected,
        id2word=id2word_selected,
        chunksize=100,
        random_state=100,
        alpha='auto',
        eta='auto',
        iterations=400,
        num_topics=num_topics,
        passes=20,
        eval_every=None, # Don't evaluate model perplexity, takes too much time.
        update_every=1
    )
    models.append(model)
    
    # Compute Coherence Score
    coherence_model = CoherenceModel(model=model, texts=bow_selected, dictionary=id2word_selected, coherence='c_v')
    coherence = coherence_model.get_coherence()
    coherences.append(coherence)
    print('Coherence Score: ', coherence)
    
    #print each topics top coefficients
    tt, c_vs = get_topTopics(model, corpus_selected, bow_selected, id2word_selected, 'c_v')
    i=1
    for cluster in tt:
        top_topics.append({'num_clusters':num_topics, 'total_cv':coherence, 'cluster':i,'cluster_cumass':c_vs[i-1], 'words':cluster})
        i+=1
    del num_topics, model, coherence_model, coherence,tt, c_vs, i

print("ended", datetime.datetime.now().strftime('%H:%M:%S'))
top_topics = pd.DataFrame(top_topics)
top_topics.to_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/clusters_" + name + "_topics.xlsx")

#plot coherence versus num_topics
plt.plot(ntopics, coherences, linewidth=2)
plt.title("coherence scores per n.clusters")
plt.xlabel("number of clusters")
plt.ylabel("coherence score c_v")
plt.show()


#create dataframe with description - cluster number
model = models[10] #grabs the model with 15 clusters
outcomes = eval_model(model, corpus_selected, df_scorecard)
scorecard_outcomes = pd.merge(df_scorecard, outcomes, how='left', on=['doc_id', 'number'])
scorecard_outcomes.to_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/scorecard/clusters_" + name + "_evaluated.xlsx")


# pyLDAvis.enable_notebook()
# vis = pyLDAvis.gensim.prepare(model, corpus, id2word)
# vis





