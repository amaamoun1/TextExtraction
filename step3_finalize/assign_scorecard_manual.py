# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 15:00:34 2020

@author: Asser.Maamoun
"""

import re
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.metrics import confusion_matrix

import datetime
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

out_clustering = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scorecard/clustering/"
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scorecard/"

#############################################################################
# load data and combine scorecard items
#############################################################################

# load the data and subset the scorecard descriptions
df = pd.read_excel(out_local + "bigsample_scorecard_clean.xlsx")
mycols = ['doc_id'] + [x for x in df.columns if re.match("^\\d{1,2}_desc$", x)]
df_scorecard = df[df['scorecard_present']==1][mycols]
del df, mycols

#combine scorecard items into one item
df_scorecard = df_scorecard.replace(np.nan, '', regex=True)
df_scorecard['full'] = df_scorecard['1_desc'] + " " + df_scorecard['2_desc'] + " " + df_scorecard['3_desc'] + " " + df_scorecard['4_desc'] + \
    " " + df_scorecard['5_desc'] + " " + df_scorecard['6_desc'] + " " + df_scorecard['7_desc'] + " " + df_scorecard['8_desc'] + \
    " " + df_scorecard['9_desc'] + " " + df_scorecard['10_desc'] + " " + df_scorecard['11_desc'] + " " + df_scorecard['12_desc'] + \
    " " + df_scorecard['13_desc'] + " " + df_scorecard['14_desc'] + " " + df_scorecard['15_desc'] + " " + df_scorecard['16_desc'] + \
    " " + df_scorecard['17_desc'] + " " + df_scorecard['18_desc'] + " " + df_scorecard['19_desc'] + " " + df_scorecard['20_desc'] 
df_scorecard = df_scorecard[['doc_id', 'full']]

###############################################################################
#      Create training and test sets
###############################################################################

# indicate the training set
doc_ids = list(set(df_scorecard['doc_id']))
random.seed(1234)
sample_ids = sorted(random.sample(doc_ids, 50))
df_scorecard['sample_train'] = df_scorecard['doc_id'].apply(lambda x: int(x in sample_ids))
df_scorecard = df_scorecard[['doc_id', 'sample_train', 'full']]
df_scorecard = df_scorecard.reset_index(drop=True)
del sample_ids, doc_ids


# save
file_path = out_clustering + "scorecard_full_notes.xlsx"
df_scorecard.to_excel(file_path, sheet_name= "sc_full", index=False)
del file_path

#read the past edits
df_notes = pd.read_excel(out_clustering + "scorecard_full_notes_edited.xlsx")
df_notes = df_notes[['doc_id', 'topic_true', 'tie']]
df_notes = df_scorecard.merge(df_notes, how="left")
df_notes.to_excel(out_clustering + "scorecard_full_notes_edited.xlsx", index=False)


###############################################################################
#      Manual Dictionaries
###############################################################################

#read in the subtopics dictionaries
df_subtopics = pd.read_excel(out_clustering + "manual_keywordslist_subtopics.xlsx")
df_subtopics = df_subtopics[df_subtopics['topic']=='growth']
dict_subtopics = df_subtopics.set_index('subtopic')['subtopic keys'].to_dict()

#read in the topic dictionaries
df_topics = pd.read_excel(out_clustering + "manual_keywordslist.xlsx")
df_topics['all_keys'] = df_topics['primary keys'] + df_topics['secondary keys']
dict_topics = df_topics.set_index('topic')['all_keys'].to_dict()

#create a list of revenue and cost words
words_rev = dict_subtopics['revenue'] + dict_topics['expansion'] + dict_topics['branding'] + dict_topics['innovate'] + dict_topics['deals']
words_rev = list(set(words_rev.split(", ")))
words_cost = dict_subtopics['ebitda'] + dict_topics['operations']
words_cost = list(set(words_cost.split(", ")))

topics = ['revenue', 'cost', 'none', 'tie']

###############################################################################
#      Assign topics using the keyword dictionaries
###############################################################################

def print_both(string_var, *args):
    toprint = ''.join([str(arg) for arg in args])
    print(toprint)
    string_var.append(toprint + "\n")

def plot_confusion(df, title):
    confusion = confusion_matrix(list(df['topic_true']), list(df['topic_pred']), labels=topics) #true, pred
    confusion = pd.DataFrame(confusion, index=topics, columns=topics)
    
    sn.set(font_scale=1)
    plt.figure(figsize=(10,7))
    sn.heatmap(confusion, annot=True) #i is true, j is pred
    
    plt.title(title, fontsize = 20) # title with fontsize 20
    plt.xlabel('Predicted', fontsize = 15) # x-axis label with fontsize 15
    plt.ylabel('True', fontsize = 15) # y-axis label with fontsize 15
    plt.show()
    
#lemmanize functions
lemmatizer = WordNetLemmatizer()
stopwords = ["and"]

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
    
def lemmanize_keyword(text):
    space_replace = ["(", ")", "/"]
    drop = [",", "'"]
    for x in space_replace:
        text = text.replace(x," ")
    for x in drop:
        text = text.replace(x,"")
    tokens = [word.lower() for word in nltk.word_tokenize(text)]
    lemmas = []
    for word, pos in nltk.pos_tag(tokens):
        if word in stopwords:
            continue
        result_pos=wordnet_pos(pos)
        if result_pos != None:
            lemmas.append(lemmatizer.lemmatize(word, result_pos))
        else:
            lemmas.append(word)
    return " ".join(lemmas)

#function to assign topics
def assign_topic(text):
    #clean text
    text = str(text)
        
    #lemmanize text
    words=text.split(", ")
    lemmas=[lemmanize_keyword(x) for x in words]
    text = " ". join(lemmas)
    num_words = len(text.split(" "))
    
    #find counts of primary and secondary keywords
    count_rev = 0
    count_cost = 0
    for word in words_rev:
        word_count = len(re.findall("\\b" + word + "\\b", text))
        count_rev += word_count
    for word in words_cost:
        word_count = len(re.findall("\\b" + word + "\\b", text))
        count_cost += word_count            
    
    if count_rev>count_cost:
        outcome = "revenue"
    elif count_rev<count_cost:
        outcome = "cost"
    elif count_rev==0:
        outcome = "none"
    else:
        outcome = "tie"
    
    return num_words, count_rev/num_words, count_cost/num_words, (count_rev-count_cost)/num_words, outcome

"""

#evaluate the sample
df_toeval = pd.read_excel(out_clustering + "scorecard_full_notes_edited.xlsx")
df_toeval = df_toeval[(df_toeval["sample_train"]==1) & (pd.notnull(df_toeval["topic_true"]))]
df_toeval = df_toeval.reset_index(drop=True)
df_eval = []
for i, row in df_toeval.iterrows():
    if i % 50 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['total_words'], row['score_rev'], row['score_cost'], row['score_diff'], row['topic_pred'] = assign_topic(row['full'])
    df_eval.append(row)
print(i, datetime.datetime.now().strftime('%H:%M:%S'))
del i, row, df_toeval
df_eval = pd.DataFrame(df_eval)
df_eval['correct'] = df_eval.apply(lambda row: int(row['topic_pred'] == row['topic_true']), axis=1)
df_eval['not found'] = df_eval.apply(lambda row: int(row["score_rev"]==0 and row["topic_pred"]==1), axis=1)


#subset various methods
df_evaltie = df_eval[df_eval['topic_pred']=='tie']
df_evalnone = df_eval[df_eval['topic_pred']=='none']

#histogram scores
plt.hist(list(df_eval['score_rev']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('score revenue');
plt.show()

plt.hist(list(df_eval['score_cost']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('score cost');
plt.show()

plt.hist(list(df_evaltie['score_rev']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('score tie');
plt.show()



#print results
df_results = []
df_results.append({"type": "overall correct", 'percent':sum(df_eval['correct'])/len(df_eval)})
df_results.append({"type": "overall none", 'percent': len(df_evalnone)/len(df_eval) })
df_results.append({"type": "overall tie", 'percent':len(df_evaltie)/len(df_eval)})
df_results.append({"type": "overall evaluated (correct + wrong)", 'percent':(len(df_eval) - len(df_evaltie)) /len(df_eval)})
df_results.append({"type": "overall correct of evaluated", 'percent':sum(df_eval['correct']) / (len(df_eval) - len(df_evaltie))})
df_results = pd.DataFrame(df_results)
print(df_results)

#plot confusion
plot_confusion(df_eval, "Confusion Matrix All")

df_eval.to_excel(out_clustering + "scorecard_full_eval.xlsx", index=False)
df_results.to_excel(out_clustering + "scorecard_full_evalresults.xlsx", index=False)

###############################################################################
#      Final Assignment of topics
###############################################################################


#evaluate the final
df_finaleval = []
for i, row in df_scorecard.iterrows():
    if i % 1000 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['total_words'], row['score_revenue'], row['score_cost'], row['score_diff'], row['outcome'] = assign_topic(row['full'])
    df_finaleval.append(row)
print(i, datetime.datetime.now().strftime('%H:%M:%S'))
del i, row
df_finaleval = pd.DataFrame(df_finaleval)
df_finaleval.to_excel(out_clustering + "scorecard_full_finaleval.xlsx", index=False)

"""

