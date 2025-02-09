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

#only search relevant people, no duplicates!
candidates = candidates.replace(np.nan, '', regex=True)
candidates = candidates[candidates['is_duplicate']==0]
candidates = candidates[candidates['candidate_flag']!=1]
candidates = candidates[[x!="" for x in candidates['candidate_firstname']]]
candidates = candidates[[x!="" for x in candidates['candidate_lastname']]]

#designate those that are ceos
candidates['ceo_cfo'] = candidates['title_clean'].apply(is_ceo_cfo)

#set up variables for scraping loop
candidates = candidates[["doc_id_old", "doc_id_new", "candidate_firstname", "candidate_lastname", "company_clean", "company_flag", "ceo_cfo", "career_clean"]]
candidates['doc_id_full'] = "oldid_" + candidates['doc_id_old'].astype(str) + "_newid_" + candidates['doc_id_new'].astype(str)
candidates = candidates.reset_index(drop=True)

#use latest company in career section
def latest_company(career):
    if pd.isnull(career) or career=='':
        return ''
    latest_job = career.split("\n")[0]
    try:
        return re.sub("<u\+.*?>", "", latest_job.split("||")[2]).strip()
    except IndexError:
        return ''

candidates['latest_company'] = candidates['career_clean'].apply(latest_company)
df = pd.DataFrame(candidates)
del candidates


#only search those that were not already found using university
past_results1 = pd.read_csv(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\01 university_company_scrape\results_ceos_cfos.csv")
past_results2 = pd.read_csv(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\01 university_company_scrape\results_other.csv")
past_docids = set(past_results1[past_results1['num_results']>0]['docid']).union(set(past_results2[past_results2['num_results']>0]['docid']))
df = df[[x not in past_docids for x in df['doc_id_full']]]


#only use the latest jobs that are clean
df.to_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\02 career_onlyname_scrape\latest_job.xlsx", index=False)
df = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\02 career_onlyname_scrape\latest_job_fixed_other.xlsx")
df['latest_company'] = df['latest_company'].fillna("")
df['career_clean'] = df['career_clean'].fillna("")
df['company_clean'] = df['company_clean'].fillna("")


#############################################################################
#    Import Data and Basic cleaning
#############################################################################


############################################
#  Input Variables
############################################

path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping"

usrName = "steven.kaplan@chicagobooth.edu"
pssWrd = "Smartproj17"
url = 'https://www.linkedin.com'
url_recruiter = 'https://www.linkedin.com/cap/dashboard/home'

search_ceos_cfos = 0
start=False

############################################
#  Scraping Loop
############################################

#setup according to the current sample
df = df[df['ceo_cfo']==search_ceos_cfos]
df = df.reset_index(drop=True)

if search_ceos_cfos==1:
    results_name = "results_career_ceos_cfos.csv"
else:
    results_name = "results_career_other.csv"

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
    with open(path_out + "/02 career_onlyname_scrape/" + results_name, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["i", "start_time", "docid", "firstname", "lastname", "company", "company_flag", "latest_career_company", "keywords", "search_type", "num_results", "is_namematch", "url"])
    done = set()
else:  
    done = pd.read_csv(path_out + "/02 career_onlyname_scrape/" + results_name)
    done = set(done['docid'])

#start scraping
with open(path_out + "/02 career_onlyname_scrape/" + results_name, 'a', newline='') as f:
    writer = csv.writer(f)
    for i in range(len(df)):
        
        #grab candidate info
        docid = df['doc_id_full'][i]
        firstname = df['candidate_firstname'][i]
        lastname = df['candidate_lastname'][i]
        company = df['company_clean'][i]
        company_flag = df['company_flag'][i]
        latest_company = df['latest_company'][i]
        
        if df['bad'][i]==1:
            print(i, docid, "BAD LATEST COMPANY")
            continue
        
        
        #skip candidates already scraped
        if docid in done:
            print(i, docid, "ALREADY SCRAPED")
            continue
        
        #only run in 3 2-hour intervals a day
        start_time = datetime.datetime.now().strftime('%H:%M:%S')
        start_hour = int(re.match("\\d+", start_time).group(0))
        while ((start_hour<=11) | ((start_hour>=14) & (start_hour<=15)) | ((start_hour>=18) & (start_hour<=19)) | (start_hour>=22)):
            print("waiting", start_time)
            time.sleep(300)
            start_time = datetime.datetime.now().strftime('%H:%M:%S')
            start_hour = int(re.match("\\d+", start_time).group(0))
        
        #setup keywords
        search_type = "none"
        if latest_company != "":
            keywords1 = latest_company
            info = ""
        else:
            keywords1 = ""
            info = "NO CAREER"
        
        #allow the scraper 3 attempts for each candidate
        success=False
        tries=0    
        while (success==False) and (tries<3):
            #attempt
            try:
                #allow some time to pass
                time.sleep(random.uniform(8,12))
                start_time = datetime.datetime.now().strftime('%H:%M:%S')
                print(i, docid, start_time, info)
                
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
                except (NoSuchElementException, ElementNotInteractableException):
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
                
                #default
                num_results="No candidates found"
                
                #enter keywords
                time.sleep(random.uniform(1,3))
                if keywords1!="":
                    search_type = "latest_company"
                    keywords = keywords1
                    searchinfo = driver.find_element_by_id("search-info")
                    driver.find_element_by_xpath('//*[@title="Profile keywords or boolean"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="keywords-input"]').send_keys(keywords)
                    driver.find_element_by_xpath('//*[@id="keywords-input"]').send_keys(Keys.RETURN)
                    time.sleep(random.uniform(0.5,1.5))
                    
                    #wait for search to process
                    WebDriverWait(driver, 10).until(EC.staleness_of(searchinfo))
                    driver.execute_script("window.scroll(0,-1000)")
                    time.sleep(random.uniform(4,8))
                    
                    #checks if any results occur and tracks number of results
                    searchinfo = driver.find_element_by_id("search-info")
                    num_results = searchinfo.text
                    if num_results=="":
                        num_results = driver.find_element_by_xpath("//*[@id='search-results']").text
                
                #deal with no results
                if num_results=="No candidates found":
                    #if no results pop up, try searching just the name:
                    keywords=""
                    search_type = "name_only"
                    if keywords1!="":
                        driver.execute_script("window.scroll(0,1000)")
                    time.sleep(random.uniform(1,3))
                    searchinfo = driver.find_element_by_id("search-info")
                    driver.find_element_by_xpath('//*[@title="Profile keywords or boolean"]').click()
                    time.sleep(random.uniform(1,3))
                    driver.find_element_by_xpath('//*[@id="keywords-input"]').clear()
                    driver.find_element_by_xpath('//*[@id="keywords-input"]').send_keys(Keys.RETURN)
                    time.sleep(random.uniform(0.5,1.5))
                    
                    #wait for search to process
                    if keywords1!="":
                        WebDriverWait(driver, 10).until(EC.staleness_of(searchinfo))
                    driver.execute_script("window.scroll(0,-1000)")
                    time.sleep(random.uniform(4,8))
                    
                    #checks if any results occur and tracks number of results
                    searchinfo = driver.find_element_by_id("search-info")
                    num_results = searchinfo.text
                    if num_results=="":
                        num_results = driver.find_element_by_xpath("//*[@id='search-results']").text
                    
                    #if no results again, skip to next candidate
                    if num_results=="No candidates found":
                        writer.writerow([i, start_time, docid, firstname, lastname, company, company_flag, latest_company, keywords, search_type, 0,"",""])
                        driver.find_element_by_xpath('//*[@id="clear-search"]').click()
                        success=True
                        print("                       NO RESULTS", search_type)
                        continue
                    #if more than 5 results, skip to next candidate
                    elif int(re.search("\\d+", num_results).group())>5:
                        writer.writerow([i, start_time, docid, firstname, lastname, company, company_flag, latest_company, keywords, search_type, int(re.search("\\d+", num_results).group()),"",""])
                        driver.find_element_by_xpath('//*[@id="clear-search"]').click()
                        success=True
                        print("                       >5 RESULTS", search_type)
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
                writer.writerow([i, start_time, docid, firstname, lastname, company, company_flag, latest_company, keywords, search_type, num_results, is_namematch, driver.current_url])
                time.sleep(random.uniform(1,2))
                driver.execute_script("window.scroll(0,1500)")
                time.sleep(random.uniform(8,12))
                content = driver.page_source.encode('utf-8').strip()
                with open(path_out + "/htmls/" + docid + "_career.html", "w") as f:
                    f.write(str(content))
                driver.execute_script("window.scroll(0,-1500)")
                time.sleep(random.uniform(1,2))
                
                #return to advanced search page
                driver.find_element_by_xpath('//*[@id="advanced-search"]').click()
                nobtn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="no-btn"]')))
                time.sleep(random.uniform(1,3))
                nobtn.click()
                print("                       ", num_results, search_type)
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
                time.sleep(random.uniform(4,8))
                driver.find_element_by_xpath('//*[@class="no-btn"]').click()
        assert success==True



