#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:07:50 2025

@author: nayandusoruth
"""

import numpy as np
import os
import time



""" progress class
a small utility class which acts as a "progress bar" - "packaged away" into it's own object for code reuse and legibility
"""
class progress():
    # constructor method - constructor for progress object - </verified/>
    def __init__(self, startIt, totalIt):
        """Constructor method - takes as arguments starting and total iterations of timer"""
        self.currentIteration = startIt
        self.totalIterations = totalIt
        
        # setup array of time stamps and corresponding iteration indices
        self.timeIndexes = np.array([0])
        self.times = np.array([time.time()])
    
    # utility function - cls() - clears txt console output - </verified/>
    def cls(self):
        """utility method - clears console"""
        os.system('cls' if os.name=='nt' else 'clear')
    
    # core function - increments progress object currentIteration - </verified/>
    def increment(self, increment=1):
        """Computational method - increments progress object iteration - takes as optional argument 'increment'"""
        self.currentIteration += increment
        
        # add new timestamp to timeIndexes and times
        self.timeIndexes = np.append(self.timeIndexes, self.currentIteration)
        self.times = np.append(self.times, time.time())
        
    # output function - displays current progress to console  - </verified/>
    def display(self, title="", percentDisplay=True, rounding=2):
        """Accessor method - displays current progress in console - takes as optional arguments the progress's 'title', wether to display it as a percentage, and the display rounding"""
        self.cls()
        if(percentDisplay):
            percent = round(100 * self.currentIteration / self.totalIterations, rounding)
            print(title, percent, "%", end="\r")
        else:
            print(title, self.currentIteration, " / ", self.totalIterations, end="\r")
    
    # utility function - returns total time elapsed by progress object
    def timeElapsed(self):
        """Accessor method - returns total time recorded"""
        return (self.times[len(self.times)-1] - self.times[0])