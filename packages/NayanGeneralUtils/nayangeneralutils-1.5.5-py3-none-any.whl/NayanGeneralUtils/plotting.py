#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 14:51:45 2025

@author: nayandusoruth
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import NayanGeneralUtils.fileHandling as fileHandling
import sympy as sy

""" Plotting functions
Some general plotting functions using matplot lib
"""

class plotter():
    """Plotter class - acts as 'wrapper' to matplotlib fig/ax objects - intended to streamline plotting data"""
# utility methods
    # constructor method ---------------------------- </verified/>
    def __init__(self, markerWidth=0.8, markerArea=12, gridColor='k', gridStyle='-',gridWidth=0.1, errCapsize=3, histWidth=0.5):
        """Plotter object constructor - sets up fig/ax and standard formatting variables"""
        # setup figure/axes
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        
        # setup standard formatting variables
        self.markerWidth = markerWidth
        self.markerArea = markerArea
        
        self.gridColor = gridColor
        self.gridStyle = gridStyle
        self.gridWidth = gridWidth
        
        self.errCapsize = errCapsize
        
        self.histWidth = histWidth
    
    # display figure method - </verified/>
    def display(self):
        """Utility method - displays current figure"""
        plt.show()
        
    # save figure method - </verified/>
    def saveFig(self, directory, fileName):
        """Utility method - Saves figure to directory/fileName.png"""
        fileHandling.saveFigure(directory, fileName, self.fig)
    
    # get fig width method - </verified/>
    def figWidth(self):
        """Utility method - returns width of figure in pixels"""
        return int(self.fig.get_figwidth() * self.fig.get_dpi())
    
    # get fig width method - </verified/>
    def figHeight(self):
        """Utility method - returns height of figure in pixels"""
        return int(self.fig.get_figheight() * self.fig.get_dpi())
    
# figure "setup" methods ----------------------------
    
    # axis labels method - </verified/>
    def axisLabels(self, xLabel="xData", yLabel="yData"):
        """Figure setup method - label axes on figure"""
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)
        
    # axis ticks methods - </verified/>
    def axisTicks(self, xTicks, yTicks):
        """Figure setup method - manually sets axis ticks with xTicks and yTicks"""
        # setup axis ticks
        self.ax.set_xticks(xTicks)
        self.ax.set_yticks(yTicks)
        
    # gridline setup method - </verified/>
    def gridline(self):
        """Figure setup method - sets gridlines"""
        self.ax.grid(color=self.gridColor, linestyle=self.gridStyle, linewidth=self.gridWidth)
    
    # legend setup method - </verified/>
    def legend(self, loc="upper right"):
        """Figure setup method - applies a legend to location loc"""
        plt.legend(loc=loc)
    
# plotting methods ---------------------------------

    # symPy expression plotting method  - </verified/>
    def plotFunction(self, expression, xVariable, xLow, xHigh, color='k', label=""):
        """Plotting method - basic sympy expression plotting over xVariable in [xLow, xHigh]"""
        # convert to lambda function for evaluation purposes
        lambdaExpression = sy.lambdify(xVariable, expression,modules=['numpy'])
        
        # evaluate expression over linspace
        xData = np.linspace(xLow, xHigh, self.figWidth())
        yData = lambdaExpression(xData)
                
        self.ax.plot(xData, yData, color=color, label=label)

    # base scatter method - </verified/>
    def scatter(self, xData, yData, marker = 'x', color='k', label=""):
        """Plotting method - basic scatter plot between xData and yData"""
        self.ax.scatter(xData, yData, marker = marker, color=color, s=self.markerArea, linewidths=self.markerWidth, label=label)
    
    # scatter w/yAxis errorbars method - </verified/>
    def scatterYer(self, xData, yData, yErr, color='k', label=""):
        """Plotting method - basic scatter plot between xData and yData with error in y yErr"""
        self.ax.errorbar(xData, yData, marker = "", color=color, yerr=yErr, label=label, ls="", capsize=self.errCapsize)
    
    # scatter w/xAxis errorbars method - </verified/>
    def scatterXer(self, xData, yData, xErr, color='k', label=""):
        """Plotting method - basic scatter plot between xData and yData with error in x xErr"""
        self.ax.errorbar(xData, yData, marker = "", color=color, xerr=xErr, label=label, ls="", capsize=self.errCapsize)
    
    # scatter w/xyAxis errorbars method - </verified/>
    def scatterXYer(self, xData, yData, xErr, yErr, color='k', label=""):
        """Plotting method - basic scatter plot between xData and yData with error in both x,y xrr, yErr"""
        self.ax.errorbar(xData, yData, marker = "", color=color, yerr=yErr, xerr=xErr, label=label, ls="", capsize=self.errCapsize)
        
    # base histogram method - </verified/>
    def histogram(self,xData, bins=10, color="r", label=""):
        """Plotting method - basic histogram plot over xData"""
        self.ax.hist(xData, bins = bins, color=color, label=label, rwidth=self.histWidth)



