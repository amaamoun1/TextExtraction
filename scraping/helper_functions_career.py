# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 19:58:43 2021

@author: Asser.Maamoun
"""

import os
import re
import pandas as pd
import datetime
import dateutil
import numpy as np
import openpyxl

#############################################################################
#    helper functions
#############################################################################

suffixes = ['ag', 'co', 'company', 
            'corporation', 'corp', 'inc',
            'gp', 'grp', 'group',
            'holding', 'holdings',
            'international', 'intl', 
            'lc', 'llc', 'llp', 'lp',  
            'ltd', 'lte', 'limited', 'incorporated', 'pllc', 'plc', 'mfg', 'pc', 'pa']

stopwords = ["previously", "formerly", "known as", "acquired", "portfolio company", 
             'an', 'and', 'of', 'the', 'at', 'in', 'on', 'a', 'by', 'as']

def get_hyperlinks(ws, column_number, num_rows):
    links = []
    for i in range(1,num_rows+1):
        try:
            url_candidate = ws.cell(row=i+1, column=column_number).hyperlink.target
        except:
            url_candidate = ws.cell(row=i+1, column=column_number).value
        links.append(url_candidate)
    return links


def clean_excel_date(date):
    if pd.isnull(date):
        return np.nan
    date = re.sub("\.0$", "", str(date).strip())
    if pd.isnull(date) or date=="" or date==".":
        return np.nan
    elif date.lower() =="present":
        return str(dateutil.parser.parse("July 1 2021"))[:10]
    elif len(date)>4:
        try:
            date = dateutil.parser.parse(date, default=default_date)
            date = str(date)[:10]
        except:
            try:
                date = pd.Timedelta(int(date), unit='d') + datetime.datetime(1899, 12, 30)
                date = str(date)[:10]
            except:
                print("FAILED:", date)
                return date
    return date
             
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



def find_hiring_dates(linkedin, search_company=np.nan, search_position=np.nan, hired_position=np.nan):
    if hired_position=="" or hired_position=="." or pd.isnull(hired_position):
        hired_position=np.nan
    else:
        try:
            hired_position=int(hired_position)
        except:
            print("FAILED:", hired_position)
            return np.nan, np.nan
    if linkedin=="" or pd.isnull(linkedin):
        print("NO INFO:", linkedin)
        return np.nan, np.nan
    
    search_company = clean_company(search_company)
    jobs = linkedin.split("\n")
    num=0
    #print("start:",jobs, ":end")
    for job in jobs:
        num+=1
        #print(job)
        parts = job.lower().split("||")
        dates = parts[0].strip()
        company = clean_company(parts[1]).strip()
        position = parts[2].strip()
        position = position.replace("chief financial officer", "cfo")
        position = position.replace("chief executive officer", "ceo")
        if num==hired_position:
            start = dates.split(" - ")[0]
            end = dates.split(" - ")[1]
            return start, end
        elif (search_company==company):
            if pd.isnull(search_position) or pd.isnull(position):
                continue
            elif (("ceo" in search_position) and ("ceo" in position)) or \
            (("cfo" in search_position) and ("cfo" in position)):
                start = dates.split(" - ")[0]
                end = dates.split(" - ")[1]
                return start, end
    print("FAILED:", search_company, search_position, hired_position)
    return np.nan, np.nan


default_date = dateutil.parser.parse("January 1 2020")        
def find_tenure(interview, start, end):
    try:
        interview = dateutil.parser.parse(interview, default=default_date)
    except:
        print("FAILED:", interview)
        return np.nan, np.nan
    if pd.isnull(start) or pd.isnull(end) or start=="none" or end=="none":
        print("FAILED:", start, end)
        return np.nan, np.nan
    
    length_before = np.nan
    length_after = np.nan
    
    if start == "present":
        return np.nan, np.nan
    elif len(start)==4:
        start = int(start)
        length_before = (interview.year - start) * 12
    else:
        try:
            start = dateutil.parser.parse(start, default=default_date)
        except:
            print("FAILED:", start)
            return np.nan, np.nan
        length_before = interview - start
        length_before = length_before / datetime.timedelta(days=30.5)
        
    if end == "present":
        if type(start)==int:
            end = 2021
            length_after = (end - max(start, interview.year)) * 12
        else:
            end = dateutil.parser.parse("March 1 2021")
            length_after = end - max(start, interview)
            length_after = length_after / datetime.timedelta(days=30.5)
    elif len(end)==4:
        end = int(end)
        if type(start)==int:
            length_after = (end - max(start, interview.year)) * 12
        else:
            length_after = (end - max(start.year, interview.year)) * 12 
    else:
        try:
            end = dateutil.parser.parse(end, default=default_date)
        except:
            print("FAILED:", end)
            return np.nan, np.nan
        if type(start)==int:
            length_after = (end.year - max(start, interview.year)) * 12
        else:
            length_after = end - max(start, interview)
            length_after = length_after / datetime.timedelta(days=30.5)
        
    return round(length_before), round(length_after)

find_tenure("january 2014", "april 2014", "april 2016")
find_tenure("march 2014", "april 2013", "september 2016")
find_tenure("march 2014", "present", "present")
find_tenure("march 2014", "april 2014", "present")
find_tenure("march 2014", "2014", "2016")
find_tenure("march 2014", "2012", "2014")

def was_will_position(linkedin, date, company_linkedin=np.nan, hired_position=np.nan):
    
    if hired_position=="" or hired_position=="." or pd.isnull(hired_position):
        hired_position=np.nan
    else:
        try:
            hired_position=int(hired_position)
        except:
            hired_position=np.nan
    
    if pd.notnull(company_linkedin):
        company_linkedin = clean_company(company_linkedin)
        
    try:
        date = dateutil.parser.parse(date, default=default_date)
    except:
        if pd.isnull(hired_position):
            print("FAILED:", date, hired_position)
            return np.nan, np.nan, np.nan, np.nan
        date=np.nan
    
    if linkedin=="" or pd.isnull(linkedin):
        print("NO INFO:", linkedin)
        return np.nan, np.nan, np.nan, np.nan
    
    past_ceo = 0
    past_cfo = 0
    future_ceo = 0
    future_cfo = 0
    
    jobs = linkedin.split("\n")
    num = 0
    for job in jobs:
        num+=1
        parts = job.lower().split("||")
        
        if parts[0]=="":
            parts=parts[1:]
        if len(parts)<3:
            print("FAILED: ", jobs, "JOB:", job)
            continue
        dates = parts[0].strip()
        start = dates.split(" - ")[0]
        if start == "present" or start=="none":
            continue
        try:
            start = dateutil.parser.parse(start, default=default_date)
        except:
            if pd.isnull(hired_position):
                continue
            else:
                start = np.nan
        
        company = parts[1]
        company = clean_company(company)
        position = parts[2].strip()
        position = position.replace("chief financial officer", "cfo")
        position = position.replace("chief executive officer", "ceo")
        
        if pd.notnull(hired_position):
            if num<hired_position:
                if ("ceo" in position):
                    past_ceo = 1
                if ("cfo" in position):
                    past_cfo = 1
            elif num>hired_position:
                if ("ceo" in position):
                    future_ceo = 1
                if ("cfo" in position):
                    future_cfo = 1
        else:
            if pd.notnull(company_linkedin) and pd.notnull(date) and start<date and company_linkedin!=company:
                if ("ceo" in position):
                    past_ceo = 1
                if ("cfo" in position):
                    past_cfo = 1
            elif pd.notnull(company_linkedin) and pd.notnull(date) and start>date and company_linkedin!=company:
                if ("ceo" in position):
                    future_ceo = 1
                if ("cfo" in position):
                    future_cfo = 1
    return past_ceo, past_cfo, future_ceo, future_cfo
    