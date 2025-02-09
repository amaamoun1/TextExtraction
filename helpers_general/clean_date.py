# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 14:57:44 2020

@author: Asser.Maamoun
"""

import re
import pandas as pd
import numpy as np
import datetime
    
#############################################################################
#        date cleaning 
#############################################################################

months_long = { 
        'january': "01",
        'february': "02",
        'march': "03",
        'april': "04",
        'may': "05",
        'june': "06",  
        'july': '07',
        'august': '08',
        'september': '09',
        'october': '10',
        'november': '11',
        'december': '12'        
        }

months_short = { 
        'jan': "01",
        'feb': "02",
        'mar': "03",
        'apr': "04",
        'may': "05",
        'june': "06",  
        'july': '07',
        'aug': '08',
        'sept': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12'        
        }

days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
suffixes = ["st", "rst", "nd", "rd", "th", "d"]


def cleanDateSingle(date_orig):
    #check for datetimes
    if pd.isnull(date_orig):
        return date_orig
    if type(date_orig)==datetime.datetime:
        return date_orig.strftime("%Y-%m-%d")
    date_orig=date_orig.lower()
    
    #clean out comma
    date = re.sub(",", " ", date_orig)
    date = re.sub("\.", " ", date)
    
    #clean out day of week
    for day in days_of_week:
        date = re.sub(day, "", date)
    
    #clean out day suffixes
    for suf in suffixes:
        date = re.sub("(?<=\d)" + suf + "\\b", "", date)
    
    #clean out everything thats not a digit at the end of the string
    date = re.sub("\D+$", "", date)
    date = re.sub("update", "", date)
    date = re.sub("date", "", date)
    date = re.sub("\\bof\\b", "", date)
    date = re.sub("^d\s", "", date)
      
    #clean out unnecessary whitespace
    date = " ".join(date.split())
    date = re.sub("^\s+", "", date)
    date = re.sub("\s+$", "", date)
    
    #empty
    if date=="":
        print("NOW NULL:", date_orig)
        return np.nan    
    # 1) 2/14/2015 => 2015-02-14
    match = re.match('^(\d{1,2})\/(\d{1,2})\/(\d{4})$', date)
    if match is not None:
        return '{2}-{0:0>2}-{1:0>2}'.format(*match.groups())
    # 2) 2/14/15 => 2015-02-14
    match = re.match('^(\d{1,2})\/(\d{1,2})\/(\d{2})$', date)
    if match is not None:
        return "20" + '{2}-{0:0>2}-{1:0>2}'.format(*match.groups())
    # 3) february 14 2015 => 2015-02-14
    for m in months_long:
        match = re.match('^' + m + '\s(\d{1,2})\s(\d{4})', date)
        if match is not None:
            return match[2] + "-" + months_long[m] + "-" + '{0:0>2}'.format(match[1])
    # 4) feb 14 2015 => 2015-02-14
    for m in months_short:
        match = re.match('^' + m + '\s(\d{1,2})\s(\d{4})', date)
        if match is not None:
            return match[2] + "-" + months_short[m] + "-" + '{0:0>2}'.format(match[1])
    # 5) 14 february 2015 => 2015-02-14
    for m in months_long:
        match = re.match('^(\d{1,2})\s' + m + '\s(\d{4})', date)
        if match is not None:
            return match[2] + "-" + months_long[m] + "-" + '{0:0>2}'.format(match[1])
    # 6) 14 feb 2015 => 2015-02-14
    for m in months_short:
        match = re.match('^(\d{1,2})\s' + m + '\s(\d{4})', date)
        if match is not None:
            return match[2] + "-" + months_short[m] + "-" + '{0:0>2}'.format(match[1])
    # 6) feb 2015 => 2015-02
    for m in months_long:
        match = re.match('^' + m + '\s(\d{6})', date)
        if match is not None:
            return match[1][2:] + "-" + months_long[m] + "-" + match[1][:2]
        else:
            match = re.match('^' + m + '\s(\d{4})', date)
            if match is not None:
                return match[1] + "-" + months_long[m]
    # 7) 2004-11-23
    if re.match('^(\d{4})\\-(\d{2})\\-(\d{2})$', date):
        return date
    print("Could not clean:", date_orig)
    return np.nan

def cleanDate(dates):
    cleaned = []
    for date in dates:
        if not pd.isnull(date):
            clean = cleanDateSingle(date)
            cleaned.append(clean)
        else:
            cleaned.append(date)
    return cleaned


