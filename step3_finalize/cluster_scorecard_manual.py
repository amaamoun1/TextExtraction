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
import pyLDAvis.gensim_models

out_clustering = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scorecard/clustering/"
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scorecard/"

#############################################################################
# create a sample of scorecard items to look at
#############################################################################

# load the data and subset the scorecard descriptions
df = pd.read_excel(out_local + "bigsample_scorecard_clean.xlsx")
mycols = ['doc_id'] + [x for x in df.columns if re.match("^\\d{1,2}_desc$", x)]
df_scorecard = df[mycols]
del df, mycols

# give each description its own row
df_scorecard = pd.melt(frame=df_scorecard, id_vars=['doc_id'], var_name='number', value_name='desc')
df_scorecard['number'] = df_scorecard['number'].apply(lambda x: int(re.search('\\d+', x).group(0)))
df_scorecard = df_scorecard[pd.notnull(df_scorecard['desc'])]
df_scorecard = df_scorecard.sort_values(['doc_id', 'number'])

#grab the first part of the scorecard item i.e. everything before first bullet
def grab_headline(text):
    find_headline = re.search("(.*?)<", text)
    if find_headline:
        if find_headline.end() == 1:
            find_headline = re.search("<(.*?)<", text)
            if find_headline:
                text = find_headline.group(1)
        else:
            text = find_headline.group(1)
    return text
df_scorecard['head'] = df_scorecard['desc'].apply(grab_headline)

###############################################################################
#      Create training and test sets
###############################################################################

# indicate the training set
doc_ids = list(set(df_scorecard['doc_id']))
random.seed(1234)
sample_ids = sorted(random.sample(doc_ids, 50))
sample_ids += sorted(random.sample([x for x in doc_ids if x not in sample_ids], 50))
df_scorecard['sample_train'] = df_scorecard['doc_id'].apply(lambda x: int(x in sample_ids))
df_scorecard = df_scorecard[['doc_id', 'sample_train', 'number', 'head', 'desc']]
del sample_ids, doc_ids

# indicate the validation set
doc_ids = list(set(df_scorecard['doc_id']))
random.seed(1235)
sample_ids = sorted(random.sample(doc_ids, 50))
df_scorecard['sample_test'] = df_scorecard['doc_id'].apply(lambda x: int(x in sample_ids))
df_scorecard = df_scorecard[['doc_id', 'sample_train', 'sample_test', 'number', 'head', 'desc']]
del sample_ids, doc_ids

# save
file_path = out_clustering + "scorecard_notes.xlsx"
df_scorecard.to_excel(file_path, sheet_name= "sc_descriptions", index=False)
del file_path

#read the past edits
df_notes = pd.read_excel(out_clustering + "scorecard_notes_edited.xlsx")
df_notes = df_notes[['doc_id', 'number', 'topic_true', 'keywords']]
df_notes = df_scorecard.merge(df_notes, how="left")
df_notes.to_excel(out_clustering + "scorecard_notes_edited.xlsx", index=False)


###############################################################################
#      Manual Dictionaries
###############################################################################


#read in the topics
df_notes = pd.read_excel(out_clustering + "scorecard_notes_edited.xlsx")
topics = pd.read_excel(out_clustering + "scorecard_types.xlsx")
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
    typ = row['topic_true']
    words = row['keywords']
    if pd.notnull(words):
        words=words.split(", ")
    else:
        continue
    sample_counts[typ] += 1
    for word in words:
        keywords[typ].add(word)
del typ, words, index, row, word


#create a dataframe of topic - keyword
df_keywords = []
for x in keywords.keys():
    for i in keywords[x]:
        df_keywords.append({"topic": x, "keyword": i})
df_keywords = pd.DataFrame(df_keywords)
df_keywords_past = pd.read_excel(out_clustering + "manual_keywords_edits.xlsx")
df_keywords = pd.merge(df_keywords, df_keywords_past, how='left', indicator=True)
df_keywords.to_excel(out_clustering + "manual_keywords.xlsx", index=False)
del x, i



####################################
# manually split keywords into primary and secondary dictionaries#
####################################

#could add extra words to stopwords
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

def select_primary(r):
    if pd.isnull(r['keywords']):
        return ""
    else:
        words=r['keywords'].split(", ")
        words=[lemmanize_keyword(x) for x in words]
        return ', '.join([x for x in words if x in keywords_primary[r['topic_true']]])
    
def select_secondary(r):
    if pd.isnull(r['keywords']):
        return ""
    else:
        words=r['keywords'].split(", ")
        words=[lemmanize_keyword(x) for x in words]
        return ', '.join([x for x in words if x in keywords_secondary[r['topic_true']]])


#load the manually categorized keywords
df_keywords = pd.read_excel(out_clustering + "manual_keywords_edits_strict1.xlsx")


#initiate keywords dictionaries to seperate the primary from secondary
keywords_primary = {}
keywords_secondary = {}
for x in topics:
    keywords_primary[x] = set()
    keywords_secondary[x] = set()
del x

#fill in the dictionaries
for index, row in df_keywords.iterrows():
    typ = row['topic']
    word = lemmanize_keyword(row['keyword'])
    if row['primary'] == 1:
        keywords_primary[typ].add(word)
    elif row['primary'] == 0:
        keywords_secondary[typ].add(word)
del typ, index, row, word


#create a datafreame of topic - joined keywords
df_keywordslist = []
for x in keywords.keys():
    df_keywordslist.append({"topic": x, "primary keys": ', '.join(keywords_primary[x]), "secondary keys": ', '.join(keywords_secondary[x])})
df_keywordslist = pd.DataFrame(df_keywordslist)
df_keywordslist.to_excel(out_clustering + "manual_keywordslist.xlsx", index=False)
del x


#create a primary keys and secondary keys column in the notes excel
df_notes['primary'] = df_notes.apply(select_primary, axis=1)
df_notes['secondary'] = df_notes.apply(select_secondary, axis=1)
df_notes.to_excel(out_clustering + "scorecard_notes_split.xlsx", index=False)




###############################################################################
#      Assign topics using the keyword dictionaries
###############################################################################

def print_both(string_var, *args):
    toprint = ''.join([str(arg) for arg in args])
    print(toprint)
    string_var.append(toprint + "\n")
    
    
def plot_confusion(df, title):
    confusion = confusion_matrix(list(df['topic_true']), list(df['topic_pred']), labels=topics) #true, pred
    confusion = pd.DataFrame(confusion, index = topics, columns = topics)
    
    sn.set(font_scale=1)
    plt.figure(figsize=(10,7))
    sn.heatmap(confusion, annot=True) #i is true, j is pred
    
    plt.title(title, fontsize = 20) # title with fontsize 20
    plt.xlabel('Predicted', fontsize = 15) # x-axis label with fontsize 15
    plt.ylabel('True', fontsize = 15) # y-axis label with fontsize 15
    plt.show()
    
#create an empty topic counts dict
def create_topic_counts():
    topic_counts = {}
    for x in topics:
        topic_counts[x] = 0
    return topic_counts

#function to assign topics
def assign_topic(text):
    #clean text
    text = str(text)
        
    #lemmanize text
    words=text.split(", ")
    lemmas=[lemmanize_keyword(x) for x in words]
    text = " ". join(lemmas)
    
    #find counts of primary and secondary keywords
    prim_counts = create_topic_counts()
    sec_counts = create_topic_counts()
    for topic in keywords_primary:
        for word in keywords_primary[topic]:
            word_count = len(re.findall("\\b" + word + "\\b", text))
            prim_counts[topic] += word_count
        for word in keywords_secondary[topic]:
            word_count = len(re.findall("\\b" + word + "\\b", text))
            sec_counts[topic] += word_count            
    
    #assign those topics with very specific language
    if prim_counts["exit"] > 0:
        return ("exit", "primary", prim_counts["exit"], sec_counts["exit"])
    else:
        #find the topic with maximum primary counts
        prim_max = max(prim_counts.values())
        
        prim_select = []
        for topic in prim_counts.keys():
            if prim_counts[topic] == prim_max:
                prim_select.append(topic)
        
        #if only one topic with max count, return it
        if len(prim_select)==1:
            return (prim_select[0], "primary", prim_max, sec_counts[prim_select[0]])
        else:
            #else tiebreak with secondary coutns
            sec_max = max(sec_counts.values())
            
            #if no secondary counts, return all primary maxes
            if sec_max == 0:
                if prim_max == 0:
                    return ("nf", "secondary", 0, 0)
                else:
                    return (', '.join(prim_select), "secondary", prim_max, 0)
            
            sec_select = []
            for topic in sec_counts:
                if sec_counts[topic] == sec_max:
                    sec_select.append(topic)
            #if only one sec_max return it, else return list of sec_maxs
            if len(sec_select)==1:
                return (sec_select[0], "secondary", prim_max, sec_max)    
            else:
                return (', '.join(prim_select), "secondary", prim_max, sec_max)

"""
#evaluate the sample
df_toeval = pd.read_excel(out_clustering + "scorecard_notes_edited.xlsx")
df_toeval = df_toeval[(df_toeval["sample_test"]==1) & (pd.notnull(df_toeval["topic_true"]))]
df_toeval = df_toeval.reset_index(drop=True)
df_eval = []
for i, row in df_toeval.iterrows():
    if i % 50 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['topic_pred'], row['eval_method'], row['prim_score'], row['sec_score'] = assign_topic(row['head'])
    df_eval.append(row)
del df_toeval
df_eval = pd.DataFrame(df_eval)

df_eval['correct'] = df_eval.apply(lambda row: int(row['topic_pred'] == row['topic_true']), axis=1)
df_eval['not found'] = df_eval.apply(lambda row: int(row["prim_score"]==0 and row["sec_score"]<=1), axis=1)
df_eval['multiple'] = df_eval.apply(lambda row: int("," in row["topic_pred"] and (row["sec_score"] > 1 or row['prim_score']>0)), axis=1)
df_eval['multiple_correct'] = df_eval.apply(lambda row: row['multiple'] * int(row['topic_true'] in row['topic_pred']), axis=1)



#subset various methods
df_evalmult = df_eval[df_eval['multiple']==1]
df_evalnf = df_eval[df_eval['not found'] ==1]
df_evalprim = df_eval[df_eval['eval_method']=='primary']
df_evalprimcut = df_evalprim[df_evalprim['prim_score']>=2]
df_evalprimnotcut = df_evalprim[df_evalprim['prim_score']<2]
df_evalsec = df_eval[(df_eval['eval_method']=='secondary') & (df_eval['multiple']==0) & (df_eval['not found']==0)]
df_evalseccut = df_evalsec[(df_evalsec['prim_score']>=1) | (df_evalsec['sec_score']>=3)]
df_evalsecnotcut = df_evalsec[(df_evalsec['prim_score']==0) & (df_evalsec['sec_score']<3)]

#histogram scores
plt.hist(list(df_evalprim['prim_score']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('Primary Score among Primary');
plt.show()

plt.hist(list(df_evalprim['sec_score']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('Secondary Score among Primary');
plt.show()

plt.hist(list(df_evalsec['prim_score']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('Primary Score among Secondary');
plt.show()

plt.hist(list(df_evalsec['sec_score']), density=False, align='left', bins=20)  # `density=False` would make counts
plt.ylabel('Counts')
plt.xlabel('Secondary Score among Secondary');
plt.show()




#print results
df_results = []
df_results.append({"type": "overall correct", 'percent':sum(df_eval['correct'])/len(df_eval)})
df_results.append({"type": "overall wrong", 'percent':1 - sum(df_eval['correct'])/len(df_eval) - sum(df_eval['multiple'])/len(df_eval) - sum(df_eval['not found'])/len(df_eval)})
df_results.append({"type": "overall not found", 'percent':len(df_evalnf)/len(df_eval)})
df_results.append({"type": "overall multiple", 'percent':len(df_evalmult)/len(df_eval)})
df_results.append({"type": "overall evaluated (correct + wrong)", 'percent':(len(df_eval) - len(df_evalnf) - len(df_evalmult))/len(df_eval)})
df_results.append({"type": "overall correct of evaluated", 'percent':sum(df_eval['correct']) / (len(df_eval) - sum(df_eval['multiple']) - sum(df_eval['not found']))})
df_results.append({"type": "primary method used" , 'percent':len(df_evalprim)/len(df_eval)})
df_results.append({"type": "primary correct", 'percent':sum(df_evalprim['correct'])/len(df_evalprim)})
df_results.append({"type": "primary method cut used" , 'percent':len(df_evalprimcut)/len(df_eval)})
df_results.append({"type": "primary cut correct", 'percent':sum(df_evalprimcut['correct'])/len(df_evalprimcut)})
df_results.append({"type": "primary method not cut used" , 'percent':len(df_evalprimnotcut)/len(df_eval)})
df_results.append({"type": "primary not cut correct", 'percent':sum(df_evalprimnotcut['correct'])/len(df_evalprimnotcut)})
df_results.append({"type": "secondary method used" , 'percent':len(df_evalsec)/len(df_eval)})
df_results.append({"type": "secondary correct", 'percent':sum(df_evalsec['correct'])/len(df_evalsec)})
df_results.append({"type": "secondary method cut used" , 'percent':len(df_evalseccut)/len(df_eval)})
df_results.append({"type": "secondary cut correct", 'percent':sum(df_evalseccut['correct'])/len(df_evalseccut)})
df_results.append({"type": "secondary method not cut used" , 'percent':len(df_evalsecnotcut)/len(df_eval)})
df_results.append({"type": "secondary not cut correct", 'percent':sum(df_evalsecnotcut['correct'])/len(df_evalsecnotcut)})
df_results.append({"type": "overall multiple contains correct", 'percent':sum(df_evalmult['multiple_correct'])/len(df_evalmult)})
df_results = pd.DataFrame(df_results)
print(df_results)
# print(df_evalprim['topic_true'].value_counts())
# print(df_evalsec['topic_true'].value_counts())


#plot confusion
plot_confusion(df_eval, "Confusion Matrix All")
plot_confusion(df_evalprim, "Confusion Matrix Primary")
plot_confusion(df_evalsec, "Confusion Matrix Secondary")

df_eval.to_excel(out_clustering + "scorecard_eval.xlsx", index=False)
df_results.to_excel(out_clustering + "scorecard_evalresults.xlsx", index=False)

###############################################################################
#      Final Assignment of topics
###############################################################################


# load the data and subset the scorecard descriptions
df = pd.read_excel(out_local + "bigsample_scorecard_clean.xlsx")
df.columns = ["doc_id"] + ["sc_" + x for x in df.columns if x !="doc_id"]
mycols = ['doc_id'] + [x for x in df.columns if re.match("^sc_\\d{1,2}_desc$", x)]
df_scorecard = df[mycols]
del df, mycols

# give each description its own row
df_scorecard = pd.melt(frame=df_scorecard, id_vars=['doc_id'], var_name='number', value_name='desc')
df_scorecard['number'] = df_scorecard['number'].apply(lambda x: int(re.search('\\d+', x).group(0)))
df_scorecard = df_scorecard[pd.notnull(df_scorecard['desc'])]
df_scorecard = df_scorecard.sort_values(['doc_id', 'number'])

#grab the first part of the scorecard item i.e. everything before first bullet
df_scorecard['head'] = df_scorecard['desc'].apply(grab_headline)
df_scorecard = df_scorecard.reset_index(drop=True)

#evaluate the final
df_finaleval = []
for i, row in df_scorecard.iterrows():
    if i % 1000 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['topic_pred'], row['eval_method'], row['prim_score'], row['sec_score'] = assign_topic(row['head'])
    df_finaleval.append(row)
del i, row
df_finaleval = pd.DataFrame(df_finaleval)
df_finaleval['not found'] = df_finaleval.apply(lambda row: int(row["prim_score"]==0 and row["sec_score"]<=1), axis=1)
df_finaleval['multiple'] = df_finaleval.apply(lambda row: int("," in row["topic_pred"] and (row["sec_score"] > 1 or row['prim_score']>0)), axis=1)

df_finaleval.to_excel(out_clustering + "scorecard_finaleval.xlsx", index=False)

"""

###############################################################################
#      Split growth into subcategories
###############################################################################

def split_growth(text):
    #clean text
    text = str(text)
    space_replace = ["(", ")", "/", "-"]
    drop = [",", "'"]
    for x in space_replace:
        text = text.replace(x," ")
    for x in drop:
        text = text.replace(x,"")
        
    #lemmanize text
    words=text.split(" ")
    lemmas=[lemmanize_keyword(x) for x in words]
    text = " ". join(lemmas)
    
    #counts
    count_sales = 0
    for word in lemmas_sales:
        count_sales += len(re.findall("\\b" + word + "\\b", text))
    count_cut = 0
    for word in lemmas_cut:
        count_cut += len(re.findall("\\b" + word + "\\b", text))
    
    #output
    if count_sales > 0 and count_cut > 0:
        return "both"
    elif count_sales > 0:
        return "revenue"
    elif count_cut > 0:
        return "ebitda"
    else:
        return "neither"
    
def split_growth_row(row):
    result = split_growth(row['head'])
    method = "headline"
    if result == "neither":
        result = split_growth(row['desc'])
        method = "desc"
        if result == "neither":
            result = "both"
    return result, method

def merge_into(v1, v2):
    if pd.notnull(v1):
        return v1
    else:
        return v2


#split up the growth category into growth_rev and growth_ebitda
df_finaleval = pd.read_excel(out_clustering + "scorecard_finaleval.xlsx")
df_growth = df_finaleval[df_finaleval['topic_pred']=="growth"][['doc_id', 'number', 'desc', 'head']]
df_keywordsgrowth = pd.read_excel(out_clustering + "manual_keywordslist_subtopics.xlsx")
df_keywordsgrowth = df_keywordsgrowth[df_keywordsgrowth['topic']=='growth']
sales_words = [x.split(', ') for x in list(df_keywordsgrowth[df_keywordsgrowth['subtopic']=='revenue']['subtopic keys'])][0]
lemmas_sales = [lemmanize_keyword(x) for x in sales_words]
cut_words = [x.split(', ') for x in list(df_keywordsgrowth[df_keywordsgrowth['subtopic']=='ebitda']['subtopic keys'])][0]
lemmas_cut = [lemmanize_keyword(x) for x in cut_words]
del sales_words, cut_words, df_keywordsgrowth 

"""
#evaluate method on a sample of 100
df_growth_sample = df_growth.sample(n=100, random_state=1)
df_growth_sample.to_excel(out_clustering + "growth_sample.xlsx", index=False)

df_growth_sample = pd.read_excel(out_clustering + "growth_sample_edited.xlsx")
df_growth_sample = df_growth_sample.reset_index(drop=True)
df_growth_sampleeval = []
for i, row in df_growth_sample.iterrows():
    if i % 50 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['pred'], row['eval_method'] = split_growth_row(row)
    df_growth_sampleeval.append(row)
del i, row, df_growth_sample
df_growth_sampleeval = pd.DataFrame(df_growth_sampleeval)
df_growth_sampleeval['correct'] = df_growth_sampleeval.apply(lambda row: int(row['pred'] == row['actual']), axis=1)
df_growth_sampleeval.to_excel(out_clustering + "growth_sampleeval.xlsx", index=False)


#evaluate on full df
df_growth = df_growth.reset_index(drop=True)
df_growth_eval = []
for i, row in df_growth.iterrows():
    if i % 500 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['pred'], row['eval_method'] = split_growth_row(row)
    df_growth_eval.append(row)
del i, row
df_growth_eval = pd.DataFrame(df_growth_eval)
df_growth_eval['pred'] = df_growth_eval['pred'].apply(lambda x: "growth_" + x)
df_growth_eval = df_growth_eval.drop(['eval_method'], axis = 1)

#back into finaleval
df_growth_eval = df_growth_eval.rename({'pred':'growth_pred'}, axis=1)
df_finaleval_growth = df_finaleval.merge(df_growth_eval, how='left', on = ['doc_id', 'number', 'desc', 'head'])
df_finaleval_growth['topic_pred'] = df_finaleval_growth.apply(lambda row: merge_into(row['growth_pred'], row['topic_pred']), axis=1)
df_finaleval_growth.drop(['growth_pred'], inplace=True, axis=1)

df_finaleval_growth.to_excel(out_clustering + "scorecard_finaleval_growth.xlsx", index=False)

"""
###############################################################################
#      Split relations into subcategories
###############################################################################

def split_relations(text):
    #clean text
    text = str(text)
    space_replace = ["(", ")", "/", "-"]
    drop = [",", "'"]
    for x in space_replace:
        text = text.replace(x," ")
    for x in drop:
        text = text.replace(x,"")
        
    #lemmanize text
    words=text.split(" ")
    lemmas=[lemmanize_keyword(x) for x in words]
    text = " ". join(lemmas)
    
    #counts
    count_board = 0
    for word in lemmas_board:
        count_board += len(re.findall("\\b" + word + "\\b", text))
    count_int = 0
    for word in lemmas_int:
        count_int += len(re.findall("\\b" + word + "\\b", text))
    count_ext = 0
    for word in lemmas_ext:
        count_ext += len(re.findall("\\b" + word + "\\b", text))
    
    #output
    found = ""
    if count_board > 0:
        found += "board"
    if count_int > 0:
        found += "int"
    if count_ext > 0:
        found += "ext"
    if found == "boardintext":
        found = "all"
    if found == "":
        found = "none"
    return found
    
def split_relations_row(row):
    result = split_relations(row['head'])
    method = "headline"
    if result == "none":
        result = split_relations(row['desc'])
        method = "desc"
        # if result == "none":
        #     result = "all"
    return result, method


#split up the growth category into growth_rev and growth_ebitda
df_finaleval = pd.read_excel(out_clustering + "scorecard_finaleval_growth.xlsx")
df_relations = df_finaleval[df_finaleval['topic_pred']=="relations"][['doc_id', 'number', 'desc', 'head']]
df_keywordsrelations = pd.read_excel(out_clustering + "manual_keywordslist_subtopics.xlsx")
df_keywordsrelations = df_keywordsrelations[df_keywordsrelations['topic']=='relations']
board_words = [x.split(', ') for x in list(df_keywordsrelations[df_keywordsrelations['subtopic']=='board']['subtopic keys'])][0]
lemmas_board = [lemmanize_keyword(x) for x in board_words]
int_words = [x.split(', ') for x in list(df_keywordsrelations[df_keywordsrelations['subtopic']=='int']['subtopic keys'])][0]
lemmas_int = [lemmanize_keyword(x) for x in int_words]
ext_words = [x.split(', ') for x in list(df_keywordsrelations[df_keywordsrelations['subtopic']=='ext']['subtopic keys'])][0]
lemmas_ext = [lemmanize_keyword(x) for x in ext_words]
del board_words, int_words, ext_words, df_keywordsrelations

"""
#evaluate method on a training sample of 100
df_relations_sample = df_relations.sample(n=100, random_state=1)
df_relations_sample.to_excel(out_clustering + "relations_sample.xlsx", index=False)

df_relations_sample = pd.read_excel(out_clustering + "relations_sample_edited.xlsx")
df_relations_sample = df_relations_sample.reset_index(drop=True)
df_relations_sampleeval = []
for i, row in df_relations_sample.iterrows():
    if i % 50 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['pred'], row['eval_method'] = split_relations_row(row)
    df_relations_sampleeval.append(row)
del i, row, df_relations_sample
df_relations_sampleeval = pd.DataFrame(df_relations_sampleeval)
df_relations_sampleeval['correct'] = df_relations_sampleeval.apply(lambda row: int(row['pred'] == row['actual']), axis=1)
df_relations_sampleeval.to_excel(out_clustering + "relations_sampleeval.xlsx", index=False)

#evaluate method on a test sample of 100
df_relations_sample = df_relations.sample(n=100, random_state=2)
df_relations_sample.to_excel(out_clustering + "relations_sample_test.xlsx", index=False)

df_relations_sample = pd.read_excel(out_clustering + "relations_sample_test_edited.xlsx")
df_relations_sample = df_relations_sample.reset_index(drop=True)
df_relations_sampleeval = []
for i, row in df_relations_sample.iterrows():
    if i % 50 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['pred'], row['eval_method'] = split_relations_row(row)
    df_relations_sampleeval.append(row)
del i, row, df_relations_sample
df_relations_sampleeval = pd.DataFrame(df_relations_sampleeval)
df_relations_sampleeval['correct'] = df_relations_sampleeval.apply(lambda row: int(row['pred'] == row['actual']), axis=1)
df_relations_sampleeval.to_excel(out_clustering + "relations_sample_testeval.xlsx", index=False)


#evaluate on full df
df_relations = df_relations.reset_index(drop=True)
df_relations_eval = []
for i, row in df_relations.iterrows():
    if i % 500 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['pred'], row['eval_method'] = split_relations_row(row)
    df_relations_eval.append(row)
del i, row
df_relations_eval = pd.DataFrame(df_relations_eval)
df_relations_eval['pred'] = df_relations_eval['pred'].apply(lambda x: "relations_" + x)
df_relations_eval = df_relations_eval.drop(['eval_method'], axis = 1)

#back into finaleval
df_relations_eval = df_relations_eval.rename({'pred':'relations_pred'}, axis=1)
df_finaleval_relations = df_finaleval.merge(df_relations_eval, how='left', on = ['doc_id', 'number', 'desc', 'head'])
df_finaleval_relations['topic_pred'] = df_finaleval_relations.apply(lambda row: merge_into(row['relations_pred'], row['topic_pred']), axis=1)
df_finaleval_relations.drop(['relations_pred'], inplace=True, axis=1)

df_finaleval_relations.to_excel(out_clustering + "scorecard_finaleval_growthrelations.xlsx", index=False)


###############################################################################
#      Save final counts
###############################################################################

#get counts per topic and merge to keywordslists
df_keywords_topic = pd.read_excel(out_clustering + "manual_keywordslist.xlsx")
df_keywords_subtopic = pd.read_excel(out_clustering + "manual_keywordslist_subtopics.xlsx")
df_finaleval = pd.read_excel(out_clustering + "scorecard_finaleval_growthrelations.xlsx")
df_topiccounts = df_finaleval[(df_finaleval['multiple']==0) & (df_finaleval['not found']==0)]
df_topiccounts = df_topiccounts[['topic_pred', 'doc_id']]
df_topiccounts = df_topiccounts.drop_duplicates()
df_topiccounts = df_topiccounts.groupby('topic_pred', as_index=False).count()
df_topiccounts.columns = ['topic', 'count']
df_topiccounts['subtopic'] = df_topiccounts['topic'].apply(lambda x: x.split("_")[-1])
df_topiccounts['topic'] = df_topiccounts['topic'].apply(lambda x: x.split("_")[0])
df_topiccounts = df_topiccounts.merge(df_keywords_topic, how='left')
df_topiccounts = df_topiccounts.merge(df_keywords_subtopic[['topic', 'subtopic','subtopic keys']], how='left', on = ['topic', 'subtopic'])
df_topiccounts = df_topiccounts[['topic', 'subtopic', 'count'] + list(df_topiccounts.columns[3:])]
df_topiccounts.to_excel(out_clustering + "scorecard_finalcleanCounts.xlsx", index=False)


#transform to wide format
df_finaleval_growth = pd.read_excel(out_clustering + "scorecard_finaleval_growthrelations.xlsx")
df_finalclean = df_finaleval_growth.copy()
df_finalclean = df_finalclean[(df_finalclean['multiple']==0) & (df_finalclean['not found']==0)]
df_finalclean = df_finalclean[['doc_id', 'number', 'topic_pred']]
df_finalclean['number'] = df_finalclean['number'].apply(lambda x: "sc_" + str(x) + "_topic")
df_finalclean = df_finalclean.pivot('doc_id','number','topic_pred')
df_finalclean= df_finalclean.reset_index()
df_finalclean.to_excel(out_clustering + "scorecard_finalclean.xlsx", index=False)


"""



