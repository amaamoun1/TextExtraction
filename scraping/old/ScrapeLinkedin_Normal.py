import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import unicodedata
import numpy as np
import re
import datetime
import random

#only search for the schools that we want to search for
def reduce_schools(text):
    clean = re.sub("^ba  mba", "mba", text)
    clean = re.sub("\\bmba  all", "all", clean)
    clean = re.sub("\\ball $", "", clean)
    if re.search("^(ba|mba)", clean):
        clean = re.sub("\\ball.*", "", clean)
    return clean.strip()

def school_only(text):
    clean = re.sub("\\bba\\b", "", text)
    clean = re.sub("\\bmba\\b", "", clean)
    clean = re.sub("\\s+", " ", clean)
    return clean.strip()

def pre_2012(text):
    if pd.isnull(text):
        return 1
    if int(text[:4]) < 2012:
        return 1
    return 0
    
#read in extractions
read = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")

#select post 2012
read['pre2012'] = read['date_clean'].apply(pre_2012)
read = read[read['pre2012']==0]

#only search relevant people, no duplicates!
read_df = pd.DataFrame(read)
read_df = read_df.replace(np.nan, '', regex=True)
read_df = read_df[read_df['is_duplicate']==0]
read_df = read_df[read_df['candidate_flag']!=1]
del read

#set up variables for scraping loop
read_df = read_df[["doc_id_old", "doc_id_new", "candidate_firstname", "candidate_lastname", "undergrad_clean", "mba_clean", "college_raw", "college_potential"]]
read_df['doc_id_full'] = "oldid_" + read_df['doc_id_old'].astype(str) + "_newid_" + read_df['doc_id_new'].astype(str)
read_df['schools'] = "ba " + read_df['undergrad_clean'] + " mba " + read_df['mba_clean'] + " all " + read_df['college_raw']
read_df['schools'] = read_df['schools'].apply(reduce_schools)
read_df['schools_linkedin'] = read_df['schools'].apply(school_only)
read_df['combined'] = read_df['candidate_firstname']+ ' ' + read_df['candidate_lastname'] + ' ' + \
    read_df['schools_linkedin']
read_df = read_df.reset_index(drop=True)

#login info
usrName = "yanndecressin@gmail.com"
pssWrd = "Ywbiwi1997"
url = 'https://www.linkedin.com'

#open chrome
driver = webdriver.Chrome(executable_path='/Users/Asser.Maamoun/Downloads/chromedriver')
driver.maximize_window()
time.sleep(10)

#navigate to linkedin 
driver.get(url)
time.sleep(10)

#login
driver.find_element_by_class_name('nav__button-secondary ').click()
time.sleep(5)
driver.find_element_by_name('session_key').send_keys(usrName)
driver.find_element_by_name('session_password').send_keys(pssWrd)
driver.find_element_by_class_name('login__form_action_container ').click()
time.sleep(20)

#search
results = []
for i in range(100):
    
    #grab information on new candidate
    time.sleep(random.uniform(8,12))
    docid = read_df['doc_id_full'][i]
    to_search = read_df['combined'][i]
    start_time = datetime.datetime.now().strftime('%H:%M:%S')
    print(i, docid, start_time)

    #searches the name and school
    driver.find_element_by_class_name('global-nav__search').click()
    time.sleep(random.uniform(2,3))
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/*/input').send_keys(to_search)
    time.sleep(random.uniform(2,3))
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/*/input').send_keys(Keys.ENTER)
    time.sleep(random.uniform(5,6))
    driver.find_element_by_xpath('//*[@aria-label="People"]').click()
    time.sleep(random.uniform(4,6))
    
    #checks if any results occur and tracks number of results
    num_results = driver.find_element_by_xpath("//*[@class='search-results-page core-rail']").text
    if re.search("^No results", num_results):
        results.append([docid, to_search, 0])
        continue
    num_results = re.sub(" results?\\n.*", "", num_results, flags=re.DOTALL)
    num_results = re.sub("About ", "", num_results)
    num_results = re.sub(",", "", num_results)
    num_results = int(num_results)
    curr_results = [docid, to_search, num_results]

    #click on first result and save url
    driver.find_element_by_xpath("//*[@class='search-results-page core-rail']//*[@class='entity-result__image']").click()
    time.sleep(random.uniform(5,6))
    curr_results.append(driver.current_url)

    #scrolls down and clicks on all of the show more buttons if applicable
    driver.execute_script("window.scroll(0,1000)")
    time.sleep(random.uniform(2,6))
    try:
        test = driver.find_elements_by_class_name('pv-profile-section__toggle-detail-icon')
        for detail in test:
            detail.click()
            print("-----------CLICKED SEE MORE TAB-----------------")
    except IndexError:
        pass

    #grabs page source and save
    content = driver.page_source.encode('utf-8').strip()
    with open("C:/Users/Asser.Maamoun/Documents/htmls/" + docid + ".html", "w") as f:
        f.write(str(content))
    soup = BeautifulSoup(content, 'html.parser')
    
    #extracts name
    name = soup.find('li', class_="inline t-24 t-black t-normal break-words").text.strip()
    curr_results.append(name)
    
    #extracts experiences and education
    experiences = soup.find_all('li', class_="pv-entity__position-group-pager pv-profile-section__list-item ember-view")
    education = soup.find_all('li', class_="pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view")
    for item in experiences + education:
        curr_results.append(unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore'))

    results.append(curr_results)

driver.quit()

results_df = pd.DataFrame(results)
results_df.to_excel('/Users/Asser.Maamoun/Documents/scraping_results.xlsx', index=False)
