# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 18:26:06 2019

@author: Asser.Maamoun
"""


def find_obj(lst, obj):
    """
    Input: lst - a list of tuples or a single tuple
           obj - the obj to search for in the tuple's first entry
    Ouput: a list of all "obj" elements in the list. only looks at the
        depth=1 elements and the compares obj to each tuple's first entry.
    """
    obj_list = []
    if isinstance(lst, tuple):
        lst=[lst]
    if isinstance(obj, str):
        obj=[obj]
    for item in lst:
        if item[0] in obj:
            obj_list.append(item)
    return obj_list

def findall_obj(lst, obj):
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
#        print('lst:', lst, 'item:', item, "checking", item[0])
        if isinstance(item, str):
            continue
        elif item[0] == obj:
            obj_list.append(item)
        elif len(item)<2:
            print('list:', lst, 'item:', item)
            raise ValueError("findall_obj: Cannot Enter item's contents")
        else:
            item_child = findall_obj(item[1], obj)
            if len(item_child)>0:
                obj_list.extend(item_child)
    return obj_list

def flatten_pict(pict_contents):
    pict_flat=[]
    for item in pict_contents:
        if isinstance(item, tuple):
            #flatten
            item_tag = item[0]
            item_contents = item[1]        
            if (item_tag=='tbl'):
                pict_flat.extend([flatten_text(item_contents)])
            else:
                print("bad tuple:", item, "unknown tag:", item_tag)
                raise ValueError("Unknown imbedded tuple in pict")
        else:
            print("bad item:", item)
            raise ValueError("Unknown imbedded item in pict")
    if pict_flat == []:
        pict_flat = ""
    return pict_flat

def flatten_run(run_contents):
    """
    Input: a run tuple's contents
    Output: If the run only contains text, then return the text as concatenated string
        if the run also contains tables, return a list of parsed contents that 
        preserves the ordering of the run's text and tables.
    """
#    if isinstance(p_contents, str):
#        return [p_contents]
    r_flat = []
    for item in run_contents:
        #make sure to parse for both strings and tables!
        if isinstance(item, str):
            r_flat.append(item)
        elif isinstance(item, tuple):
            #flatten
            item_tag = item[0]
            item_contents = item[1]
            if item_tag=='pict':
                r_flat.append(flatten_pict(item_contents))
            else:
                print("bad tuple:", item, "unknown tag:", item_tag)
                raise ValueError("Unknown imbedded tuple in run")
        else:
            print("unknown run child:", item)
            raise ValueError("Unknown object in the run list")
    if len(r_flat)==1 & (isinstance(r_flat[0], str) | isinstance(r_flat[0], list)):
        r_flat = r_flat[0]
    return r_flat


def flatten_tag(smart_tuple):
    """
    Input: A smart tag as a tuple
    Output: A list of two elements. the first of which contains the alias and 
        the second of which contains the contents. If the content is exclusively
        paragraphs, then the paragraphs are concatenated. Else the content is
        appended as is.
    """
    smart_flat = []
    tag_name = smart_tuple[0]
    tag_contents = smart_tuple[1] #a tuple containing the tags contents

    curr_tag="tag start: "+tag_name
    smart_flat.append(curr_tag)
    if not isinstance(tag_contents, tuple):
        print("The bad smart_tuple:", smart_tuple)
        raise ValueError("Error: The content of a smart tag should be a tuple")
    elif tag_contents[0] != "lst":
        print("bad smart_tuple:", smart_tuple)
        raise ValueError("Tag contents should be in a list")
    else:
        tag_contents = tag_contents[1]
        tag_contents_flat = flatten_node_list(tag_contents)
        smart_flat.extend(tag_contents_flat)
    smart_flat.append("tag end: "+tag_name)
    return smart_flat
        

def flatten_p(p_contents):
    """
    Input: a paragraph tuple's contents
    Output: A list of the contents. concatenate all adjacent strings. if there
        is an inbedded smart_tag, create a new list item for the smart alias,
        and the flattened smart contents seperately before moving on to the
        rest of the paragraph. If there is a run node with only text, simply add
        it. If the run node also contains tables, then extend the list with
        the flattened run node.
    """
#    if isinstance(p_contents, str):
#        return [p_contents]
    p_flat = [""]
    last_ind = 0
    for item in p_contents:
        #if paragraph contains smart tags, flatten and add as new elements
        if isinstance(item, tuple):
            #flatten
            item_tag = item[0]
            item_contents = item[1]
            if item_tag=="r":
                run_flat = flatten_run(item_contents)
                if isinstance(run_flat,str):
                    p_flat[last_ind] += run_flat
                    continue
                else:
                    #if the last item is an empty string, remove it
                    if p_flat[last_ind]=="":
                        p_flat.pop(last_ind)
                    p_flat.extend(run_flat)           
            elif item_tag=="tag":
                #if the last item is an empty string, remove it
                if p_flat[last_ind]=="":
                    p_flat.pop(last_ind)
                tag_flat = flatten_tag(item_contents)
                p_flat.extend(tag_flat)
            elif (item_tag=='sdt') | (item_tag=='ins'):
                #if the last item is an empty string, remove it
                if p_flat[last_ind]=="":
                    p_flat.pop(last_ind)
                sdt_flat = flatten_content(item_contents)
                p_flat.extend(sdt_flat)
            else:
                print("bad tuple:", item, "unknown tag:", item_tag)
                raise ValueError("Unknown imbedded tuple in paragraph")
            #add an empty string to append future contents to
            p_flat.extend([""])
            last_ind = len(p_flat)-1
        else:
            print("unknown paragraph child:", item)
            raise ValueError("Unknown object in the paragraph list")
    #if the last item is an empty sting, drop it
    if (p_flat[last_ind]=="") & (len(p_flat)>1):
        p_flat.pop(last_ind)
    return p_flat

def flatten_node_list(node_list):
    list_flat = [""]
    last_ind=0
    for item in node_list:
        if isinstance(item, tuple):
            #flatten
            item_tag = item[0]
            item_contents = item[1]
            if item_tag=="r":
                run_flat = flatten_run(item_contents)
                if isinstance(run_flat,str):
                    list_flat[last_ind] += run_flat
                    continue
                else:
                    #if the last item is an empty string, remove it before adding extra elements
                    if list_flat[last_ind]=="":
                        list_flat.pop(last_ind)
                    list_flat.extend(run_flat)
            elif item_tag=="p":
                #if the last item is an empty string, remove it before adding extra elements
                if list_flat[last_ind]=="":
                    list_flat.pop(last_ind)
                p_flat = flatten_p(item_contents)
                list_flat.extend(p_flat) if p_flat!=[""] else ''
            elif item_tag=="tag":
                #if the last item is an empty string, remove it before adding extra elements
                if list_flat[last_ind]=="":
                    list_flat.pop(last_ind)
                tag_flat = flatten_tag(item_contents)
                list_flat.extend(tag_flat)
            elif item_tag=="sdt":
                #if the last item is an empty string, remove it before adding extra elements
                if list_flat[last_ind]=="":
                    list_flat.pop(last_ind)
                sdt_flat = flatten_content(item_contents)
                list_flat.extend(sdt_flat)
            elif (item_tag=='tc'):
                #if the last item is an empty string, remove it before adding extra elements
                if list_flat[last_ind]=="":
                    list_flat.pop(last_ind)
                tc_flat = flatten_cell(item_contents)
                list_flat.extend(tc_flat)
            elif (item_tag=='tbl'):
                #if the last item is an empty string, remove it before adding extra elements
                if list_flat[last_ind]=="":
                    list_flat.pop(last_ind)
                list_flat.extend([flatten_text(item_contents)])
 #               raise ValueError("table in a list!")
            else:
                print("unknown tuple in list:", item, "unknown tag:", item_tag)
                raise ValueError("Unknown tuple in list")
            #add an empty string to append future contents to
            list_flat.extend([""])
            last_ind = len(list_flat)-1
        else:
            print("list:", node_list, "unknown list child:", item)
            raise ValueError("Unknown object in the node list")
    if list_flat[last_ind]=="":
        list_flat.pop(last_ind)
    return list_flat

def flatten_content(tup):
    #flatten
    tup_tag = tup[0]
    tup_contents = tup[1]
    if tup_tag=="r":
        tup_contents = flatten_run(tup_contents)
    elif tup_tag=="p":
        tup_contents = flatten_p(tup_contents)
    elif tup_tag=="tag":
        tup_contents = flatten_tag(tup_contents)
    elif tup_tag=="lst":
        tup_contents=flatten_node_list(tup_contents)
    else:
        print("bad tuple:", tup, "unknown tag:", tup_tag)
        raise ValueError("Unknown tuple tag")
    return tup_contents

def flatten_cell(cell):
    cell_flat = []
    cell_type = cell[0]
    cell_contents = cell[1]
    if cell_type=='tag':
        smart_flat = flatten_tag(cell_contents)
        cell_flat.extend(smart_flat)
    elif cell_type=='lst':
        lst_flat = flatten_node_list(cell_contents)
        cell_flat.extend(lst_flat)
    elif cell_type=='sdt':
        sdt_flat = flatten_content(cell_contents)
        cell_flat.extend(sdt_flat)
    elif cell_type=='tbl':
        print("cell:", cell)
        cell_flat.extend([flatten_text(cell)])
#        raise ValueError("Table within in a Table")
    else:
        print("cell:", cell, "unknown type:", cell_type, "unknown cell item:", cell_contents)
        raise ValueError("Unknown cell item type " + cell_type)
    return "".join(cell_flat)
    

def flatten_tables(doc_list):
    """
    Returns a flattened version of the table. The tables are represented
    as a list of rows. each row is a list of cells. a smart tag will
    be split up into two cells, the first of which contains the alias and 
    the second of which contains the contents. If the content is a list of all
    paragraphs, then the paragraphs are concatenated. Else the content is
    appended as is.
    """
    tables = []
    raw_tables = findall_obj(doc_list, "tbl")
    if len(raw_tables)==0:
        print("Double-Check! No tables found!")
    for table in raw_tables:
        table_flat = []
        table_contents = table[1]
        for row in table_contents:
            row_flat = []
            if not isinstance(row, tuple):
                print("bad row item:", row)
                raise ValueError("row item is not a tuple")
            row_tag = row[0]
            row_contents = row[1]
            if row_tag not in ["tr", "sdt"]:
                print("bad row item:", row)
                raise ValueError("row item is not a row or sdt")
#            print('row: ', row_cells)
            for cell in row_contents:
#                print("cell: ", cell)
                cell_contents = cell[1]
                cell_flat = flatten_cell(cell_contents)
                row_flat.append(cell_flat)
            table_flat.append(row_flat)
        tables.append(table_flat)
    return tables

# =============================================================================
# 
# def flatten_toc(doc_list):
#     """
#     Returns a flattened version of the table. The tables are represented
#     as a list of rows. each row is a list of cells. a smart tag will
#     be split up into two cells, the first of which contains the alias and 
#     the second of which contains the contents. If the content is a list of all
#     paragraphs, then the paragraphs are concatenated. Else the content is
#     appended as is.
#     """
#     tocs = []
#     raw_toc = findall_obj(doc_list, "toc")
#     if len(raw_toc)==0:
#         print("Double-Check! No toc found!")
#     elif len(raw_toc)>1:
#         print("Double-Check! More than 1 toc found!")
#     for toc in raw_toc:
#         toc_flat = []
#         toc_contents = toc[1]
#         for row in toc_contents:
#             if not isinstance(row, list):
#                 print("bad toc item:", row)
#                 raise ValueError("row item is not a list")
#             toc_flat.append(row[0])
#         tocs.append(toc_flat)
#     return tocs
# =============================================================================

def flatten_text(doc_list):
    """
    Input: a python representation of a node with text within it
    Output: the text within the node as a concatenated string
    """
    text=""
    if not isinstance(doc_list, list):
        doc_list = [doc_list]
    for item in doc_list:
        if isinstance(item, tuple):
            text+=flatten_text(item[1])
        elif isinstance(item, list):
            text+=flatten_text(item)
        elif isinstance(item, str):
            text+=item
        else:
            print(item)
            raise ValueError("Unknown item to convert to text")
    return text





















