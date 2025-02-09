# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 15:20:04 2020

@author: Asser.Maamoun
"""

import pandas as pd
import numpy as np


#### START HELPER FUNCTIONS
    
def overlapMatRaw(df):
    df = df.notnull()
    if "Non_Missing" in df.columns:
        df = df.drop('Non_Missing', axis=1)
    n_cols = len(df.columns)
    matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    for i in range(n_cols):
        for j in range(i+1):
            overlapping = sum( df.iloc[:,i] & df.iloc[:,j] )
            matrix.iat[i, j] = overlapping
            matrix.iat[j, i] = overlapping
    #sort by counts
    matrix.sort_values(by="doc_id", axis=0, ascending=False, inplace=True)
    indexes = list(matrix.index.values)
    matrix = matrix[indexes]
    return matrix

def overlapMatPercent(overlaps):
    n_cols = len(overlaps.columns)
    matrix = pd.DataFrame(index=overlaps.columns, columns=overlaps.columns)
    seen_null = set()
    for i in range(n_cols):
        for j in range(n_cols):
            if overlaps.iat[i,i] == 0:
                matrix.iat[i, j] = np.nan
                if overlaps.columns[i] not in seen_null:
                    seen_null.add(overlaps.columns[i])
                    print("column", overlaps.columns[i], "has no non-null")
                continue
            matrix.iat[i, j] = overlaps.iat[i, j] / overlaps.iat[i,i]
    return matrix

def check_mergeMatrix(df, v1, v2):
    return df.loc[v1][v2]==0

def check_mergeDoc(df, v1, v2):
    for i, row in df.iterrows():
        if (pd.notnull(row[v1])) & (pd.notnull(row[v2])):
            print("check doc:", row['doc_path'])
            return False
    return True

def checkMerge(df, overlaps, mergers):
    mergers_dict = {}
    #rows in df are a list of variables to merge together
    for i, row in mergers.iterrows():
        l = sum(1 for e in row if pd.notnull(e))
        n_overlaps = 0
        new_row = []
        #if there is only one competency in the row, skipit
        if l<2:
            continue
        #check all possible combinations of competencies in the given row
        for i in range(len(row)):
            if pd.isnull(row[i]):
                continue
            elif row[i] not in df.columns:
                print("<", row[i], "> not found in df")
                continue
            new_row.append(row[i])
            for j in range(i-1):
                if pd.isnull(row[j]):
                    continue
                elif row[j] not in df.columns:
                    print("<", row[j], "> not found in df")
                    continue
                if not check_mergeMatrix(overlaps, row[i], row[j]):
                    n_overlaps += 1
                    check_mergeDoc(df, row[i], row[j]) #find a document that we can check
                    print("overlapping keys: <" + row[i] + "> , <" + row[j] + ">")
        #create a dictionary of replacements to use in merge_vars
        for name in new_row[1:]:
            mergers_dict[name] = new_row[0]
    return mergers_dict

def merge_vars(old_df, v1, v2):
    df=old_df.copy()
    if v1 not in old_df.columns:
        print("<", v1, "> not found in df")
        return old_df
    elif v2 not in old_df.columns:
        print("<", v2, "> not found in df")
        return old_df
    df[v1] = np.where(pd.isnull(df[v1]), df[v2], df[v1])
    df.drop(v2, inplace=True, axis=1)
    return df

def checkMerge_nodrop(df, overlaps, mergers):
    mergers_dict = {}
    #rows in df are a list of variables to merge together
    for i, row in mergers.iterrows():
        l = sum(1 for e in row if pd.notnull(e))
        n_overlaps = 0
        new_row = [row[0].replace("comp_raw_", "comp_merged_")]
        #check all possible combinations of competencies in the given row
        for i in range(len(row)):
            if pd.isnull(row[i]):
                continue
            elif row[i] not in df.columns:
                print("<", row[i], "> not found in df")
                continue
            new_row.append(row[i])
            for j in range(i-1):
                if not check_mergeMatrix(overlaps, row[i], row[j]):
                    n_overlaps += 1
                    check_mergeDoc(df, row[i], row[j]) #find a document that we can check
                    print("overlapping keys: <" + row[i] + "> , <" + row[j] + ">")
        #create a dictionary of replacements to use in merge_vars
        for name in new_row[1:]:
            mergers_dict[name] = new_row[0]
    return mergers_dict


def merge_vars_nodrop(old_df, v1, v2):
    df=old_df.copy()
    if v1 not in old_df.columns:
        print("<", v1, "> not found in df")
        df[v1] = df[v2]
        return df
    elif v2 not in old_df.columns:
        print("<", v2, "> not found in df")
        return old_df
    df[v1] = np.where(pd.isnull(df[v1]), df[v2], df[v1])
    return df

#### END HELPER FUNCTIONS
