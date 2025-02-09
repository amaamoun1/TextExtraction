# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 19:54:21 2020

@author: Asser.Maamoun
"""

import pandas as pd
import re



def isolate_scorecard(text):
    match = None
    attempt = 0
    while (match==None) and (attempt<5):
        if attempt==0:
            match1 = re.search("\\bkey outcomes\\b", text)
            match2 = re.search("\\bkey accountabilities\\b", text)
            if match1 and match2:
                if match1.start() < match2.start():
                    match = match1
                else:
                    match = match2
            elif match1:
                match = match1
            else:
                match = match2
        elif attempt==1:
            match = re.search("\\bscorecard\\b", text)
        elif attempt==2:
            match1 = re.search("\\boutcomes\\b", text)
            match2 = re.search("\\baccountabilities\\b", text)
            if match1 and match2:
                if match1.start() < match2.start():
                    match = match1
                else:
                    match = match2
            elif match1:
                match = match1
            else:
                match = match2
        attempt+=1
    if match:
        start = match.start()
        isolated = text[start:]
    else:
        isolated = text
    return isolated


def clean_scorecard(text):
    #first, check for new page and if the new page starts with a line followed by a line only contaning the date, delete those first two lines as well becasue they are footers
    cleaned = re.sub("\\n(?:(?:\\s*NEW PAGE\\s*\\n+)(?:[^\\n]*\n+[^\\n\\S]*\w{3,9}\s*\\d{1,2},\\s*\\d{4}\\s*smart\\s*assessment\\s*\\n)*)*", "\n", text)
    cleaned = re.sub("\\n{2,}", "\n", cleaned)
    cleaned = re.sub("\\n\\s*page\\s*\\d*\\s*\\n", "\n", cleaned)
    cleaned = re.sub("\\n\\s*(?:page)?\\s*\\d{1,2}\\s*of\\s*\\d{1,2}\\s*\\n", "\n", cleaned)
    cleaned = re.sub("\\n\\s*\\d+\\s*\\n", "\\n", cleaned)
    return cleaned


def identify_line(line, header_words, curr):
    #a new outcome is identified by the "1 ..." or "2 ..." at the beginning of line
    #if the last outcome was 1 then we search for either 1a, 1b, 1c, or 2
    if re.search("^\\s*1a?[\\)\\.]?\\s", line):
        if curr==0:
            return ("first", 1)
        else:
            return ("drop", 0)
    to_search = re.compile("^\\s*(" + str(curr) + "|" + str(curr+1) + ")[abcd]?[\\)\\.]?\\s")
    m = re.search(to_search, line)
    if m:
        return ("new", int(m.group(1)))
    words = set(line.split())
    if len(words) < 8:
        num_header = 0
        for word in header_words:
            if word in words:
                num_header+=1
                if num_header >= 3:
                    return ("header", curr)
        if num_header == len(words):
            return ("header", curr)
    return ("middle", curr)

def group_lines(text, header_words):
    lines = text.split("\n")
    group = []
    groups = []
    curr = 0
    for line in lines:
        ltype, new_curr = identify_line(line, header_words, curr)
        #only start grouping lines once we see the first outcome
        if (curr==0) and (ltype!="first"): #catches all but the first line
            continue
        elif (curr==0) and (ltype=="first"): #create the first group
            curr = 1
            group = [line]
        elif ltype=="new": #append the last group and create a new group
            curr = new_curr
            groups.append(group)
            group = [line]
        elif ltype=="middle": #append middle lines
            group.append(line)
        elif ltype=="drop": #if a new numbering starts with 1, we stop looking
            break
    if len(group)>0: #we append the last group
        groups.append(group) 
    return groups

def split_line(line, lnum):
    #first isolate the outcome number if this is a new outcome
    if lnum == 0:
        match = re.search("^\\s*(\\d{1,2}[abc]?)[\\)\\.]?(.*)", line, flags=re.DOTALL)
        number = match.group(1)
        line = match.group(2)
    else:
        number = ""
    #if we only have a rating, i.e. if line starts with 40+ spaces
    if re.search("^\\s{40,}", line):
        desc = ""
        rating = line.strip()
    else:
        line = line.strip()
        splits = re.split("\\s{2,}", line)
        #rating will be the last split entry, unless we only have one split
        if len(splits) == 1:
            desc = splits[0]
            rating = ""
        else:
            desc = " ".join(splits[:-1])
            rating = splits[-1]
    return number, desc, rating

def split_combine_group(group):
    number = ""
    desc = ""
    rating = ""
    lnum = 0
    for line in group:
        n, d, r = split_line(line, lnum)
        number += n + " "
        desc += d + " "
        rating += r + " "
        lnum+=1
    number = number.strip()
    desc = desc.strip()
    rating = rating.strip()
    return [number, desc, rating]


        


header_words = ["outcomes", "accountabilities", "key", "rating",
                "comments", "grade", "#"]

# isolated_texts = []
# cleaned_texts = []
# grouped_texts = []
# combined_groups = []
# dicts = []
# for text in master_scorecardText:
#     isolated = isolate_scorecard(text)
#     isolated_texts.append(isolated)
#     cleaned = clean_scorecard(isolated)
#     cleaned_texts.append(cleaned)
#     grouped = group_lines(cleaned, header_words)
#     grouped_texts.append(grouped)
#     combined = [split_combine_group(x) for x in grouped]
#     combined_groups.append(combined)
#     scorecard_dict = {}
#     for group in combined:
#         desc_name = group[0] + "_desc"
#         rat_name = group[0] + "_rating"
#         scorecard_dict[desc_name] = group[1]
#         scorecard_dict[rat_name] = group[2]
#     dicts.append(scorecard_dict)
    
def parse_scorecardText(text):
    #create the groupings by outcome
    isolated = isolate_scorecard(text)
    cleaned = clean_scorecard(isolated)
    if cleaned == "":
        return {}
    grouped = group_lines(cleaned, header_words)
    combined = [split_combine_group(x) for x in grouped]
    #store the outcomes in dictionary
    scorecard_dict = {}
    group_num = 1
    for group in combined:
        desc_name = str(group_num) + "_desc"
        rat_name = str(group_num) + "_rating"
        scorecard_dict[desc_name] = group[1]
        scorecard_dict[rat_name] = group[2]
        group_num += 1
    return scorecard_dict


