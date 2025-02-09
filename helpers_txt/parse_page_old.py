# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 22:21:12 2020

@author: Asser.Maamoun
"""

import pandas as pd
import numpy as np
import re

def addSpaces(text):
    new = "\s" + text[0]
    for letter in text[1:]:
        if letter==" ":
            continue
        elif letter in ["(", ")"]:
            letter = "\\" + letter
        new += "[\s\-]*" + letter  #allow for accidental whitespace and new lines
    return new

def identifyPage(page, last_page):
    if re.search(addSpaces("\n\ncontents\n\n"), page) or re.search(addSpaces("disclaimer and confidentiality policy"), page):
        return "other"
    if re.search(addSpaces("competency scorecard"), page):
        return "competency"
    elif re.search(addSpaces("competencies"), page):
        if re.search(addSpaces("ratings and comments"), page) or \
            re.search(addSpaces("removes underperformers"), page) or \
            re.search(addSpaces("personal effectiveness"), page):
                return "competency"
    elif (re.search(addSpaces("scorecard"), page)) or (re.search(addSpaces("outcomes"), page)):
        if (re.search(addSpaces("rating"), page)) or (re.search(addSpaces("grade"), page)):
            return "scorecard"
    elif re.search(addSpaces("your questions"), page):
        return "questions"
    #keep identifying as scorecard until the next section is found
    if last_page=="scorecard":
        return"scorecard"
    return "other"

def extractCompetencies(page, clean_obs):
    comp_set, info_set, _, bad_chars, space_chars, _ = clean_obs
    competencies = {}
    unclean = {}

    #fix bad characters
    for b in bad_chars: page = page.replace(b, "")
    for s in space_chars: page = page.replace(s, " ")
    #take out unnecessary spaces
    #page=" ".join(page.split())

    #extract the competencies
    for competency in comp_set:
        #if competency is not found rating will be nan
        rating = np.nan
        comp_reg = addSpaces(competency)  #allow for accidental whitespace and new lines
        #find_competency = re.search("\s" + comp_reg + "\s", page)
        find_competency = re.search(comp_reg, page)
        if find_competency:
            #if competency is found, but it was not rated, then return NF
            entry = page[(find_competency.end()):(find_competency.end()+50)]
            current_line = page
            find_rating = re.match("^\s*(a|b|c){1}\s*(\+|-)?(?:[^a-z].*)*$", entry, flags=re.DOTALL)
            if find_rating:
                rating=find_rating.group(1)
                suffix = find_rating.group(2)
                if suffix:
                    rating= rating + suffix
            #keep track of those that are filled in
            elif ((re.match("^n/a(?:[^a-z].*)*$", entry))!=None) | ("not observed" == entry[:12]) | (re.match("^na(?:[^a-z].*)*$", entry)!=None) | \
                 ("not investigated" == entry[:16]) |  ("insufficient data" == entry[:17]) | ("n a " == entry[:4]):
                rating = "na"
            #keep track of no issues
            elif ("no issues" in entry[:9]):
                rating = "no issues"
            elif ("*" in entry):
                rating = "asterisk"
            #keep track of cases with too limited experience to rate
            elif re.match("^limited", entry):
                rating = "limited"
            else:
                if entry in unclean:
                    unclean[entry] += 1
                else:
                    unclean[entry] = 1
        competencies[competency] = rating            
    return competencies, unclean
        

def extractOutcomes(page, clean_obs):
    _, _, _, _, space_chars, bad_chars = clean_obs
    outcomes = {}
    #add new lines at end of page for easier id
    page += "\n\n\n"

    #fix bad characters
    for b in bad_chars: page = page.replace(b, "")
    for s in space_chars: page = page.replace(s, " ")
    
    #cut everything out before this sections (sometimes mission and scorecard are on the same page)
    section_start = re.search("(" + addSpaces("scorecard") + ")?", page)
    if not section_start:
        section_start = re.search("(" + addSpaces("outcomes") + ")?", page)
    if section_start:
        page = page[section_start.start():]
    #split the page by outcome number
    outcomes = {}
    ranks = re.findall("\n\n(\d{1,2})\.\n\n", page)
    if ranks:
        ranks = [int(x) for x in ranks]
        splits = re.split("\n\n\d{1,2}\.\n\n", page)[1:]
#        print(splits)
        results = []
        for split in splits:
            split = "\n\n" + split + "\n\n" #add back the new lines for demarcation of paragraphs
            outcome = np.nan
            find_outcome = re.search("^\n*(.*?)\n\n\n", split, re.DOTALL)
            if find_outcome:
                outcome = find_outcome.group(1)    
            rating = np.nan
            find_rating = re.search("\n\n+(a|b|c){1}[\n\s]*(\+|-)?(?:[^a-z].*)*$", split, re.DOTALL)
            if find_rating:
                rating=find_rating.group(1)
                suffix = find_rating.group(2)
                if suffix:
                    rating= rating + suffix
            results.append((outcome, rating))
        outcomes = dict(zip(ranks, results))
    return outcomes
        