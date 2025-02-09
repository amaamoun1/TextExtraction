# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 17:52:45 2019

@author: amaamoun
"""

import re

def clean_key(key_entry, table_type, clean_obs):
    comp_set, info_set, _, bad_chars, space_chars = clean_obs
    
    #make lower case
    key_cleaned=key_entry.lower()
    #fix bad characters
    for b in bad_chars: key_cleaned = key_cleaned.replace(b, "")
    for s in space_chars: key_cleaned = key_cleaned.replace(s, " ")
    #take out unnecessary spaces
    key_cleaned=" ".join(key_cleaned.split())
    #check if we need to track the given key
    track_key=0
    if table_type=="info":
        if key_cleaned in info_set:
            track_key=1
    elif table_type=="competency":
        if key_cleaned in comp_set:
            track_key=1
    else:
        raise ValueError("Unaccounted table type in key cleaning: " + table_type)
    return (key_cleaned, track_key)

def clean_entry(var_entry, table_type):
    cleaned_entry=var_entry.lower()
    cleaned_entry=cleaned_entry.replace("tag end: ","")
    cleaned_entry=cleaned_entry.replace("tag start: ","")
    unclean_entry = 0
    rating=cleaned_entry
    #we only need to clean the competency ratings so that we exclude their comments
    if table_type=="competency":
        #find the rating (A/B/C) and its suffix (+/-) if a suffix exists
        find_rating = re.match("^(a|b|c){1}(\+|-)?(?:[^a-z].*)*$", cleaned_entry)
        if find_rating:
            rating=find_rating.group(1)
            suffix = find_rating.group(2)
            if suffix:
                rating= rating + suffix
            #double check for duplicate rating entries and print if they exist
            # find_2nd = re.match("(?:\.|\s)+(a|b|c){1}(\+|-)?(?:[^a-z].*)*$", cleaned_entry[len(rating):])
            # if find_2nd:
            #     rating2=find_2nd.group(1)
            #     suffix2 = find_2nd.group(2)
            #     if suffix2:
            #         rating2= rating2 + suffix2
            #     print("found 2nd", rating2, "in", var_entry)
        #keep track of those that are filled in
        elif ((re.match("^n/a(?:[^a-z].*)*$", cleaned_entry))!=None) | ("not observed" == cleaned_entry[:12]) | (re.match("^na(?:[^a-z].*)*$", cleaned_entry)!=None) | \
             ("not investigated" == cleaned_entry[:16]) |  ("insufficient data" == cleaned_entry[:17]):
            rating = "n/a"
        #keep track of no issues
        elif ("no issues" in cleaned_entry):
            rating = "no issues"
        elif ("*" in cleaned_entry):
            rating = "asterisk"
        #keep track of cases with too limited experience to rate
        elif re.match("^limited", cleaned_entry):
            rating = "limited experience"
        #remaining cases are tracked as unclean ratings
        else:
            unclean_entry = 1
        
    return (rating, unclean_entry)



