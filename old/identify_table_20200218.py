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


#comp_cat = ["intellectual ability", "personal effectiveness", 
#            "team leadership", "interpersonal effectiveness", 
#            "contextual skills/experience", "leadership competencies",
#            "personal competencies", "intellectual competencies",
#            "motivational competencies", "interpersonal competencies",
#            "technical/functional competencies"]
#comp_cat_2019 = ["intellectual ability", "personal effectiveness", 
#            "team leadership", "interpersonal effectiveness", 
#            "contextual skills/experience"]

name_identifiers = ["Candidate Name", "Candidate", "Feedback Recipient",
                    "Leader Name", "Executive Name", "Prepared For", "Prepared By",
                    "Purpose of This Assessment", "Purpose of This Feedback Process",
                    "Executive Assessment", "Smart Assessment®", "SmartAssessment®",
                    "SmartFeedback® Report", "SmartFeedback®",
                    "Developmental Assessment", "SmartAssessment",
                    "SmartAssessment® Report", "Developmental Report",
                    "Executive Report", 
                    "SmartAssessment Report", "Executive Assessment Report", 
                    "Smart Assessment® Report", "Developmental Assessment Report",
                    ]

comp_dict={"flexible/adaptable":"adaptable",
           "ambitious for greater impact":"ambitious",
           "analytical":"analysis", "analysis":"analysis",
           "aggressive":"aggressive",
           "assertive":"assertive",
           "balanced in judgment": "balanced decisions",
           "builds relationships": "builds relationships", 
           "calm under pressure":"calm", "self-controlled/composed":"calm",
           "creative/innovative": "creative",
           "decisive":"decisive",
           "delegates":"delegates",
           "attention to detail": "detail", "detail oriented":"detail",
           "develops people": "develops people",
           "driven to achieve":"driven", 
           "efficiency of execution":"efficiency", "executes efficiently":"efficiency",
           "understands others/empathizes":"empathizes",
           "finance":"financial", "financially savvy":"financial",
           "focused":"focused",
           "sets high standards":"high standards",
           "hires a players": "hires a players",
           "holds people accountable": "holds people accountable",
           "human resources": "human resources",
           "industry knowledge":"industry knowledge", "knowledge of the industry": "industry knowledge", "knows the industry":"industry knowledge",
           "information technology":"information technology",
           "honest/has integrity": "integrity", "integrity/honesty":"integrity",
           "brainpower/learns quickly":"intelligent", "intelligent":"intelligent",
           "learning oriented":"learning oriented",
           "listening":"listening", "listens effectively": "listening",
           "manages execution (tracks/metrics)":"manages execution",
           "marketing":"marketing",
           "enthusiasm/ability to motivate others": "motivational", "motivates/inspires":"motivational",
           "moves fast": "moves fast",
           "navigates organizations/politics": "navigates politics",
           "network of talented people":"network",
           "open to criticism and others' ideas": "open to criticism", "open to feedback/ideas":"open to criticism",
           "operations":"operations",
           "organization and planning":"organization", "organizes/plans":"organization",
           "persistent":"persistent",
           "persuades/influences":"persuasion", "persuasion":"persuasion", 
           "proactive": "proactive", "proactivity/takes initiative":"proactive", 
           "follows through on commitments":"reliable",
           "removes underperformers":"removes underperformers",
           "resourceful":"resourceful",
           "treats people with respect":"respects others", "respects others":"respects others",
           "sales":"sales", 
           "sales and marketing":"sales and marketing", "commercial":"sales and marketing",
           "self-aware": "self aware",
           "self-confident":"self confident",
           "strategic": "strategic", "strategic thinking/visioning": "strategic",
           "takes on challenges/risks":"takes on challenges",
           "teams/collaborates":"teamwork", "teamwork":"teamwork",
           "tenacious":"tenacious",
           "work ethic": "work ethic", "hard working": "work ethic",
           "oral communication":"verbal communication", "verbal communication":"verbal communication", "speaks effectively":"verbal communication",
           "written communications":"written communication"
           }
header_list=[ #"competencies", "competencies rating and comments", 
             "contextual/experience", "intellectual", "intellectual ability",
             "intellectual competencies", "interpersonal", "interpersonal competencies",
             "interpersonal effectiveness", "leadership", "leadership competencies", "motivational",
             "motivationl competencies", "personal competencies", "personal", "personal effectiveness",
             "self-management competencies", "team leadership", "technical/functional",
             "technical/functional competencies", "motivational competencies"
             ]
header_list=[]
# loops through the table and decides what table it is based on if any of
# its cells contains certain strings. To add robustness, we could
# check if multiple cells fulfill certain criteria.

def which_table(table, last_table):
    table_name="other"
    num_comp = 0
    for row in table:
#        last_text = ""
        for cell in row:
            #Check 1: does the table give identifying information
            if cell.strip() in name_identifiers:
                return "info"
                
            #Check 2: does the table give competency information
            #in non-2019, we can find 'competencies' in the first cell of table
            if (cell.lower().strip() in header_list) | \
                (cell.lower().strip() in comp_dict.keys()):
                num_comp+=1 #keep track of the number of listed competencies
                if (last_table=="competencies") & (num_comp==2):
                    return "competencies"
                if num_comp == 5: #if the table has identified all five competency categories
                    return "competencies"
                
#            #for the 2019 version, the clean identification is from merged cells with the competency type
#            if cell.lower() in comp_cat_2019:
#                #num_comp+=1 #keep track of the number of listed competencies
#                if last_text=="":
#                    last_text = cell
#                else:
#                    if last_text==cell: #a merged cell is interpreted as two cells with the same contents
#                        num_comp+=1 #keep track of the number of listed competencies
#                        if num_comp == 5: #if the table has identified all five competency categories
#                            table_name = "competencies"
#                            break #stop looking through rest of table
#                    else:
#                        last_text=cell #if not a merged cell, update last_text
            
    return table_name


###############################################################################
    # This is some scratch space for debugging and testing #
    
#%cd C:\Users\amaamoun\Desktop\Kaplan\TextExtraction
#
#dummy_docs = {
#        ".\DummyDocs\Cleaning_Small.docx" : {"info": 0, "competencies": 5},
#        ".\DummyDocs\Cleaning_Small_Copy.docx" : {"info": 0, "competencies": 5},
#        ".\DummyDocs\cleaning1_v2019.docx" : {"info": 0, "competencies": 5},
#        ".\DummyDocs\cleaning2_v2012.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning3_v2015.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning4_namenotintable.docx" : {"info": None, "competencies": 1},
#        ".\DummyDocs\cleaning5_feedback.docx" : {"info": 0, "competencies": None},
#        ".\DummyDocs\cleaning6_v2012_nonamecell.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning7_v2015_competency_comments.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning8_v2015_long_comp_comments.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning9_v2008.docx" : {"info": 0, "competencies": 1},
#        ".\DummyDocs\cleaning10_v2019_NoCompetencies.docx" : {"info": 0, "competencies": None},
#        }
#
#to_check = ["info", "competencies"]
#
#incorrect_paths = {};
##check all the table types in to_check
#for table_type in to_check:
#    incorrect_paths[table_type]=[]
#    #loop through all of the dummy documents
#    for test_path in dummy_docs:
#        #select the path and convert to a docx Document
#        test_doc = Document(test_path)
#        test_doc_name = test_path.replace('.\\DummyDocs\\', '')
#        #find the location of the table_type in the document and load table
#        table_loc = dummy_docs[test_path][table_type]
#        if table_loc==None:
#            continue
#        test_table = test_doc.tables[table_loc]
#        
#        #checks the output of which_table for table_type in test_path
#        identified_as = which_table(test_table)
#        
#        #if incorrectly identified, print the structure of the tables
#        if identified_as != table_type:
#            print(test_doc_name, table_type, "identified as", identified_as)
#            incorrect_paths[table_type].append(test_path)
#            for row in test_table.rows: #loop through all table rows
#                text = (cell.text for cell in row.cells)
#                text = tuple(text)
#                print(text)
#        #if correctly identified, print the notification
#        else:
#            print("correct id of", test_doc_name, table_type, ":", table_type)
#
#
#
#
#
#
#
#
#
#
#
#
#
