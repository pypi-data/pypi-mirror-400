#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:12:09 2025

@author: nayandusoruth
"""
import numpy as np
import datetime


""" Misc utilities
Assorted general utilities
"""

def strLinesConcatenate(strList, current=""):
    """utility function - concatenates and returns strList with line breaks""" # - </Verified/>
    if(len(strList)==1):
        return '\n'.join([current, str(strList[0])])
    else:
        return '\n'.join([current, strLinesConcatenate(strList[1:],current=str(strList[0]))])
    
    
def convertStrDateTime(dateTimeStr):
    """utility function - converts 'dd/mm/yyyy hh:mm:ss' str to datetime object""" # - </Verified/>
    format = "%d/%m/%Y %H:%M:%S"
    dateTime = datetime.datetime.strptime(dateTimeStr, format)
    return dateTime
