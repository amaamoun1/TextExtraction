# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 16:53:54 2021

@author: Asser.Maamoun
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException

import sys
import codecs
import time
import pandas as pd
import unicodedata
import numpy as np
import re
import datetime
import random
import csv
import openpyxl




#############################################################################
#    load the manual search file
#############################################################################

file = r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\04 manual_search\manual_search_yann.xlsx"

df = pd.read_excel(file)
wb = openpyxl.load_workbook(file)
ws = wb['Sheet1']


############################################
#  Input Variables
############################################

path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping"

usrName = "steven.kaplan@chicagobooth.edu"
pssWrd = "Smartproj17"
url = 'https://www.linkedin.com'
url_recruiter = 'https://www.linkedin.com/cap/dashboard/home'

results_name = "/04 manual_search/results_manual.csv"
start=False

############################################
#  Scraping Loop
############################################

#open up google chrome
driver = webdriver.Chrome(executable_path='/Users/Asser.Maamoun/Downloads/chromedriver')
driver.maximize_window()

#navigate to linkedin 
driver.get(url)
time.sleep(10)

#login
driver.find_element_by_class_name('nav__button-secondary ').click()
time.sleep(5)
driver.find_element_by_name('session_key').send_keys(usrName)
driver.find_element_by_name('session_password').send_keys(pssWrd)
driver.find_element_by_class_name('login__form_action_container ').click()
time.sleep(30)

#open linkedin recruiter
driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[1])
driver.get(url_recruiter)
time.sleep(random.uniform(3,5))
driver.find_element_by_xpath('//*[@id="advanced-search"]').click()
driver.find_element_by_xpath('//*[@class="no-btn"]').click()


#set up results file if this is the first run, else check those already scraped in past runs
if start==True:
    with open(path_out + "/" + results_name, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["i", "start_time", "docid", "url"])
    done = set()
else:  
    done = pd.read_csv(path_out + "/" + results_name)
    done = set(done['docid'])
    
    
with open(path_out + "/" + results_name, 'a', newline='') as f:
    writer = csv.writer(f)
    for i in range(len(df)):
        url_candidate = df['linkedin_link'][i]
        docid = "oldid_" + str(df['doc_id_old'][i]) + "_newid_" + str(df['doc_id_new'][i])
        if docid in done:
            print("ALREADY SCRAPED")
            continue
        firstname = df['candidate_firstname'][i]
        lastname = df['candidate_lastname'][i]
        start_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(i, docid, start_time)
        if url_candidate ==".":
            writer.writerow([i, start_time, docid, firstname, lastname, url_candidate])
            print("NOT ON LINKEDIN")
            continue
        elif pd.isnull(url_candidate):
            print("NO URL")
            continue
        else:
            try:
                url_candidate = ws.cell(row=i+2, column=16).hyperlink.target
            except:
                url_candidate = df['linkedin_link'][i]
            
        #allow the scraper 3 attempts for each candidate
        success=False
        tries=0    
        while (success==False) and (tries<3):
            #attempt
            try:
                
                time.sleep(random.uniform(1,2))
                driver.get(url_candidate)
                
                #grabs page source and saves
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='profile-info']")))
                driver.execute_script("window.scroll(0,1500)")
                time.sleep(random.uniform(8,12))
                content = driver.page_source.encode('utf-8').strip()
                with open(path_out + "/htmls/" + docid + "_manual.html", "w") as f:
                    f.write(str(content))
                driver.execute_script("window.scroll(0,-1500)")
                time.sleep(random.uniform(1,2))
                
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    name = soup.select("div.profile-info > h1.searchable")[0].text.strip()
                except IndexError:
                    name = "out_of_network"
                                          
                print("                       FOUND")
                success=True
                writer.writerow([i, start_time, docid, firstname, lastname, url_candidate, name])
            except KeyboardInterrupt:
                raise
            except:
                #keep track of exception
                msg = sys.exc_info()[0]
                print("FAILED ATTEMPT", msg)
                #prep for next attempt at the candidate
                success=False
                tries+=1
                #enforce timeout and renavigate to recruiter search page
                time.sleep(random.uniform(5*60,6*60))
                driver.get(url_recruiter)
        assert success==True



