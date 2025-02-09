
# -*- coding: utf-8 -*-
"""

"""

import numpy as np
import pandas as pd
import re
from parse_page import identifyPage
from parse_page import identify_career
# from parse_page import extractCompetencies
# from parse_page import extractScorecard



def identifyAllPages(txtPages):
    #set up document level data storage
    tables_seen=[""]
    page_types = {} #key - type of page, element - list...page numbers of that type
    
    #loop through all pages in the document and identify sections
    page_id = 0
    for page_id in range(len(txtPages)):
        
        #get the page and identify
        pageText = txtPages[page_id]
        page_type = identifyPage(pageText, set(tables_seen[:-1])-set([tables_seen[-1]]))
        
        if (page_type == "other") and (tables_seen[-1]=="scorecard"):
            page_type = "scorecard"
        if (page_type == "other") and (tables_seen[-1]=="career"):
            page_type = "career"
        
        #add to the page_types dictionary and the tables_seen array
        tables_seen.append(page_type)
        if page_type not in page_types:
            page_types[page_type] = [page_id]
        else:
            page_types[page_type].append(page_id)
        
    return page_types

def identifyCareerPages(txtPages):
    #set up document level data storage
    tables_seen=[""]
    page_types = {} #key - type of page, element - list...page numbers of that type
    
    #loop through all pages in the document and identify sections
    page_id = 0
    for page_id in range(len(txtPages)):
        
        #get the page and identify
        pageText = txtPages[page_id]
        page_type = identify_career(pageText, set(tables_seen[:-1])-set([tables_seen[-1]]))
        
        if (page_type == "other") and (tables_seen[-1]=="career"):
            page_type = "career"
        
        #add to the page_types dictionary and the tables_seen array
        tables_seen.append(page_type)
        if page_type not in page_types:
            page_types[page_type] = [page_id]
        else:
            page_types[page_type].append(page_id)
        
    return page_types




def find_college_potentials(txt, colleges):
    #we search for 5 words before and after "university" or "college"
    regex = "(?:(?:\\w+\\W+){0,5})(?:(?:\\buniversity\\b)|(?:\\bcollege\\b))(?:(?:\\W+\\w+){0,5})"
    potentials = re.findall(regex, txt)
    if potentials:
        return " AND ".join(potentials)
    else:
        return np.nan


def find_college(txt, colleges):
    #combine pages into single text
    colleges_found = []
    for college in colleges:
        if re.search("\\b" + college + "\\b", txt):
            colleges_found.append(college)
    #if multiple college names were found with the most appearances, list all
    if len(colleges_found)>0:
        colleges_found = " AND ".join(colleges_found)
    else:
        colleges_found = np.nan
    return colleges_found


def find_college_ba(txt, colleges):
    #combine pages into single text
    colleges_found = []
    for college_pair in colleges:
        college = college_pair[0]
        mba_school = college_pair[1]
         
        # print(college)
        mba_r = "\\bm\\.?b\\.?a\\.?\\b"
        ba_r = "(?<![m\\.])\\bb\\.?[as]\\.?\\b"
        years_r = "\\b\\d{2,4}\\b"
        college_r = "\\b" + college.replace(".", "\\.?") + "\\b"
        potentials = None
        if re.search(college_r, txt):
            potentials = re.findall("(?:(?:\\w+\\W+){0,10})" + college_r + "(?:(?:\\W+\\w+){0,10})", txt)
        if potentials:
            #drop any mba-related schools
            if pd.notnull(mba_school):
                potentials_filtered = []
                mba_school_r = "\\b" + mba_school.replace(".", "\\.?") + "\\b"
                for potential in potentials:
                    if re.search(mba_r, potential):
                        continue
                    elif re.search(mba_school_r, potential):
                        continue
                    else:
                        potentials_filtered.append(potential)
                potentials = potentials_filtered
            if len(potentials)>0:
                #keep the best match per school
                found = college
                ba = 0
                years = 0
                for potential in potentials:
                    curr_found = college
                    curr_ba = 0
                    curr_years = 0
                    #check for ba or for years
                    if re.search(ba_r, potential):
                        curr_found = curr_found + " BA"
                        curr_ba = 1
                    if re.search(years_r, potential):
                        curr_found = curr_found + " YEARS"
                        curr_years = 1
                    #update above
                    if (curr_ba>ba) or (curr_ba==ba and curr_years>years):
                        found = curr_found
                        ba = curr_ba
                        years = curr_years
                colleges_found.append(found)
    #if multiple college names were found with the most appearances, list all
    if len(colleges_found)>0:
        colleges_found = " AND ".join(colleges_found)
    else:
        colleges_found = np.nan
    return colleges_found

def find_mba(txt, schools): 
    #combine pages into single text
    schools_found = []
    for pair in schools:
        # print(pair)
        added = 0
        school = pair[0]
        uni = pair[1]
        need_at = pair[2]
        mba_r = "\\bm\\.?b\\.?a\\.?\\b"
        years_r = "\\b\\d{2,4}\\b"
        school_r = "\\b" + school.replace(".", "\\.?") + "\\b"
        uni_r = "\\b" + uni.replace(".", "\\.?") + "\\b"
        if re.search(school_r, txt):
            potentials = re.findall("(?:(?:\\w+\\W+){0,10})" + school_r + "(?:(?:\\W+\\w+){0,10})", txt)
            #keep the best match per school
            found = "SCHOOL " + school
            mba = 0
            years = 0
            at = 0
            for potential in potentials:
                curr_found = "SCHOOL " + school
                curr_mba = 0
                curr_years = 0
                curr_at = 0
                #check if we can find the university, mba, or years of attendance near the school
                if re.search(uni_r, potential):
                    curr_found = curr_found + " UNI " + uni
                    curr_at = 1
                if re.search(mba_r, potential):
                    curr_found = curr_found + " MBA"
                    curr_mba = 1
                if re.search(years_r, potential):
                    curr_found = curr_found + " YEARS"
                    curr_years = 1
                #update above only if we have a better match now
                if (curr_at>at) or (curr_at==at and curr_mba>mba) or (curr_at==at and curr_mba==mba and curr_years>years):
                    found = curr_found
                    at = curr_at
                    mba = curr_mba
                    years = curr_years
            if at == 1 or (need_at == 0 and (mba==1 or years==1)):
                schools_found.append(found)
                added = 1
        if (added==0) and (uni not in ' '.join(schools_found)): #only continue if we werent able to find a satisfactory school search
            if re.search(uni_r, txt):
                potentials = re.findall("(?:(?:\\w+\\W+){0,10})" + uni_r + "(?:(?:\\W+\\w+){0,10})", txt)
                #keep the best match per school
                found = "UNI " + uni
                mba = 0
                years = 0
                for potential in potentials:
                    curr_mba = 0
                    curr_years = 0
                    curr_found =  "UNI " + uni
                    #check if we can find mba or years near the university
                    if re.search(mba_r, potential):
                        curr_found = curr_found + " MBA"
                        curr_mba = 1
                    if re.search(years_r, potential):
                        curr_found = curr_found + " YEARS"
                        curr_years = 1
                    #update above only if we were able to find mba near the university
                    if (curr_mba==1) and (curr_years>=years):
                        found = curr_found
                        mba = curr_mba
                        years = curr_years
                #only add to schools_found if we found mba near the school
                if (mba==1):
                    schools_found.append(found)
                    added = 1
    #if multiple college names were found with the most appearances, list all
    if len(schools_found)>0:
        schools_found = " AND ".join(schools_found)
    else:
        schools_found = np.nan
    return schools_found

def find_gender(txt, name):
    male = 0
    female = 0
    if pd.notnull(name):
        method = "in_name"
        male += len(re.findall("\\bmr[\\.\\s]+", name))
        female += len(re.findall("\\bms[\\.\\s]+", name)) 
        female += len(re.findall("\\bmrs[\\.\\s]+", name))
        if (male>female) and (male>0):
            gender="m"
        elif (female>male) and (female>0): 
            gender="f"
        elif (female == male) and (female>0):
            gender = "tie"
        else: 
            method = "find_names"
            name = re.sub("[^a-z\\s]", "", name) #drop all non letters non-spaces
            names = list(set(name.split()))
            for name in names:
                male += len(re.findall("\\bmr[\\.\\s]+"+name, txt))
                female += len(re.findall("\\bms[\\.\\s]+"+name, txt)) 
                female += len(re.findall("\\bmrs[\\.\\s]+"+name,txt))
            if (male>female) and (male>0):
                gender="m"
            elif (female>male) and (female>0): 
                gender="f"
            elif (female == male) and (female>0):
                gender = "tie"
    if (female==0) and (male==0):
        method = "find_pronouns"
        male = len(re.findall("\\bmr[\\.\\s]", txt)) + len(re.findall("\\bhe\\b", txt)) + \
            len(re.findall("\\bhis\\b", txt)) + len(re.findall("\\bhim\\b", txt))
        female = len(re.findall("\\bms[\\.\\s]", txt)) + len(re.findall("\\bmrs[\\.\\s]",txt)) + \
                len(re.findall("\\bshe\\b", txt)) + len(re.findall("\\bher\\b", txt)) + \
                len(re.findall("\\bhers\\b", txt))
        
        if (male>female) and (male>0):
            gender="m"
        elif (female>male) and (female>0): 
            gender="f"
        elif (female == male) and (female>0):
            gender = "tie"
        else:
            gender = "nf"
    flag = int((male>0) and (female>0))
    return gender, method, male, female, flag





