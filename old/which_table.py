# -*- coding: utf-8 -*-
"""
This function reads in a docx table and outputs the type of the table, i.e.
    if the table contains interview info or competencies.

To do:
    - Automatically detect which table version is being interpreted. 
        - This can only be done once we look at many documents, as the tables 
            might vary by document. This could be implemented by checking if 
            the table contains certin key words, or by trying to find the 
            header immediately prior to the table.
                - Front Page Info
                - ghSMART Competency Ratings 

Notes:
    - Merged Cells are read as multiple cells all with the same information
    - info on the docx package: https://python-docx.readthedocs.io/en/latest/index.html
    - info on the pandas package: https://pandas.pydata.org/
"""


from docx import Document
import pandas as pd

#comp_cat = ["intellectual ability", "personal effectiveness", 
#            "team leadership", "interpersonal effectiveness", 
#            "contextual skills/experience", "leadership competencies",
#            "personal competencies", "intellectual competencies",
#            "motivational competencies", "interpersonal competencies",
#            "technical/functional competencies"]
comp_cat_2019 = ["intellectual ability", "personal effectiveness", 
            "team leadership", "interpersonal effectiveness", 
            "contextual skills/experience"]

name_identifiers = ["Candidate Name", "Candidate", "Feedback Recipient"]
# loops through the table and decides what table it is based on if any of
# its cells contains certain strings. To add robustness, we could
# check if multiple cells fulfill certain criteria.

def which_table(table):
    table_name="other"
    num_comp = 0
    for row in table.rows:
        last_text = ""
        for cell in row.cells:
            curr_text = cell.text
            #Check 1: does the table give identifying information
            if curr_text.strip() in name_identifiers:
                table_name="info"
                break #stop looking through rest of table
                
            #Check 2: does the table give competency information
            #in non-2019, we can find 'competencies' in the first cell of table
            if "competencies" in curr_text.lower():
                table_name="competencies"
                break #stop looking through rest of the table
            #for the 2019 version, the clean identification is from merged cells with the competency type
            if curr_text.lower() in comp_cat_2019:
                #num_comp+=1 #keep track of the number of listed competencies
                if last_text=="":
                    last_text = curr_text
                else:
                    if last_text==curr_text: #a merged cell is interpreted as two cells with the same contents
                        num_comp+=1 #keep track of the number of listed competencies
                        if num_comp == 5: #if the table has identified all five competency categories
                            table_name = "competencies"
                            break #stop looking through rest of table
                    else:
                        last_text=curr_text #if not a merged cell, update last_text
            
    return table_name


###############################################################################
    # This is some scratch space for debugging and testing #
    
#%cd C:\Users\amaamoun\Desktop\Kaplan\TextExtraction

dummy_docs = {
        ".\DummyDocs\Cleaning_Small.docx" : {"info": 0, "competencies": 5},
        ".\DummyDocs\Cleaning_Small_Copy.docx" : {"info": 0, "competencies": 5},
        ".\DummyDocs\cleaning1_v2019.docx" : {"info": 0, "competencies": 5},
        ".\DummyDocs\cleaning2_v2012.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning3_v2015.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning4_namenotintable.docx" : {"info": None, "competencies": 1},
        ".\DummyDocs\cleaning5_feedback.docx" : {"info": 0, "competencies": None},
        ".\DummyDocs\cleaning6_v2012_nonamecell.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning7_v2015_competency_comments.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning8_v2015_long_comp_comments.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning9_v2008.docx" : {"info": 0, "competencies": 1},
        ".\DummyDocs\cleaning10_v2019_NoCompetencies.docx" : {"info": 0, "competencies": None},
        }

to_check = ["info", "competencies"]

incorrect_paths = {};
#check all the table types in to_check
for table_type in to_check:
    incorrect_paths[table_type]=[]
    #loop through all of the dummy documents
    for test_path in dummy_docs:
        #select the path and convert to a docx Document
        test_doc = Document(test_path)
        test_doc_name = test_path.replace('.\\DummyDocs\\', '')
        #find the location of the table_type in the document and load table
        table_loc = dummy_docs[test_path][table_type]
        if table_loc==None:
            continue
        test_table = test_doc.tables[table_loc]
        
        #checks the output of which_table for table_type in test_path
        identified_as = which_table(test_table)
        
        #if incorrectly identified, print the structure of the tables
        if identified_as != table_type:
            print(test_doc_name, table_type, "identified as", identified_as)
            incorrect_paths[table_type].append(test_path)
            for row in test_table.rows: #loop through all table rows
                text = (cell.text for cell in row.cells)
                text = tuple(text)
                print(text)
        #if correctly identified, print the notification
        else:
            print("correct id of", test_doc_name, table_type, ":", table_type)













