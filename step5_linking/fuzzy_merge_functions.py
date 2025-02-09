# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import re
import pandas as pd
import numpy as np
from pyjarowinkler import distance
from datetime import datetime
from pytz import timezone

suffixes = ['ag', 'co', 'company', 
            'corporation', 'corp', 'inc',
            'gp', 'grp', 'group',
            'holding', 'holdings',
            'international', 'intl', 
            'lc', 'llc', 'llp', 'lp',  
            'ltd', 'lte', 'limited', 'incorporated', 'pllc', 'plc', 'mfg', 'pc', 'pa']

stopwords = ["previously", "formerly", "known as", "acquired", "portfolio company", 
             'an', 'and', 'of', 'the', 'at', 'in', 'on', 'a', 'by', 'as']
             
def clean_company(c):
    #clean punctuations
    if pd.isnull(c):
        return ''
    c = c.lower()
    c = re.sub("[\\-\\/\\|\\,]", " ", c)
    c = re.sub("[^a-z\\s\\d]", "", c)
    
    #clean stopwords
    for x in stopwords:
        c = re.sub("\\b" + x + "\\b", "", c)
    
    #clean suffixes
    for x in suffixes:
        c = re.sub("\\b" + x + "\\b", "", c)
    
    #make all whitespace just a single space
    c = c.strip()
    c = re.sub("\\s+", " ", c)
    
    #the following loop combines adjacent letters, i.e. "t j max" becomes "tj max" and "t j max u s a" becomes "tj max usa"
    letters = re.search("\\b((?:\\S{1}\\s)+(?:\\S))\\b", c)
    while (pd.notnull(letters)):
        letters = letters[0]
        replacement = re.sub(" ", "", letters)
        c = re.sub("\\b" + letters + "\\b", replacement, c)
        letters = re.search("\\b((?:\\S{1}\\s)+(?:\\S))\\b", c)
    return c


test = clean_company("hello'there t j max inc  ")



def company_simularity(in_name, check_name):
  #checks if either name is NaN
  if (pd.isnull(in_name) | pd.isnull(check_name)):
    return 0

  #splits names into seperate words
  in_words = in_name.split()
  check_words = check_name.split()
  
  #check the number of words that are the same in both names
  num_words = len(in_words)
  num_matched = 0
  start_matched = 0
  i = 0
  for w in in_words:
    if w in check_words:
      #start keeps track of the number of consecutive matching words at the beginning of the name
      if (start_matched==i and len(check_words)>=i and in_words[i] == check_words[i]): #indicates that we have seen start consecutive word matches
        start_matched +=1
      num_matched += 1 #num keeps track of the total number of word matches
    i += 1
    
    start_perc = round(start_matched/num_words,2)*100
    total_perc = round(num_matched/num_words,2)*100
    
    #get jaro-winkler distance
    jarowink = distance.get_jaro_distance(in_name, check_name, winkler=True, scaling=0.1)
    jarowink = round(jarowink,3) *1000
  
  return (start_perc, total_perc, jarowink)




def fuzzy_merge_keepbest(input_names, check_names, num_keep=10, threshold=0.75):  
    #all_list tracks all matches
    all_dicts = [np.nan] * len(input_names) *num_keep
    
    i = 0
    for in_name in input_names:
        #keep track of time
        if i==0 or i % 100 == 0:
            chi_time = datetime.now(timezone('America/Chicago'))
            print(i, "parsing at", chi_time.strftime('%H:%M:%S'))
        #initialize vectors
        curr_matches = [np.nan] * num_keep
        curr_scores = [np.nan] * num_keep
        j = 0
        #check every possible name
        for check_name in check_names:
            #find the current similiarity
            if check_name == "":
                continue
            
            #create the min scores and index if we have the num_keep
            if j == num_keep:
                min_score = min(curr_scores)
                min_index = curr_scores.index(min_score)
            
            start_perc, total_perc, jarowink = company_simularity(in_name, check_name)
            if jarowink < threshold:
                continue
            curr_score = (start_perc*10000000 + total_perc * 10000 + jarowink)
            
            #the first num_keep strings are entered into the list
            if j<num_keep:
                curr_matches[j] = check_name
                curr_scores[j] = curr_score
            
            #if a higher score has been found than the list's mininum, replace the minimum
            elif curr_score > min_score:
                #replace the minimum values
                curr_scores[min_index] = curr_score
                curr_matches[min_index] = check_name
                
                #update the minimum values
                min_score = min(curr_scores)
                min_index = curr_scores.index(min_score)
            j += 1
        
        #sort the results for the current matches
        sorted_indexes = sorted(range(num_keep), key=lambda k: curr_scores[k], reverse=True)
        sorted_scores = [curr_scores[x] for x in sorted_indexes]
        sorted_matches = [curr_matches[x] for x in sorted_indexes]
        
        #combine into one vector and add to all_list
        rank = 0
        for x in range(len(sorted_matches)):
            full_dict = {}
            full_dict['input_name'] = in_name
            full_dict['match_name'] = sorted_matches[x]
            full_dict['match_rank'] = rank
            full_dict['match_score'] = sorted_scores[x]
            all_dicts[(i*num_keep)+rank] = full_dict
            rank += 1
        i +=1
  
    all_df  = pd.DataFrame(all_dicts)
      
    return all_df


def fuzzy_merge_keepthreshold(input_names, check_names):  
    #all_list tracks all matches
    all_dicts = []
    i = 0
    for in_name in input_names:
        #keep track of time
        if i==0 or i % 100 == 0:
            chi_time = datetime.now(timezone('America/Chicago'))
            print(i, "parsing at", chi_time.strftime('%H:%M:%S'))
        #initialize vectors
        curr_matches = []
        curr_scores = []
        
        #check every possible name
        for check_name in check_names:
            #skip nulls
            if check_name == "":
                continue
            
            #find the current similiarity
            start_perc, total_perc, jarowink = company_simularity(in_name, check_name)
            curr_score = (start_perc*10000000 + total_perc * 10000 + jarowink)
            
            #only keep useful info
            if jarowink>0.8:
                curr_matches.append(check_name)
                curr_scores.append(curr_score)
        
        #sort the results for the current matches
        sorted_indexes = sorted(range(len(curr_scores)), key=lambda k: curr_scores[k], reverse=True)
        sorted_scores = [curr_scores[x] for x in sorted_indexes]
        sorted_matches = [curr_matches[x] for x in sorted_indexes]
        
        #combine into one vector and add to all_list
        rank = 0
        for x in range(len(sorted_matches)):
            full_dict = {}
            full_dict['input_name'] = in_name
            full_dict['match_name'] = sorted_matches[x]
            full_dict['match_rank'] = rank
            full_dict['match_score'] = sorted_scores[x]
            all_dicts.append(full_dict)
            rank += 1
        i +=1
  
    all_df  = pd.DataFrame(all_dicts)
      
    return all_df


 

