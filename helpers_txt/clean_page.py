# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 22:16:53 2020

@author: Asser.Maamoun
"""

import re

def cleanPageDefault(page):
    #make lower case
    page=page.lower()
    
    #### OLD
    #need to get undo the fact that "-/+" always appear on a new line
    #cleaned1 = re.sub("\n\-\n", "-", page)
    #cleaned1 = re.sub("\n\+\n", "+", cleaned1)
    #make slashes appear on the same line
    #cleaned1 = re.sub("\n/", "/", cleaned1)
    #### END OLD
    
    #get rid of consecutive empty lines
    cleaned2 = re.sub("[\r\x07\x0C]", "\n", page)
    cleaned2 = re.sub("\n[^\S\n]+", "\n", cleaned2) #make new lines start with a non-Space character
    cleaned2 = re.sub("\n{4,}", "\n\n\n", cleaned2)
    #replace leading and trailing spaces of pages with a single new line
    cleaned3 = re.sub("^\s*", "\n", cleaned2)
    cleaned3 = re.sub("\s*$", "\n", cleaned3)
    #clear the boilerplate language if possible
    cleaned3 = re.sub("^\s*confidential\s+", "\n", cleaned3)
    cleaned3 = re.sub("©.*?\n\n+", "", cleaned3, flags=re.DOTALL)
    cleaned3 = re.sub("\s+page\s+\d{1,2}\s+of\s+\d{1,2}\s+", "\n\n", cleaned3)

    return cleaned3

def cleanPageInfo(page):
    #make lower case
    page=page.lower()
    
    #### OLD
    #need to get undo the fact that "-/+" always appear on a new line
    #cleaned1 = re.sub("\n\-\n", "-", page)
    #cleaned1 = re.sub("\n\+\n", "+", cleaned1)
    #make slashes appear on the same line
    #cleaned1 = re.sub("\n/", "/", cleaned1)
    #### END OLD
    
    #get rid of consecutive empty lines
    cleaned2 = re.sub("[\r\x07\x0C]", "\n", page)
    # cleaned2 = re.sub("\n[^\S\n]+", "\n", cleaned2) #make new lines start with a non-Space character
    cleaned2 = re.sub("\n{4,}", "\n\n\n", cleaned2)
    #replace leading and trailing spaces of pages with a single new line
    cleaned3 = re.sub("^\s*", "\n", cleaned2)
    cleaned3 = re.sub("\s*$", "\n", cleaned3)
    #clear the boilerplate language if possible
    cleaned3 = re.sub("^\s*confidential\s+", "\n", cleaned3)
    cleaned3 = re.sub("©.*?\n\n+", "", cleaned3, flags=re.DOTALL)
    cleaned3 = re.sub("\s+page\s+\d{1,2}\s+of\s+\d{1,2}\s+", "\n\n", cleaned3)

    return cleaned3

def cleanPageScorecard(page):
    #make lower case
    page=page.lower()
    
    #get rid of consecutive empty lines but do not (!!!) force new lines to start with a non-Space character
    cleaned2 = re.sub("[\r\x07\x0C]", "\n", page)
    cleaned2 = re.sub("\n{4,}", "\n\n\n", cleaned2)
    
    #replace trailing spaces of pages with a single new line
    #do not trim leading spaces due to grades on right side of page
    cleaned3 = re.sub("\s*$", "\n", cleaned2)
    
    #clear the boilerplate language if possible...specifically any lines that start with confidential
    cleaned3 = re.sub("^\W*confidential.*?\n+", "\n", cleaned3, flags=re.DOTALL)
    cleaned3 = re.sub("\n\W*confidential.*?\n+", "\n", cleaned3, flags=re.DOTALL)
    cleaned3 = re.sub("©.*?\n+", "\n", cleaned3, flags=re.DOTALL)
    cleaned3 = re.sub("\s*page\s+\d{1,2}\s+of\s+\d{1,2}\s+", "", cleaned3)

    return cleaned3