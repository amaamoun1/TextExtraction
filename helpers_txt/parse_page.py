# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 22:21:12 2020

@author: Asser.Maamoun
"""

import pandas as pd
import numpy as np
import re

def addSpaces(text):
    # new = "\W+" + text[0] #nonword must precede first letter
    new = "\\b" + text[0]
    for letter in text[1:]:
        if letter==" ":
            continue
        elif letter in ["(", ")"]:
            letter = "\\" + letter
        new += "[\\s\\-]*" + letter  #allow for accidental whitespace or dashes
    new += "\\b" #word boundary must follow last letter
    return new

def makeReg(text):
    new = ""
    for letter in text:
        if letter in ["(", ")"]:
            letter = "\\" + letter
        new += letter
    return new

def identifyPage(page, already_seen):
    if re.search("^\\s*.*smartassessment", page):
        return "info"
    if re.search(addSpaces("prepared for"), page) and \
        re.search(addSpaces("prepared by"), page) and \
        re.search(addSpaces("purpose of this"), page):
        if "info" not in already_seen:
            return "info"
    if re.search(addSpaces("rating definitions"), page):
        if "rating definitions" not in already_seen:
            return "rating definitions"
    if re.search("\\.{10,}", page):
        return "contents"
    if re.search(addSpaces("executive summary"), page) or \
        re.search(addSpaces("what do you need to be aware of?"), page):
        if "summary" not in already_seen:
            return "summary"
    if re.search(addSpaces("\\n\\ncontents\\n\\n"), page) or re.search(addSpaces("disclaimer and confidentiality policy"), page):
        if "disclaimer or contents" not in already_seen:
            return "disclaimer or contents"
    if re.search(addSpaces("key strengths and risk areas"),page) or \
        (re.search(addSpaces("key strengths"), page) and \
        (re.search(addSpaces("biggest risk areas"),page) or re.search(addSpaces("development areas"),page))) or \
        re.search(addSpaces("strengths and development areas"), page):
        if "strengths and weaknesses" not in already_seen:
            return "strengths and weaknesses"
    if re.search("^\\s*.*recommendations", page):
        if ("recommendations" not in already_seen):
            return "recommendations"
    #if re.search(addSpaces("scorecard"), page) or re.search(addSpaces("outcomes"), page) or re.search(addSpaces("accountabilities"), page):
    if re.search("^\\s*.*scorecard", page) or re.search("^\\s*.*\\bmission", page) or re.search("^\\s*.*key outcomes", page) or re.search("^\\s*.*key accountabilities", page):
        if not re.search("^\\s*.*competency", page):
            return "scorecard"
    if re.search(addSpaces("key outcomes"), page) or re.search(addSpaces("key accountabilities"), page):
        if ("scorecard" not in already_seen) and \
            (re.search(addSpaces("rating"), page) or \
             re.search(addSpaces("ranking"), page) or \
             re.search(addSpaces("grade"), page) or \
             re.search(addSpaces("comments"), page)):
            # (re.search("\n\s*1a?[\)\.]?\s", page) and re.search("\s{2}[abc][\-\+]?\.?\s{2}", page))):
            # (re.search("\n\s*1a?\.?\s", page)):
            return "scorecard"
    if re.search("^\\s*.*competency", page) or re.search("^\\s*.*competencies", page):
        return "competency"
    # if re.search(addSpaces("competency scorecard"), page):
    #     if "competency" not in already_seen:
    #         return "competency"
    if re.search(addSpaces("competencies"), page) or re.search(addSpaces("competency"), page):
        if re.search(addSpaces("ratings and comments"), page) or \
            re.search(addSpaces("rating and comments"), page) or \
            re.search(addSpaces("experience comments"), page) or \
            re.search(addSpaces("grade"), page) or \
            re.search(addSpaces("removes underperformers"), page) or \
            re.search(addSpaces("personal effectiveness"), page):
                if "competency" not in already_seen:
                    return "competency" 
    if re.search(addSpaces("leadership trait behaviors"), page):
        if "leadership trait behaviors" not in already_seen:    
            return "leadership trait behaviors"
    if re.search(addSpaces("pwr score"), page) or \
        re.search(addSpaces("pwr assessment"), page):
        if "pwr score" not in already_seen:
            return "pwr score"
    if re.search(addSpaces("key strengths"), page) or \
        re.search(addSpaces("biggest risk areas"),page) or \
        re.search(addSpaces("development areas"),page):
        return "strengths or weaknesses"
    if re.search(addSpaces("your questions"), page) or re.search(addSpaces("key questions"), page):
        if "questions" not in already_seen:
            return "questions"
    if re.search(addSpaces("career goals and motivations"), page):
        if "career goals" not in already_seen:
            return "career goals"
    if re.search(addSpaces("supporting data"), page):
        if "supporting data" not in already_seen:
            return "supporting data"
    if re.search(addSpaces("career overview"), page) or re.search(addSpaces("detailed assessment data"), page):
        if "career" not in already_seen:
            return "career"
    return "other"

def identify_career(page, already_seen):
    if re.search("^\\s*.*smartassessment", page):
        return "info"
    if re.search(addSpaces("prepared for"), page) and \
        re.search(addSpaces("prepared by"), page) and \
        re.search(addSpaces("purpose of this"), page):
        if "info" not in already_seen:
            return "info"
    if re.search(addSpaces("rating definitions"), page):
        if "rating definitions" not in already_seen:
            return "rating definitions"
    if re.search("\\.{10,}", page) or re.search(addSpaces("table of contents"), page):
        return "contents"
    if re.search(addSpaces("executive summary"), page) or \
        re.search(addSpaces("what do you need to be aware of?"), page):
        if "summary" not in already_seen:
            return "summary"
    if re.search(addSpaces("\\n\\ncontents\\n\\n"), page) or re.search(addSpaces("disclaimer and confidentiality policy"), page):
        if "disclaimer or contents" not in already_seen:
            return "disclaimer or contents"
    if re.search(addSpaces("career overview"), page) or re.search(addSpaces("detailed assessment data"), page):
        if "career" not in already_seen:
            return "career"
    if re.search(addSpaces("career goals and motivations"), page):
        return "goals"
    return "other"
    
def extractCompetencies(page, comp_set, bad_chars, space_chars):
    competencies = {}
    
    #fix bad characters
    for b in bad_chars: page = page.replace(b, "")
    for s in space_chars: page = page.replace(s, " ")

    #extract the competencies
    for competency in comp_set:
        rating = np.nan #if competency is not found rating will be nan
        comp_space = addSpaces(competency)  #allow for accidental whitespace and new lines
        find_competency = re.search(comp_space, page)
        if find_competency:
            entry = page[(find_competency.end()):] #grab everything after the competency
            entry = entry.split("\\n")[0] #isolate only the current line...to prevent mixups in case of blanks
            find_rating = re.match("^\\s*(a|b|c){1}\\s*(\\+|\\-)?(?:[^a-z].*)*$", entry, flags=re.DOTALL) #also grabs the suffix i.e."+\-"
            if find_rating:
                rating=find_rating.group(1)
                suffix = find_rating.group(2)
                if suffix:
                    rating= rating + suffix
        competencies[competency] = rating            
    return competencies

def extractInfos(page, info_set, bad_chars, space_chars):
    infos = {}
    
    #drop contents section
    for line in page.splitlines():
        if re.search("\\.{3,}", line):
            page = page.replace(line, "")
    
    #fix bad characters
    for b in bad_chars: page = page.replace(b, "")
    for s in space_chars: 
        if s != "/":
            page = page.replace(s, " ")

    #extract the competencies
    for info in info_set:
        entry = np.nan #if competency is not found rating will be nan
        info_reg = makeReg(info)
        find_info = re.search("\\n\\s*" + info_reg + "\\s{2,}", page)
        if find_info:
            entry = page[(find_info.end()):] #grab everything after the info
            entry = entry.split("\\n")[0] #isolate only the current line...to prevent mixups in case of blanks
            entry = " ".join(entry.split()) #get rid of leading, trailing, and consecutive whitespace
        infos[info] = entry
    return infos

def extract_career(page):
    #the company and position info are usually followed by a new line that starts with "expectations"
    #however the start of the info is not easy to uniformly identify.
    #the only semi uniform attribute is that the company and position info is not indented
    #so keep everything before the "expectations" until we reach two consecutive indented lines
    #need to search in reverse because we know the end but not the start of the regex
    matches = re.findall("snoitatcepxe\\s{0,4}\\n{2}(.*?)(?:[^\\n]+?[^\\S\\n]{10,}\\n{2,}){2}", page[::-1], flags=re.DOTALL)
    if len(matches)==0:
        matches = re.findall("stnemhsilpmocca\\s{0,4}\\n{2}(.*?)(?:[^\\n]+?[^\\S\\n]{10,}\\n{2,}){2}", page[::-1], flags=re.DOTALL)
    career = [re.sub("\\n", "|", x[::-1]).strip() for x in matches]
    return " AND \n".join(career)


        