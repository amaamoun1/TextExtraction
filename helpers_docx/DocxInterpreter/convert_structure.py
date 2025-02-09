# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 23:09:35 2019

@author: Asser.Maamoun
@description: 
    To read in tables and text from word documents into python while keeping
    their order and general structure. This will be accomplished by taking
    advantage of the xml structure of word documents. The current goal is to
    convert only the body of the document, not the header or footer, but the
    code should be generalizable to include headers and footers as well.
    
    While the python-docx package converts word documents to tables
    and paragraphs, the package does not pick up these elements if they are not
    located in the outtermost level of xml nodes. Additionally, the package
    does not readily read smart tags and table of contents. In contrast, the 
    python-docx2txt package can readily convert and combine all word text
    elements into one python string, however it gets rid of the table structures
    of the document and also does not pick up on the smart tag tags.
    
    I borrow from python-docx2txt to create the basic logic of my code.
"""


#! /usr/bin/env python

import xml.etree.ElementTree as ET
import zipfile
import re


nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
         'm': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
         'w10': 'http://schemas.microsoft.com/office/word/2010/wordml',
         'v': 'urn:schemas-microsoft-com:vml',
         'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'}


def qn(tag):
    """
    Stands for 'qualified name', a utility function to turn a namespace
    prefixed tag name into a Clark-notation qualified tag name for lxml. For
    example, ``qn('p:cSld')`` returns ``'{http://schemas.../main}cSld'``.
    Source: https://github.com/python-openxml/python-docx/
    """
    prefix, tagroot = tag.split(':')
    uri = nsmap[prefix]
    return '{{{}}}{}'.format(uri, tagroot)

#These are node types that are present in the document that we actively do not
#try to parse. Some of them will be useful int he future, such as the bookmarks,
#sections, hyperlinks(for TOC).
do_not_parse = [qn('w:br'), qn('w:cr'), qn('w:pPr'), qn('w:proofErr'), 
                qn('w:tcPr'), qn('w:rPr'), qn('w:lastRenderedPageBreak'), 
                qn('w:drawing'), qn('w:trPr'), qn('m:AlternateContent'),
                qn('w:bookmarkStart'), qn('w:bookmarkEnd'), qn('w:fldChar'),
                qn('w:instrText'), qn('w:sectPr'), qn('w:hyperlink'),
                qn('w:tblPr'), qn('w:tblGrid'), qn('w:pict'), qn('w:footnoteReference'),
                qn('w:tblPrEx'), qn('w:commentReference'), qn('w:commentRangeStart'),
                qn('w:commentRangeEnd'), qn('w:del'), qn('w:softHyphen'), qn('w:sym'),
                qn('w:noBreakHyphen'), qn('w:pgNum'), qn('w:smartTagPr'),
                qn('w:moveFrom'), qn('w:moveTo'), qn('w:moveFromRangeStart'),
                qn('w:moveToRangeStart'), qn('w:moveFromRangeEnd'), 
                qn('w:moveToRangeEnd'), qn('w10:conflictDel'), qn('w10:conflictIns')]


def process_node_text(node):
    """
    INPUT: a node with text within it
    OUTPUT: the text within the node, as a concatenated string, including tabs,
        and line breaks elements
    """
    node_text = ""
    for child_node in node.iter():
        if child_node.tag == qn('w:t'): #text nodes
            t_text = child_node.text
            node_text += t_text if t_text is not None else ''
        elif child_node.tag == qn('w:tab'):
            node_text += '\t'
        elif child_node.tag in (qn('w:br'), qn('w:cr')):
            node_text += '\n'
    return node_text

def add_to_dict(to_add, dic):
    """
    A utility function for a dictionary of counts
    INPUT: dic - a dictionary
           to_add - an item to keep track off
    OUTPUT: the same dictionary, but if to_add was not yet in the dic, then
            add it with val=1, else add 1 to its value
    """
    if to_add in dic:
        dic[to_add] += 1
    else:
        dic[to_add] = 1
    return

def process_nestedTables(pict_node, unknown_elements):
    """
    INPUT: a node from which to extract tables
    OUTPUT: a list of the parsed tables, constructed by parsing every table
        node in the picture node iterator
    """
    pict_list = []
    tbls_iter = list(pict_node.iter(qn('w:tbl')))
    for tbl_node in tbls_iter:
        tbl_list = process_table(tbl_node, unknown_elements)
        pict_list.append(tbl_list)
#    print(pict_list)
    return ('pict', pict_list)

def process_run(run_node, unknown_elements):
    """
    INPUT: a run node to extract text from
    OUTPUT: the text within the node, as a concatenated string
    Works similar to process_node_text but also checks the types of items that 
    are contained in the run_node
    """
    node_text = [""]
    for child_node in run_node:
        if child_node.tag == qn('w:t'):
            t_text = child_node.text
            node_text[-1] += t_text if t_text is not None else ''
        elif child_node.tag == qn('w:tab'):
            node_text[-1] += '\t'
        elif child_node.tag in (qn('w:br'), qn('w:cr')):
            node_text[-1] += '\n'
        elif child_node.tag == qn('w:pict') or child_node.tag == qn('mc:AlternateContent'):
            tables = process_nestedTables(child_node, unknown_elements)
            if node_text[-1]=="":
                node_text[-1]=tables
            else:
                node_text.extend([tables, ""])
#            print(node_text)
        elif child_node.tag in do_not_parse:
            continue
        else:
            print("unknown r child:", child_node.tag)
            to_add = "r:" + child_node.tag
            add_to_dict(to_add, unknown_elements)
#            raise ValueError("Unknown child in run Node")
    if (len(node_text)>1) & (node_text[-1]==""):
        node_text=node_text[:-1]
    return ('r', node_text)    


def process_paragraph(par_node, unknown_elements):
    """
    INPUT: a node with tag "w:p" to extract all text from
    OUTPUT: the text within the node, as a list. If no smart tag exists within
        the paragraph, a list with a single concatenated string is returned.
        Else, the list first contains the text before the smart tag, then the 
        smart tag alias and the imbedded text as a nested list, then the text
        following the smart tag contents. This can happen repeatedly and 
        recursively, as this calls process_sdt_node, which in turn calls on 
        process_paragraphs.
    """
    par_list = []
    for child_node in par_node:
        if child_node.tag == qn('w:r'):
            run_content = process_run(child_node, unknown_elements)
            par_list.append(run_content)
        elif child_node.tag == qn('w:sdt'):
            child_list = process_sdt_node(child_node, unknown_elements)
            par_list.append(child_list)
        elif child_node.tag == qn('w:smartTag'):
            smart_contents = process_smarttag(child_node, unknown_elements)
            par_list.append(smart_contents)
        elif child_node.tag == qn('w:ins'):
            content = process_node_list(child_node, unknown_elements)
            tup = ('ins', content)
            par_list.append(tup)
        elif child_node.tag not in do_not_parse:
            print("unknown p child:", child_node.tag)
            to_add = "p:" + child_node.tag
            add_to_dict(to_add, unknown_elements)
            #raise ValueError("Unknown child in run Node")
    #strip leading and trailing whitespace
    i=0
    while i < len(par_list):
        item = par_list[i]
        if isinstance(item, str):
            par_list[i] = item.strip()
        i+=1
    return ('p', par_list)


def process_smarttag(smart_node, unknown_elements):
    tag = smart_node.get(qn('w:element'))
    content = process_node_list(smart_node, unknown_elements)
    if tag is not None:
        content = (tag, content) 
    else:
        print(smart_node.attrib)
        raise ValueError("Check for smart tags without an w:element attr!")
    return ('tag', content)

def process_toc(root_node):
    toc = []
    toc_pghs = []
    pghs = root_node.iter(qn('w:p'))
    for p in pghs:
        prop_node = p.find(qn('w:pPr'))
        if prop_node!=None:
            style_node = prop_node.find(qn('w:pStyle'))
            if style_node==None:
                continue
            style = style_node.get(qn('w:val'))
            if "toc" in style.lower():
                toc_pghs.append(p)
    for pgh in toc_pghs:
        text = process_node_text(pgh)
        clean = re.sub('^[^a-zA-Z]*', '', text)
        clean = clean.strip()
        page_number = re.sub('[^\d]*', '', clean)
        page_content = re.sub('[^a-zA-Z]*$', '', clean)
        toc.append([page_content, page_number])
    return toc

def process_sdt_node(sdt_node, unknown_elements):
    """
    INPUT: a node with tag "w:sdt" to extract all text from with alias
    OUTPUT: the text within the node, as a list of content alias followed
        by an entry per paragraph
    """
    #for all immediate content nodes, grab the text within paragraphs/runs
    content_nodes = sdt_node.findall(qn('w:sdtContent'))
    if len(content_nodes)>1:
        raise ValueError("More than one content nodes")
    elif content_nodes is None:
        raise ValueError("No content nodes")
    else:
        content_node = content_nodes[0]
        content = process_node_list(content_node, unknown_elements)
#        print("node_list:", content_node_list)
        
    #If an alias exists, find it, and assign the text to the alias
    content_properties = sdt_node.findall(qn('w:sdtPr'))
    if len(content_properties)>1:
        raise ValueError("More than one property nodes")
    elif content_properties is None:
        raise ValueError("No property nodes")
    else:
        prop_node = content_properties[0]
        smart_node = prop_node.find(qn('w:tag'))
        if smart_node is not None:
            tag = smart_node.get(qn('w:val'))
            content = ("tag", (tag, content))
    return ('sdt', content)

def process_node_list(root_node, unknown_elements):
    """
    INPUT: root_node - any node from which we want to extract child text from child
               paragraphs and child stdcontent nodes
    OUTPUT: the text within the node, as a list of content
    """
    root_list = []
    for child_node in root_node:
        if child_node.tag == qn('w:r'):
            run_content = process_run(child_node, unknown_elements)
            root_list.append(run_content)
        elif child_node.tag == qn('w:p'):
            p_text = process_paragraph(child_node, unknown_elements)
            if p_text[1]=="":
                continue
#                print("EMPTY PARAGRAPH")
            else:
                root_list.append(p_text)
        elif child_node.tag == qn('w:sdt'):
            child_list = process_sdt_node(child_node, unknown_elements)
            root_list.append(child_list)
        elif child_node.tag == qn('w:tc'):
            cell_contents = process_node_list(child_node, unknown_elements)
            root_list.append(('tc', cell_contents))
        elif child_node.tag == qn('w:tbl'):
            contents = process_table(child_node, unknown_elements)
            root_list.append(contents)
        elif child_node.tag == qn('w:smartTag'):
            contents = process_smarttag(child_node, unknown_elements)
            root_list.append(contents)
        elif child_node.tag not in do_not_parse:
            print("unknown root child:", child_node.tag)
            to_add = "sdt:" + child_node.tag
            add_to_dict(to_add, unknown_elements)
#            print("Root child:", child.tag)
    return ('lst', root_list)     
    
    
def process_table(table_node, unknown_elements):
    """
    INPUT: a table node
    OUTPUT: a list representation of the table. Each table row is a list of
        table cells. In the future, one could add funcitonality to adjust for 
        merged cells. cell
    """
    table_list = []
    for child in table_node:
        child_tag = child.tag
        if child_tag == qn('w:tr'):
            row_list = []
            for row_child in child:
                if row_child.tag == qn('w:tc'):
                    cell_contents = process_node_list(row_child, unknown_elements)
                    row_list.append(('tc', cell_contents))
                elif row_child.tag == qn('w:sdt'):
                    cell_contents = process_sdt_node(row_child, unknown_elements)
                    row_list.append(cell_contents)
                elif row_child.tag not in do_not_parse:
                    print("Unknown cell level entry:", row_child.tag)
                    to_add = "c:" + row_child.tag
                    add_to_dict(to_add, unknown_elements)
            table_list.append(('tr', row_list))
        else:
            if child_tag not in do_not_parse:
                print("Unknown table row level entry:", child_tag)
                to_add = "row:" + child_tag
                add_to_dict(to_add, unknown_elements)
    return ('tbl', table_list)


def open_body(docx_path):
    """
    INPUT: path to a docx file
    OUTPUT: string version of the xml content of the file's body
    """
    zipf = zipfile.ZipFile(docx_path)
    docx_xml = 'word/document.xml'
    docx_str = zipf.read(docx_xml)
    return docx_str


def convert_xml(docx_str):
    """
    INPUT:  docx_str - string version of the xml content of a word file
    OUTPUT: list of contents of the file, keeping only elements in search_for
        nested search_for elements are not treated as seperate elements
        but nested tables or nested smart tags are returned as errors
        a smart tag within a table is parsed as two merged cells, with the 
            first cell being the alias and second being the content
    """
    contents = []
    unknown_elements = {}
    #set the root to be the body
    root = ET.fromstring(docx_str).find(qn('w:body'))
    #grab the contents
    contents = process_node_list(root, unknown_elements)
    toc = process_toc(root)
    #delete empty nodes
#    contents = list(filter(None, contents[1]))
    return contents, toc, unknown_elements


def convert_docx(docx_path):
    docx_str=open_body(docx_path)
    return convert_xml(docx_str)


