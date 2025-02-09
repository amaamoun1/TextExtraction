# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 20:22:30 2020

@author: Asser.Maamoun
"""
import zipfile
import xml.etree.ElementTree as ET
import re


#heavily taken from docx2txt package

nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
         'm': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
         'w10': 'http://schemas.microsoft.com/office/word/2010/wordml',
         'v': 'urn:schemas-microsoft-com:vml'}


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


def process_node_text(node):
    text = ""
    for child in node.iter():
        if child.tag == qn('w:t'):
            text += child.text if child.text is not None else ''
        elif child.tag == qn('w:tab'):
            text += '\t'
        elif child.tag in (qn('w:br'), qn('w:cr')):
            text += '\n'
        elif child.tag == qn('w:p'):
            text += '\n\n'
    return text

def open_body(docx_path):
    """
    INPUT: path to a docx file
    OUTPUT: string version of the xml content of the file's body
    """
    zipf = zipfile.ZipFile(docx_path)
    docx_xml = 'word/document.xml'
    docx_str = zipf.read(docx_xml)
    return docx_str

def xml2string(docx_str):
    """
    INPUT:  docx_str - string version of the xml content of a word file
    OUTPUT: list of contents of the file, keeping only elements in search_for
        nested search_for elements are not treated as seperate elements
        but nested tables or nested smart tags are returned as errors
        a smart tag within a table is parsed as two merged cells, with the 
            first cell being the alias and second being the content
    """
    #set the root to be the body
    root = ET.fromstring(docx_str).find(qn('w:body'))
    #grab the text
    text = process_node_text(root)
    return text


def docx2string(docx_path):
    docx_str=open_body(docx_path)
    return xml2string(docx_str)
