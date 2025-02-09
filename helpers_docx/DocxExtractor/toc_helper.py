# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 23:19:28 2020

@author: Asser.Maamoun
"""
import re

#### Get a count for each type of toc entry
def tocCleaner(section):
    if re.search("^(t|t34t)?career goals", section):
        section = "career goals"
    elif re.search("genome", section):
        section = "genome competencies"
    elif re.search("^(t|t34t)?(key outcomes|outcomes)", section):
        section = "outcomes"
    elif re.search("^(t|t34t)?(key|your) ?question", section):
        section = "questions"
    elif re.search("^(t|t34t)?mission ?(for|-|–|of)", section):
        section = "mission"
    elif re.search("strengths", section):
        section = "strengths and weaknesses"
    elif re.search("^(t|t34t)?scorecard", section):
        section = "scorecard"
    elif re.search("fit to scorecard", section):
        section = "scorecard"
    elif re.search("detail", section):
        section = "detail"
    elif re.search("supporting data", section):
        section = "supporting data"
    elif re.search("disclaimer", section):
        section = "disclaimer"
    elif re.search("smartfeedback report", section):
        section = "report"
    elif re.search("competenc", section) and (re.search("standard", section) or re.search("ghsmart", section)):
        section = "competency"
    elif re.search("^(t|t34t)?competenc", section):
        section = "competency"
    elif re.search("^(key|leadership) competencies$", section):
        section = "competency"
    elif re.search("executive ?summary", section):
        section = "summary"
    elif re.search("definition", section):
        section = "rating definitions"
    elif re.search("recommendation", section):
        section = "recommendation"
    elif re.search("personality", section):
        section = "other"
    elif re.search("(providers|participants)", section):
        section = "interview participants"
    return section



def docTocChecker(tracker, tocs, docx_paths, table_type):
    notfoundComp = []
    for doc_id in range(len(tocs)):
        doc_toc = tocs[doc_id]
        doc_row = tracker[(tracker['doc_id']==doc_id) & (tracker['table']==table_type)]
        if (doc_row.iloc[0]['parsed'] == 0) & ("competency" in doc_toc):
            notfoundComp.append(docx_paths[doc_id])
    notfoundComp = sorted(notfoundComp)
    return notfoundComp