# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 18:23:26 2019

@author: Asser.Maamoun
"""


from convert_structure import convert_docx
from flatten_structure import flatten_tables
from flatten_structure import findall_obj
import random
import os
#import traceback


#################### Testing #############################
#
#test_path = 'C:/Users/Asser.Maamoun/Documents/Interviews/120509 Glenn Goldberg SF draft v1.docx'
##test_path = 'C:/Users/Asser.Maamoun/Documents/Interviews/EH Sr. Dir Prov Net Mgnt Michael Lynch Final Report (2).docx'
#
#test_contents = parse_docx(test_path)
#print("parsed xml")
#test_tables = flatten_tables(test_contents)
#print("flattened tables")


#############################################################################
#        Get a list of all the interview documents 
#############################################################################

#check the interview folder and the folder with doc converted to docx
interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Interviews"
converted_folder_path = "C:/Users/Asser.Maamoun/Documents/ConvertedInterviews"
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]
converted_docs = [os.path.join(converted_folder_path, f) for f in os.listdir(converted_folder_path) if os.path.isfile(os.path.join(converted_folder_path, f))]
all_docs = interview_docs + converted_docs

#keep a seperate list for just the docx files
doc_paths = []
docx_paths = []
for doc_id in range(len(all_docs)):
    #first read in the given document
    name = all_docs[doc_id]
    if "~$" in name:
        continue
    elif (".docx" not in name) and (".DOCX" not in name):
        doc_paths.append(name)
    else:
        docx_paths.append(name)
print("Total documents not in docx:", len(doc_paths))
print("Total documents in docx:", len(docx_paths))

del interview_folder_path, converted_folder_path, interview_docs, converted_docs, all_docs
del doc_paths, doc_id, name

#############################################################################
#        Test on subsets 
#############################################################################


#parse the xmls
#docx_to_parse = random.sample(docx_paths, 100)
#start=100
#end=200
#docx_to_parse = docx_paths[start:end]
docx_to_parse = docx_paths
contents=[]
unknown_count={}
unknown_contents=[]
i=0
while i < len(docx_to_parse):
    test_path=docx_to_parse[i]
    print('doc_id:', i, 'path', test_path)
    content, unknown = parse_docx(test_path)
    contents.append(content)
    if bool(unknown):
        unknown_contents.append((test_path, unknown))
        for item in unknown:
            if item not in unknown_count:
                unknown_count[item] = unknown[item]
            else:
                unknown_count[item] += unknown[item]
    i+=1
del unknown, i, content


test_tables=[]
#contents_to_parse = random.sample(contents, 100)
err_ind = []
err_inst = []
err_paths = []
i=0
while i < len(contents):
    print("working on doc_id:", i)
    content = contents[i]
    try:
        tables = flatten_tables(content)
    except ValueError as err:
        err_ind.append(i)
        err_inst.append(err)
        err_paths.append(docx_to_parse(i))
        print(err)
    except IndexError as err:
        err_ind.append(i)
        err_inst.append(err)
        err_paths.append(docx_to_parse(i))
        print(err)
    test_tables.append(tables)
    i+=1
del i, tables, content

#############################################################################
#        Retest on those contents that errored in table 
#############################################################################


i = 0
while i < len(err_ind):
    err = err_inst[i]
    ind = err_ind[i]
    print("\n", "working on doc_id:", ind)
    print("doc_path:", docx_paths[ind])
    content = contents[ind]
    print(err_inst[i])
    try:
        tables = flatten_tables(content)
    except ValueError as err:
        print("caught:", err)
    i+=1
    

curr_content = contents[0]
found_tables = findall_obj(curr_content, 'tbl')



#############################################################################
#        Inspecting the tables within tables
#############################################################################

def check_for_obj(lst, obj, seen=""):
    """
    Input: lst - a list of tuples or a single tuple
           obj - the obj to search for in the tuple's first entry
    Ouput: a list of all "obj" elements in the list. recursively looks at all
        depths and the compares obj to each tuple's first entry.
    """
    obj_list = []
    if isinstance(lst, tuple):
        lst=[lst]
    for item in lst:
        if isinstance(item, str):
            continue
        elif item[0] == obj:
            obj_list.append((seen + "\tbl.", item))
        elif len(item)<2:
            print('list:', lst, 'item:', item)
            raise ValueError("findall_obj: Cannot Enter item's contents")
        else:
            result = check_for_obj(item[1], obj, seen + "\\" + item[0])
            item_child = result[0]
            if len(item_child)>0:
                obj_list.extend(item_child)
    return obj_list, seen

def check_all_tables(path):
    print(path)
    content, unknown = parse_docx(test_path)
    tables = findall_obj(content, "tbl")
    i=0
    for table in tables:
        result = check_for_obj(table[1], "tbl")
        if result[0] != []:
            print("Table ID", i)
            print(result)
        i+=1
        
check_all_tables(err_paths[0])
        
for path in err_paths:
    print("\n")
    check_all_tables(path)
    


#############################################################################
#        Retest on specific files by file name
#############################################################################


result_ind=[]
result_path=[]
result_content=[]
tables=[]
result_table=[]
for i in range(len(docx_paths)):
    if "Catapult_President Education_SA_Jeff Wheatley_vF" in docx_paths[i]:
        result_ind.append(i)
        test_path = docx_paths[i]
        content, unknown = parse_docx(test_path)
        result_content.append(content)
        result_path.append(docx_paths[i])
        tables.append(findall_obj(content, 'tbl'))
        result_table.append(flatten_tables(content))


def check_for_table(lst, obj, seen=""):
    """
    Input: lst - a list of tuples or a single tuple
           obj - the obj to search for in the tuple's first entry
    Ouput: a list of all "obj" elements in the list. recursively looks at all
        depths and the compares obj to each tuple's first entry.
    """
    obj_list = []
    if isinstance(lst, tuple):
        lst=[lst]
    for item in lst:
        if isinstance(item, str):
            continue
        elif item[0] == obj:
            obj_list.append((seen + "\tbl.", item))
        elif len(item)<2:
            print('list:', lst, 'item:', item)
            raise ValueError("findall_obj: Cannot Enter item's contents")
        else:
            result = check_for_table(item[1], obj, seen + "\\" + item[0])
            item_child = result[0]
            if len(item_child)>0:
                obj_list.extend(item_child)
    return obj_list, seen



i=0
for table in tables[0]:
    print("Table ID", i)
    result = check_for_table(table[1], "tbl")
    if result[0] != []:
        print(result)
    i+=1
    
    
    
