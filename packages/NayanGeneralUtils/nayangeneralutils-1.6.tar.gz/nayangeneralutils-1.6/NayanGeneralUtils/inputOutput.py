#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:08:26 2025

@author: nayandusoruth
"""
import NayanGeneralUtils.fileHandling as fh


""" IO utilities
Assorted IO function utility functions
"""

# useful IO resources 
def IObool(text, default=True, ynDict = {"y":True, "n":False}):
    """IO function - general bool y/n question 'text' - returns boolean output"""
    return ynDict.get(input(text), default)

def IOint(text, default=1):
    """IO function - general int input question 'text' - returns int output"""
    inp = input(text)
    if(inp == "d"):
        return default
    return int(inp)

def IOfloat(text, default=0):
    """IO function - general float input question 'text' - returns float output"""
    inp = input(text)
    if(inp == "d"):
        return default
    return float(inp)




def IOsaveTxT(text, fileName):
    """IO function - queries where to save textfile"""
    filepath = input("save txt to filepath: ")
    fh.saveTxT(filepath, fileName, text)
    
def IOsaveCSV(data, fileName):
    """IO function - queries where to save CSV dataframe"""
    filepath = input("save data to filepath: ")
    fh.saveCSV(filepath, fileName, data)
    
def IOsaveFig(fig, fileName):
    """IO function - queries where to save matplotlib fig"""
    filepath = input("save data to filepath: ")
    fh.saveFigure(filepath, fileName, fig)
    
