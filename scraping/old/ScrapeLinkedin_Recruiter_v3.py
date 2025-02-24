import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
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


#############################################################################
#    Prep the candidates data
#############################################################################

def is_ceo_cfo(titles):
    ceo = 0
    for title in titles.split(" AND "):
        if ("ceo" not in title) and ("cfo" not in title):
            continue
        if re.match("(ceo succession|deputy|division|region|assistant|office of)", title):
            continue
        ceo=1
    return ceo

#read in extractions and select pre or post 2012
candidates = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")
candidates = candidates[candidates['doc_id_old']!=-1].copy()

#only search relevant people, no duplicates!
candidates = candidates.replace(np.nan, '', regex=True)
candidates = candidates[candidates['is_duplicate']==0]
candidates = candidates[candidates['candidate_flag']!=1]
candidates = candidates[[x!="" for x in candidates['candidate_firstname']]]
candidates = candidates[[x!="" for x in candidates['candidate_lastname']]]

#only ceos and cfos
candidates['ceo_cfo'] = candidates['title_clean'].apply(is_ceo_cfo)
candidates = candidates[candidates['ceo_cfo']==1]

#set up variables for scraping loop
candidates = candidates[["doc_id_old", "doc_id_new", "candidate_firstname", "candidate_lastname", "company_clean", "company_flag", "undergrad_clean", "mba_clean", "college_raw", "college_potential"]]
candidates['doc_id_full'] = "oldid_" + candidates['doc_id_old'].astype(str) + "_newid_" + candidates['doc_id_new'].astype(str)
candidates = candidates.reset_index(drop=True)

#use imprecise schools when the precise method is not available
df = []
for i, row in candidates.iterrows():
    row['schools'] = row['undergrad_clean'] + ' AND ' + row['mba_clean']
    row['schools'] = '"' + row['schools'].strip(" AND ").replace(' AND ', '" "') + '"'
    row['schools'] = row['schools'].replace('""', '')
    row['schools_type'] = 'narrow'
    if row['schools']=="":
        if row['college_raw'] != "":
            row['schools']='"' + row["college_raw"].replace(' AND ', '" "') + '"' 
        row['schools_type'] = 'broad'
    df.append(row)
df = pd.DataFrame(df)
del candidates, i, row

#############################################################################
#    Import Data and Basic cleaning
#############################################################################


############################################
#  Input Variables
############################################

path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/v3"

usrName = "steven.kaplan@chicagobooth.edu"
pssWrd = "Smartproj17"
url = 'https://www.linkedin.com'
url_recruiter = 'https://www.linkedin.com/cap/dashboard/home'


############################################
#  Scraping Loop
############################################

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



#check those already scraped
done = pd.read_csv(path_out + "/results.csv")
done = set(done['docid'])


with open(path_out + "/results.csv", 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["i", "start_time", "docid", "firstname", "lastname", "company", "company_flag", "schools", "schools_type", "num_results", "is_namematch", "url"])
    for i in range(200):
        
        #grab candidate info
        docid = df['doc_id_full'][i]
        firstname = df['candidate_firstname'][i]
        lastname = df['candidate_lastname'][i]
        company = df['company_clean'][i]
        company_flag = df['company_flag'][i]
        schools = df['schools'][i]
        schools_type = df['schools_type'][i]
        
        #skip candidates already scraped
        if docid in done:
            print(i, docid, "ALREADY SCRAPED")
            continue
        
        #only run in 3 2-hour intervals a day
        start_time = datetime.datetime.now().strftime('%H:%M:%S')
        start_hour = int(re.match("\\d+", start_time).group(0))
        # while ((start_hour<=11) | ((start_hour>=14) & (start_hour<=15)) | ((start_hour>=18) & (start_hour<=19)) | (start_hour>=22)):
        #     print("waiting", start_time)
        #     time.sleep(300)
        #     start_time = datetime.datetime.now().strftime('%H:%M:%S')
        #     start_hour = int(re.match("\\d+", start_time).group(0))
        
        #allow the scraper 3 attempts for each candidate
        success=False
        tries=0    
        while (success==False) and (tries<3):
            #attempt
            try:
                #grab information on new candidate
                time.sleep(random.uniform(8,12))
                start_time = datetime.datetime.now().strftime('%H:%M:%S')
                
                print(i, docid, start_time)
                
                #scroll down to name inputs
                driver.execute_script("window.scroll(0,750)")
                
                try: #first check if we can search name in left column 
                    #searches the firstname
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="facet-firstName"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="firstName-input"]').send_keys(firstname)
                    driver.find_element_by_xpath('//*[@id="firstName-input"]').send_keys(Keys.RETURN)
                    
                    #searches the last name
                    time.sleep(random.uniform(1,3))
                    searchinfo = driver.find_element_by_id("search-info")
                    driver.find_element_by_xpath('//*[@id="facet-lastName"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="lastName-input"]').send_keys(lastname)
                    driver.find_element_by_xpath('//*[@id="lastName-input"]').send_keys(Keys.RETURN)
                except NoSuchElementException:
                    #if not in left column, need to open up the advanced search
                    time.sleep(random.uniform(1,2))
                    driver.execute_script("window.scroll(0,-750)")
                    driver.find_element_by_xpath('//*[@id="advanced-search"]').click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='facet-firstName']")))
                    time.sleep(random.uniform(1,2))
                    driver.find_element_by_xpath('//*[@id="facet-firstName"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="firstName-input"]').send_keys(firstname)
                    driver.find_element_by_xpath('//*[@id="firstName-input"]').send_keys(Keys.RETURN)
                    driver.find_element_by_xpath('//*[@id="firstName-input"]').send_keys(Keys.TAB)
                    
                    #searches the last name
                    time.sleep(random.uniform(1,3))
                    searchinfo = driver.find_element_by_id("search-info")
                    driver.find_element_by_xpath('//*[@id="facet-lastName"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="lastName-input"]').send_keys(lastname)
                    driver.find_element_by_xpath('//*[@id="lastName-input"]').send_keys(Keys.RETURN)
                    
                    #click search
                    driver.find_element_by_xpath('//*[@class="yes-btn"]').click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@title="Profile keywords or boolean"]')))
                    time.sleep(random.uniform(1,2))
                    driver.execute_script("window.scroll(0,750)")
                
                #enter keywords
                time.sleep(random.uniform(1,3))
                searchinfo = driver.find_element_by_id("search-info")
                driver.find_element_by_xpath('//*[@title="Profile keywords or boolean"]').click()
                keywords = "(ceo OR cfo)"
                if schools != "":
                    keywords = schools + " AND " + keywords
                if (company_flag==1) | (company_flag==2):
                    keywords = '"' + company + '"' + " AND " + keywords
                driver.find_element_by_xpath('//*[@id="keywords-input"]').send_keys(keywords)
                driver.find_element_by_xpath('//*[@id="keywords-input"]').send_keys(Keys.RETURN)
                    
                
                #wait for search to process
                WebDriverWait(driver, 10).until(EC.staleness_of(searchinfo))
                driver.execute_script("window.scroll(0,-1000)")
                time.sleep(random.uniform(4,8))
                
                #checks if any results occur and tracks number of results
                searchinfo = driver.find_element_by_id("search-info")
                num_results = searchinfo.text
                if num_results=="":
                    num_results = driver.find_element_by_xpath("//*[@id='search-results']").text
                    if num_results=="No candidates found":
                        writer.writerow([i, start_time, docid, firstname, lastname, company, company_flag, schools, schools_type, 0,""])
                        driver.find_element_by_xpath('//*[@id="clear-search"]').click()
                        success=True
                        continue
                num_results = int(re.search("\\d+", num_results).group())
                
                #click on first result with EXACT name match (i.e. no nicknames)
                #but only check the first 5 results
                is_namematch = False
                result_num = 0
                while (is_namematch==False) and (result_num<min(num_results, 5)):
                    result_num += 1
                    xpath_name = "//*[@id='search-results']/li[" + str(result_num) + "]//*[@class='name']"
                    found_name = driver.find_element_by_xpath(xpath_name).text.lower()
                    is_namematch = found_name == firstname + " " + lastname
                
                time.sleep(random.uniform(1,2))
                if is_namematch == False: #click on first result
                    driver.find_element_by_xpath("//*[@id='search-results']/li[1]//*[@class='name']").click()
                else: #click on true name match
                    driver.find_element_by_xpath(xpath_name).click()
                
                #grabs page source and saves
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='profile-info']")))
                writer.writerow([i, start_time, docid, firstname, lastname, company, company_flag, schools, schools_type, num_results, is_namematch, driver.current_url])
                time.sleep(random.uniform(1,2))
                driver.execute_script("window.scroll(0,1500)")
                time.sleep(random.uniform(8,12))
                content = driver.page_source.encode('utf-8').strip()
                with open(path_out + "/htmls/" + docid + ".html", "w") as f:
                    f.write(str(content))
                driver.execute_script("window.scroll(0,-1500)")
                time.sleep(random.uniform(1,2))
                
                #return to advanced search page
                driver.find_element_by_xpath('//*[@id="advanced-search"]').click()
                nobtn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="no-btn"]')))
                time.sleep(random.uniform(1,3))
                nobtn.click()
                success=True
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
                time.sleep(random.uniform(10,12))
                driver.find_element_by_xpath('//*[@id="advanced-search"]').click()
                driver.find_element_by_xpath('//*[@class="no-btn"]').click()
        assert success==True



