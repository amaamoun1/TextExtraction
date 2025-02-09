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

def identify_table(table, last_table, clean_obs):
    """
    loops through the table and decides what table it is based on if any of
    its cells contains certain strings. if the last_table is a competency
    table then the program relaxes the constraint on identifying another
    competency table. This is to ensure that if a competency table is split
    over 2+ pages, and only a couple of competencies are on the second
    page, that we still identify that table as part of the competency table.
    """
    
    comp_set, _, name_set, bad_chars, space_chars = clean_obs
    
    table_name="other"
    num_comp = 0
    for row in table:
#        last_text = ""
        for cell in row:
            #clean the cell entry for easier identification
            cell_cleaned=cell.lower()
            for b in bad_chars: cell_cleaned = cell_cleaned.replace(b, "")
            for s in space_chars: cell_cleaned = cell_cleaned.replace(s, " ")
            cell_cleaned=" ".join(cell_cleaned.split())
            
            #Check 1: does the table give identifying information
            if cell_cleaned in name_set:
                return "info"
                
            #Check 2: does the table give competency information
            #in non-2019, we can find 'competencies' in the first cell of table
            if cell_cleaned in comp_set:
                num_comp+=1 #keep track of the number of listed competencies
                if (last_table=="competency") & (num_comp==1):
                    return "competency"
                if num_comp == 5: #if the table has identified all five competency categories
                    return "competency"
            
    return table_name

