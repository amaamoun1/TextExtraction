# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 18:28:16 2019

@author: Asser.Maamoun
"""
from docx2python import parse_docx
from flatten_python import find_obj
from flatten_python import findall_obj
from flatten_python import flatten_tables
from flatten_python import flatten_text

class PythonDocx:
    
    def __init__(self, docx_path):
        self.master = parse_docx(docx_path)
        self.tables = self.table_no_tuple()
        self.paragraphs = self.findall("p")
        self.text = self.all_text(self)
        
    def find(self, obj):
        return find_obj(self.master, obj)
    
    def findall(self, obj):
        return findall_obj(self.master, obj)
        
    def table_no_tuple(self):
        return flatten_tables(self.master)
    
    def all_text(obj):
        text=flatten_text(obj)
        return text

