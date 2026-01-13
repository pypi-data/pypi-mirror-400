#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:06:55 2025

@author: nayandusoruth
"""

import os
import pandas as pd
import json


""" File handling
A set of functions and utilities for handling files. This includes accessing CSV files, saving CSV, text, and image fig files, as well as creating new file paths
"""

# create new folder
def createFolder(directory, folderName):
    """File handling function - creates new folder at 'directory/folderName'"""
    newPath = str(directory + "/"+folderName)
    if (not os.path.exists(newPath)):
        os.makedirs(newPath)
    return newPath

# data function - reads CSV from filepath/filename - </verified/>
def getData(filePath, fileName):
    """File handling function - reads CSV from 'filepath/filename'"""
    # get data from directory/file and return to original directory
    curDir = os.getcwd()
    os.chdir(filePath)
    data = pd.read_csv(fileName + ".csv", skipinitialspace=True, sep=",", on_bad_lines='skip')
    os.chdir(curDir)

    # return
    return data

# utility function - saves dataframe as csv to filepath/filename.csv - </verified/>
def saveCSV(filepath, filename, dataFrame):
    """File handling function - saves dataframe as csv to filepath/filename.csv"""
    curDir = os.getcwd() # get the current directory
    os.chdir(filepath)
    path = filepath + "/" + filename + ".csv"
    dataFrame.to_csv(path)
    os.chdir(curDir)

# utility function - saves string text as txt to filepath/filename.txt" - </verified/>
def saveTxT(filepath, filename, text, ext="txt"):
    """File handling function - saves string text as txt to filepath/filename.txt"""
    curDir = os.getcwd() # get the current directory
    os.chdir(filepath)
    
    file = open((filename + "." + ext), "a")
    file.write(text)
    file.close()
    
    os.chdir(curDir)
    
# utility function - reads string from txt doc and returns - note can change file extension if need be - </verified/>
def readTxT(filepath, filename, ext="txt"):
    """File handling function - reads string content of ilepath/filename.ext"""
    
    curDir = os.getcwd() # get the current directory
    os.chdir(filepath)
    file = open(filepath + "/" + filename + "." + ext ,"r")
    text = file.read()
    
    os.chdir(curDir)
    
    return text

# utility function - saves fig to directory with filename - </verified/>
def saveFigure(directory, fileName, fig):
    """File handling function - saves fig to directory with filename"""
    # go to desired directory
    curDir = os.getcwd() # get the current directory
    os.chdir(directory)

    # save figure to folder
    fig.savefig(fileName, dpi=300, bbox_inches='tight')
    
    # go back to original directory
    os.chdir(curDir)
    
    
# utility function - saves python dictionary as a json file  - </verified/>
def saveDictAsJson(directory, fileName, dictionary, indent=3):
    """File handling function - saves dictionary to directory with filename as Json with indent=indent"""
    
    # go to desired directory
    curDir = os.getcwd() # get the current directory
    os.chdir(directory)
    
    # save file as json
    with open("citationFieldRequirements.json", "w") as file:
        json.dump(dictionary, file, indent=indent)
        
    # go back to original directory
    os.chdir(curDir)

# utility function - loads python dictionary from json file - </verified/>
def loadDictFromJson(directory, fileName):
    """File handling function - loads dictionary from directory/fileName.json"""
    # go to desired directory
    curDir = os.getcwd() # get the current directory
    os.chdir(directory)
    
    # access json file
    with open(directory + "/" + fileName + '.json') as json_file:
        dictionary = json.load(json_file) 
        
    # go back to original directory
    os.chdir(curDir)
    
    return dictionary
