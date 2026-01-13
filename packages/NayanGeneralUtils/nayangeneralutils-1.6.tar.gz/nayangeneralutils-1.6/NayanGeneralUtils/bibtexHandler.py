#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 10:41:36 2025

@author: nayandusoruth
"""
# ==========================================================================================================================================
# library imports
# ==========================================================================================================================================

import os
import json
import pandas as pd
import NayanGeneralUtils.fileHandling as fileHandling
import NayanGeneralUtils.misc as miscUtilities

import bibtexparser
citationFieldRequirements = fileHandling.loadDictFromJson("./", "citationFieldRequirements")


# ==========================================================================================================================================
# static citation field validity table
# table of all citation types, their required fields and optional fields
# setup as nested dictionary of entryType:{field:required/optional/clarificationNeeded/notRequired}
# ==========================================================================================================================================
"""# list of all field types
fieldTypes = ["address", "annote", "author", "booktitle", "chapter", "crossref", "edition", "editor", "howpublished", "institution", "journal", "key", "month", "note", "number", "organization", "pages", "publisher", "school", "series", "title", "type", "volume", "year"]

# cooresponding list of requirements for each entry type
articleReq = ["notRequired", "notRequired", "required", "notRequired","notRequired","notRequired","notRequired","notRequired","notRequired","notRequired", "required", "notRequired", "optional", "optional", "optional", "notRequired", "optional", "notRequired","notRequired","notRequired", "required", "notRequired", "optional", "required"]
bookReq = ["optional", "notRequired", "clarificationNeeded", "notRequired", "notRequired", "notRequired", "optional", "clarificationNeeded", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "optional", "notRequired", "notRequired", "required","notRequired", "optional", "required", "notRequired", "optional", "required"]
bookletReq = ["optional", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "optional", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "required", "notRequired", "notRequired", "optional"]
inbookReq = ["optional", "notRequired", "clarificationNeeded", "notRequired", "clarificationNeeded", "notRequired", "optional", "clarificationNeeded", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "optional", "notRequired", "clarificationNeeded", "required", "notRequired", "optional", "required", "optional", "optional", "required"]
incollectionReq = ["optional", "notRequired", "required", "required", "optional", "notRequired", "optional", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "optional", "notRequired", "optional", "required", "notRequired", "optional", "required", "optional", "optional", "required"]
inproceedingsReq = ["optional", "notRequired", "required", "required", "notRequired", "notRequired", "notRequired", "optional","notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "optional", "optional", "optional", "optional", "notRequired", "optional", "required", "notRequired", "optional", "required"]
manualReq = ["optional", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "required", "notRequired", "notRequired", "optional"]
thesisReq = ["optional", "notRequired", "required", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "required", "notRequired", "required", "optional", "notRequired", "required"]
miscReq = ["notRequired", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "optional", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "notRequired", "notRequired", "optional"]
proceedingsReq = ["optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "optional", "optional", "optional", "notRequired", "optional", "notRequired", "optional", "required", "notRequired", "optional", "required"]
techReportReq = ["optional", "notRequired", "required", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "required", "notRequired", "notRequired", "optional", "optional", "optional", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "required", "optional", "notRequired", "required"]
unpublishedReq = ["notRequired", "notRequired", "required", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "optional", "required", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "notRequired", "required", "notRequired", "notRequired", "optional"]


# cooresponding dictionary of requirements for each entry type
articleReqDict = dict(zip(fieldTypes, articleReq))
bookReqDict = dict(zip(fieldTypes, bookReq))
bookletReqDict = dict(zip(fieldTypes, bookletReq))
inbookReqDict = dict(zip(fieldTypes, inbookReq))
incollectionReqDict = dict(zip(fieldTypes, incollectionReq))
inproceedingsReqDict = dict(zip(fieldTypes, inproceedingsReq))
manualReqDict = dict(zip(fieldTypes, manualReq))
thesisReqDict = dict(zip(fieldTypes, thesisReq))
miscReqDict = dict(zip(fieldTypes, miscReq))
proceedingsReqDict = dict(zip(fieldTypes, proceedingsReq))
techReportReqDict = dict(zip(fieldTypes, techReportReq))
unpublishedReqDict = dict(zip(fieldTypes, unpublishedReq))

print(articleReqDict)

# dictionary of entryType:requirement dictionary
entryRequirements = {"article":articleReqDict, "book":bookReqDict, "booklet":bookletReqDict, "inbook":inbookReqDict, "incollection":incollectionReqDict, "inproceedings":inproceedingsReqDict, "conference":inproceedingsReqDict, "manual":manualReqDict, "mastersthesis":thesisReqDict, "phdthesis":thesisReqDict, "misc":miscReqDict, "proceedings":proceedingsReqDict, "techreport":techReportReqDict, "unpublished":unpublishedReqDict}
print(entryRequirements)

entryRequirements_jsonString = json.dumps(entryRequirements, indent=3)
print(entryRequirements_jsonString)

os.chdir("/Users/nayandusoruth/Desktop/bibtexHandler")
with open("citationFieldRequirements.json", "w") as file:
    json.dump(entryRequirements, file, indent=3)
"""
# ==========================================================================================================================================
# citation class
# represents an individual citation with a citation type, field-entry dictionary
# ==========================================================================================================================================

class citation():
    # ------------------------------------------------
    # constructor - </method verified/>
    # ------------------------------------------------
    def __init__(self,constructorType, entryData, citationFieldRequirements):
        """
        Citation class constructor method
        
        Parameters
        ----------
        constructorType : string (fromDict, fromDataFrame, fromBib)
            constructor config, wether citation is generated from a {field:value} dictionary, pandas dataframe, or bibtexparser.model.Entry object.
        entryData : dictionary, pd.DataFrame, bibtexparser.model.Entry
            the citation input data according to the 'constructorType'.
        citationFieldRequirements : dictionary
            nested dictionary describing required, optional, clarificationNeeded and notRequired fields for citation type 'entryType'

        Raises
        ------
        ValueError
            raised when inputted 'constructorType' doesn't match allowed cases.

        Returns
        -------
        None.

        """
        # initalise citation variables - citationKey is .bib entry "name" key - called citationKey to avoid confusion with field key-value pairs - field is dictionary for fields
        self.citationKey = ""
        self.entryType = ""
        self.fields = {}
        self.citationFieldRequirements = citationFieldRequirements # nested dictionary of entry types : {fields:requirements}
        self.entryTypes = citationFieldRequirements.keys() # list of all valid entry types
        self.requiredFilled = []
        self.RequiredUnfilled = []
        
        # call appropriate constructor helper
        if(constructorType=="fromDict"):
            self.fromDict(entryData)
        elif(constructorType=="fromDataFrame"):
            self.fromDataFrame(entryData)
        elif(constructorType=="fromBib"):
            self.fromBib(entryData)
        else:
            raise ValueError("citation class - constructorType: '" + constructorType + "' is invalid")
        
        # check self's validity
        self.valid(returnReport=False)
        
            
    # ------------------------------------------------
    # constructor helpers
    # ------------------------------------------------
    # takes in a dictionary of citationKey and fields, assigns fields - </method verified/>
    def fromDict(self, dictEntry):
        """
        Constructor helper method
        assigns self.citationKey, self.entryType, self.fields  

        Parameters
        ----------
        dictEntry : dictionary
            Dictionary of {citationKey, entryType, fields} representing a citation

        Returns
        -------
        None.

        """
        # assign citation key and entry type
        self.citationKey = dictEntry['citationKey'][0]
        self.entryType = dictEntry['entryType'][0]
        
        # remove citation key and entry type from dictEntry
        del dictEntry['citationKey']
        del dictEntry['entryType']
        
        # assign fields
        for key, value in dictEntry.items():
            self.fields[key] = value[0]
    
    # takes in a pandas dataframe of one row of a CSV entry, assigns fields - </method verified/>
    def fromDataFrame(self,rowEntry):
        """
        Constructor helper method
        assigns self.citationKey, self.entryType, self.fields 

        Parameters
        ----------
        rowEntry : pd.DataFrame
            1 row dataframe with citationKey, entryType, fields headers representing a citation

        Returns
        -------
        None.

        """
        # convert pd dataframe to dictionary and feed to fromDict method
        rowDict = rowEntry.to_dict(orient='list')
        self.fromDict(rowDict)

    # takes in a bibtexparser.model.Entry object, assigns fields - </method verified/>
    def fromBib(self, bibEntry):
        """
        Constructor helper method
        assigns self.citationKey, self.entryType, self.fields 

        Parameters
        ----------
        bibEntry : bibtexparser.model.Entry
            bibtexparser object representing a citation

        Returns
        -------
        None.

        """
        # assign citation key and entry type
        self.citationKey = bibEntry.key
        self.entryType = bibEntry.entry_type
        # add fields to self.fields
        for field in bibEntry.fields:
            self.addField(field.key, [field.value])  
    
    # ------------------------------------------------
    # utility methods
    # ------------------------------------------------
    
    # adds a field to self.field - </method verified/>
    def addField(self, key, value):
        """
        Citation utility method
        Adds a field {key:value} to self.fields

        Parameters
        ----------
        key : string
        value : string


        Returns
        -------
        None.

        """
        self.fields[key] = value
        
    # returns fields that satisfy requrement for entryType - </method verified/>
    def getFieldsByReq(self, citationFieldRequirements, entryType, requirement):
        """
        Citation utility method
        
        Parameters
        ----------
        citationFieldRequirements : Dictionary
            Nested dictionary describing which fields are required for different entryTypes.
        entryType : string
            Citation type.
        requirement : string (required, optional, clarificationNeeded, notRequired)
            Requirement condition for given fields.

        Returns
        -------
        list
            Fields by entryType from citationFieldRequirements that match requirement.

        """
        dictionary = citationFieldRequirements[entryType]
        return [key for key, value in dictionary.items() if value == requirement]
    
    # return wether or not field is filled out - note checks if field string is not 0 length as well - </method verified/>
    def isFieldFilled(self, field):
        """
        Citation utility method
        
        Parameters
        ----------
        field : string
            Citation field to test if filled.

        Returns
        -------
        Bool
            True/False if field is filled.

        """
        return (self.fields.get(field) is not None and len(self.fields[field][0]) > 0)
    
    # merge citations, return another citation - </method verified/>
    def merge(self, otherCitation):
        """
        Parameters
        ----------
        otherCitation : citation
            citation that will be merged with.

        Returns
        -------
        citation
            Merged citation.

        """
        # check if they have same citationKey and entryType - if not return None
        if(not(self.citationKey == otherCitation.citationKey) or not(self.entryType == otherCitation.entryType)):
            return None
        
        # get both citations as dictionaries
        selfFields = self.fields.copy()
        otherFields = otherCitation.fields.copy()
        
        # iterate through all items in selfFields
        for key, value in selfFields.items():
            # if otherFields contains key, compare them
            otherValue = otherFields.get(key)
            if(otherValue is not None):
                
                # compare values, discard worse one from either selfField or otherFields as appropriate
                if(self.compareFields(key, value, otherValue)):
                    del otherFields[key]
        
        # iterate through all items in otherFields (couldn't delete selfField entries directly otherwise loop gets unhappy)
        for key, value in otherFields.items():
            # if otherFields contains key, compare them
            selfValue = selfFields.get(key)
            if(selfValue is not None):
                
                # compare values, discard worse one from either selfField or otherFields as appropriate
                if(self.compareFields(key, value, selfValue)):
                    del selfFields[key]
                    
        
        # merge fields and reformat for fromDict constructor     
        mergeFields = {**selfFields, **otherFields}
        
        mergeFields["citationKey"] = [self.citationKey]
        mergeFields["entryType"] = [self.entryType]
        
        # return as new citation
        return citation("fromDict", mergeFields, self.citationFieldRequirements)
        
        
                
    # compare field values with same key - returns True if value1 is 'better' than value 2 - </method verified/>
    def compareFields(self, key, value1, value2):
        """
        Parameters
        ----------
        key : string
            field key.
        value1 : string
            first value of field to compare.
        value2 : string
            second value of field to compare.

        Returns
        -------
        bool
            returns True if value1 is 'better' than value 2.
            'better' arbitrarly decided on basis of str length (longer value is better), since longer field value is expected to be more complete.
            Note this is a crude comparison and may be edited in future.
        """
        len1 = len(value1[0])
        len2 = len(value2[0])
        
        return (len1 >= len2)
    
    # evaluate if field value is valid - currently a placeholder method; should be able to check
    def isFieldValid(self, key, value):
        return True
        
        
    # ------------------------------------------------
    # validation methods
    # ------------------------------------------------
    
    # checks if citation is valid - if its a valid entry type, and if so if there's any missing required fields - assigns to self - </method verified/>
    def valid(self, returnReport=False):
        """
        Citation validation method
        Tests if self.entryType is correct, and if citation fills all required fields - assigns self.requiredFilled, self.RequiredUnfilled

        Parameters
        ----------
        returnReport : bool, optional
            Wether to return a string report.

        Returns
        -------
        Bool
            True/False if citation is correctly filled/valid.

        """
        if(self.validEntryType()):
            self.requiredFilled, self.RequiredUnfilled = self.getUnfilledFields("required", returnUnfilled=True)
            
            if(returnReport):
                if(self.requiredFilled):
                    return "all required fields filled"
                return "some required fields missing: " + str(self.RequiredUnfilled)
            
        if(returnReport):
            return "invalid entryType"
            
    # checks if self.entryType is a valid bibtex entryType - </method verified/>
    def validEntryType(self):
        """
        Citation validation method
        Returns
        -------
        Bool
            True/False if self.entryType is valid entryType.

        """
        return (self.entryType in self.entryTypes)
    
    # checks which fields that satisfy "requirement" for self.entryType are filled - returns True if all fields are filled, False otherwise - optionally returns list of unfilled fields - </method verified/>
    def getUnfilledFields(self, requirement, returnUnfilled=True):
        """
        Citation validation method
        
        Parameters
        ----------
        requirement : string (required, optional, clarificationNeeded, notRequired)
            Requirement condition for given fields.
        returnUnfilled : Bool, optional
            Wether to return list of unfilled fields which match requirement. The default is True.

        Returns
        -------
        allFilled, unfilledRequirementFields : bool, optional list
            Wether or not the citation fills all fields which match Requirement. Optionally return list of unfilled fields.

        """
        # get list of required and optional fields
        requirementFields = self.getFieldsByReq(self.citationFieldRequirements, self.entryType, requirement)
        
        # remove all filled entries from requiredFields
        unfilledRequirementFields = [field for field in requirementFields if not self.isFieldFilled(field)]
        allFilled = (len(unfilledRequirementFields) == 0)
        
        if(returnUnfilled):
            return allFilled, unfilledRequirementFields
        return allFilled
            
    
        
    # ------------------------------------------------
    # output methods
    # ------------------------------------------------
    
    # return citation as a dictionary object including field:</MISSING FIELD/> for required fields - </method verified/>
    def toDict(self, includeMissingFields=True):
        """
        Citation output method
        
        Parameters
        ----------
        includeMissingFields : Bool, optional
            Wether to include missing required fields for entryType with warning message </MISSING FIELD/>. The default is True.

        Returns
        -------
        returnable : Dictionary
            Returns citation as {citationKey, entryType, fields} dictionary.

        """
        # append citationKey and entryType to returnable
        returnable = self.fields
        returnable['citationKey'] = [self.citationKey]
        returnable['entryType'] = [self.entryType]
                
        if(includeMissingFields):
            for missingField in self.RequiredUnfilled:
                returnable[missingField] = "</MISSING FIELD/>"
                
        return returnable
    
    # return citation as a pandas dataframe row - </method verified/>
    def toDataFrame(self, includeMissingFields=True):
        """
        Citation output method
        
        Parameters
        ----------
        includeMissingFields : Bool, optional
            Wether to include missing required fields for entryType with warning message </MISSING FIELD/>. The default is True.

        Returns
        -------
        pd.DataFrame
            returns citation as 1 row dataframe with citationKey, entryType, fields headers.

        """
        return pd.DataFrame(self.toDict(includeMissingFields=includeMissingFields))
    
    # return citation as bibtex formatted string - note no </MISSING FIELD/> option to avoid errors getting missed - </method verified/>
    def toBib(self):
        """
        Citation output method
        
        Returns
        -------
        string
            returns citation as string formatted in .bib file format.

        """
        # write firstline of bibtex formatted citation
        citationLines = ["@" + self.entryType + "{" + self.citationKey]
        
        # append lines for each field
        for key, value in self.fields.items():
            citationLines[len(citationLines)-1] = citationLines[len(citationLines)-1] + ","
            citationLines.append(key + " = {" + str(value) + "}")
            
        # close bibtex formatted citation
        citationLines.append("}")
        
        # string concatenate and return
        return miscUtilities.strLinesConcatenate(citationLines)
        
# testing

# open json file for citationFieldRequirements  
#with open('citationFieldRequirements.json') as json_file:
#    citationFieldRequirements = json.load(json_file)    
#citationFieldRequirements = fileHandling.loadDictFromJson("/Users/nayandusoruth/Desktop/bibtexHandler", "citationFieldRequirements")
    
#csv = {'citationKey':['testEntry'], 'entryType':["article"], 'author':["testAuthor"], 'year':["2025"], 'month':["12"], 'journal':["testJournal"], 'title':['testTitle']}
#csv2 = {'citationKey':['testEntry2'], 'entryType':["article"], 'author':["teor2"], 'year':["2026"], 'month':["9"], 'journal':["testJournal2"], 'title':['testTitle2']}

#testCsv = pd.DataFrame(csv)
#testCitation = citation("fromDataFrame", testCsv, citationFieldRequirements)  
#testCitation2 = citation("fromDict", csv2, citationFieldRequirements)  



#mergeCitation = testCitation.merge(testCitation2)
#print(mergeCitation.toDict(includeMissingFields=False))
#print()
#print(testCitation.toDict(includeMissingFields=False))
#print()
#print(testCitation2.toDict(includeMissingFields=False))
#print(testCitation.toBib())
#print(testCitation2.toBib())



# ==========================================================================================================================================
# bibliography class
# represents a list of citations as a list of citation objects
# ==========================================================================================================================================

class bibliography():
    # ------------------------------------------------
    # constructor method
    # ------------------------------------------------
    def __init__(self, constructorType, entryData, citationFieldRequirements):
        """
        

        Parameters
        ----------
        constructorType : Str (fromList, fromDataFrame, fromBib, fromDict)
            What constructor should be used.
        entryData : TYPE
            DESCRIPTION.
        citationFieldRequirements : TYPE
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.citationFieldRequirements = citationFieldRequirements # nested dictionary of entry types : {fields:requirements}
        self.citations = {} # dictionary of {citationKeys:citation objects}
        
        if(constructorType=="fromList"):
            self.fromList(entryData)
        elif(constructorType=="fromDataFrame"):
            self.fromDataFrame(entryData)
        elif(constructorType=="fromBib"):
            self.fromBib(entryData)
        elif(constructorType=="fromDict"):
            self.fromDict(entryData)
        else:
            raise ValueError("Bibliography class - constructorType: '" + constructorType + "' is invalid")
            
        # debug code
        #print(self.citations)
        #print(self.citations["testEntry"].citationKey)
        #print(self.citations["testEntry2"].citationKey)
    # ------------------------------------------------
    # constructor helpers
    # ------------------------------------------------
    
    # assigns self.citations from a dict of citation objects
    def fromDict(self, citationDict):
        self.citations = citationDict.copy()
    
    # assigns self.citations from a list of citation objects - </method verified/>
    def fromList(self, citationList):
        citationKeys = [citationKey.citationKey for citationKey in citationList]
        self.citations = dict(zip(citationKeys, citationList))
        
    # assigns self.citations from a dataframe of citations - </method verified/>
    def fromDataFrame(self, citationDataFrame):
        # convert dataframe to list of citation objects
        citationList = []
        for i in range(0, citationDataFrame.shape[0]):
            row = citationDataFrame.iloc[i:i+1]
            citationList.append(citation("fromDataFrame", row, self.citationFieldRequirements))
        
        # pass to self.fromList to finish assignment
        self.fromList(citationList)

    # assigns self.citations from a .bib file string of citations - </method verified/>
    def fromBib(self, citationBibString):
        # parse citationBibString using bibtexparser to list of bibtexparser.model.Entry objects
        library = bibtexparser.parse_string(citationBibString)
        entries = library.entries
        
        # convert list of bibtexparser.model.Entry objects to citationList
        citationList = []
        for i in range(0, len(entries)):
            citationList.append(citation("fromBib", entries[i], self.citationFieldRequirements))
        
        # pass to self.fromList to finish assignment
        self.fromList(citationList)
        
    # ------------------------------------------------
    # utility
    # ------------------------------------------------
    
    # ------------------------------------------------
    # merge methods
    # ------------------------------------------------
    
    # returns a new bibliography object which merges self and otherBibliography - </method verified/>
    def mergeBibliography(self, otherBibliography, mergeCitations=True):
        
        # get list of self/other (make sure to copy)
        selfCitationsCopy = self.citations.copy()
        otherCitationsCopy = otherBibliography.citations.copy()
        
        
        # if mergeCitations - optional parameter, wether or not to attempt merging citations with same citationKey
        if(mergeCitations):
            # iterate through self, look for copies in other - this is to merge citation copies
            for key, value in selfCitationsCopy.items():
                otherCitation = otherCitationsCopy.get(key)
                if(otherCitation is not None):
                    print("Citation merged: ", key) # warning message
                    # merge copy into self
                    selfCitationsCopy[key] = selfCitationsCopy.get(key).merge(otherCitation)
                    # delete copy from otherCitationsCopy
                    del otherCitationsCopy[key]
        else:
            # go through same loop, but change key name to accomodate both citations
            for key, value in selfCitationsCopy.items():
                otherCitation = otherCitationsCopy.get(key)
                if(otherCitation is not None):
                    print("duplicate citaiton found: ", key) # warning message
                    citation = otherCitationsCopy.pop(key)
                    citation.citationKey = key + "_copy"
                    otherCitationsCopy[key + "_copy"] = citation # 
    
        # concatenate self/other
        mergedDictionary = {**selfCitationsCopy, **otherCitationsCopy}
        
        # instantiate new bibliography and return
        return bibliography("fromDict", mergedDictionary, self.citationFieldRequirements)
    
    
   
    
    # ------------------------------------------------
    # output methods
    # ------------------------------------------------
    
    # returns string list of citation keys
    def strKeys(self):
        return str(list(self.citations.keys()))
    
    # return bib formattted string of specific citation
    def strCitation(self, citationKey):
        citation = self.citations.get(citationKey)
        return citation.toBib()
    
    # returns citations as list of citations - </method verified/>
    def toList(self):
        return list(self.citations.values())
    
    # returns citations as pandas dataframe - </method verified/>
    def toDataFrame(self, includeMissingFields=True):
        citationList = self.toList()
        returnable = citationList[0].toDataFrame(includeMissingFields=includeMissingFields)
        
        for i in range(1, len(citationList)):
            returnable = pd.merge(returnable, citationList[i].toDataFrame(includeMissingFields=includeMissingFields), how='outer')
            
        return returnable
        
    # returns citations as a .bib formatted string - </method verified/>
    def toBib(self):
        citationList = self.toList()
        strList = []
        #miscUtilities.strLinesConcatenate(citationLines)
    
        for citation in citationList:
            strList.append(citation.toBib())
            
        return miscUtilities.strLinesConcatenate(strList)
# testing
#citationList = [testCitation,testCitation2]

#csvCombined = {'citationKey':['testEntry', 'testEntry2'], 'entryType':["article", "article"], 'author':["testAuthor", "testAuthor2"], 'year':["2025", "2026"], 'month':["12", "9"], 'journal':["testJournal", "testJournal2"], 'title':['testTitle','testTitle2']}



#fileHandling.readTxT(filepath, filename, ext="txt")

#citationDataframe = pd.DataFrame(csvCombined)
#testBibliography = bibliography("fromDataFrame", citationDataframe, citationFieldRequirements)
#citations = testBibliography.toList()
#print(citations[0].citationKey)
#print(citations[1].citationKey)

#print(testBibliography.toDataFrame().to_string())

#print(testBibliography.toBib())

#testBibliography2 = bibliography("fromBib", bibTest2, citationFieldRequirements)
#print(testBibliography2.toBib())
#mergedBibliography = testBibliography.mergeBibliography(testBibliography2, mergeCitations=False)
#print(mergedBibliography.toDataFrame().to_string())




# ==========================================================================================================================================
# IO systems
# systems which use filehandlers to actually use
# assume citationFieldRequirements stored in same folder
# ==========================================================================================================================================

# ------------------------------------------------
# bibliography from/to file functions
# setup so that bibliographies are added/pulled from a "workspace" dictionary
# ------------------------------------------------

# returns bibliography from .csv file
def getBibFromCSV(directory, filename):
    bibDataFrame = fileHandling.getData(directory, filename)
    return bibliography("fromDataFrame", bibDataFrame, citationFieldRequirements)

# returns bibliography from .bib file
def getBibFromBib(directory, filename):
    bibString = fileHandling.readTxT(directory, filename, ext="bib")
    return bibliography("fromBib",bibString, citationFieldRequirements)

# merges bibliographies key1, key2 in bibDict dict and adds to dict as "merged:" + key1 + "_" + key2
def mergBibs(bibDict, key1, key2, mergeCitations=False):
    mergedBibliography = bibDict[key1].mergeBibliography(bibDict[key2], mergeCitations=mergeCitations)
    bibDict["merged_" + key1 + "_" + key2] = mergedBibliography

# saves a bibiography object to directory/filename.bib 
def saveBibToBib(bibliography, directory, filename):
    bibString = bibliography.toBib()
    fileHandling.saveTxT(directory, filename, bibString, ext="bib")
    
# saves a bibiography object to directory/filename.csv
def saveBibToCSV(bibliography, directory, filename, includeMissingFields=True):
    bibDataFrame = bibliography.toDataFrame(includeMissingFields=includeMissingFields)
    fileHandling.saveCSV(directory, filename, bibDataFrame)

# ------------------------------------------------
# IO functions
# ------------------------------------------------

# if called, should setup "workspace" dictionary - </function verified>
def mainIO():
    bibliographies = {}
    
    curDir = os.getcwd() # get the current directory
    workingDirectory = curDir
    
    stillWorking = True
    while(stillWorking):
        commandRaw = input("BibtexHandlerIO: ")
        command = commandRaw.split()
        
        if(command[0] == "exit"): # exit command
            stillWorking = False
        elif(command[0] == "cd" and len(command) == 2): # change directory command
            workingDirectory = cdIO(command)
        elif(command[0] == "read" and len(command) == 3): # read file command (including file ext AND adding bibKey)
            readIO(command, bibliographies, workingDirectory)
        elif(command[0] == "merge" and len(command) == 4): # merge bibliographies
            mergeIO(command, bibliographies)
        elif(command[0] == "export" and len(command) == 4): # export bibliographies
            exportIO(command, bibliographies, workingDirectory)
        elif(command[0] == "show" and len(command) == 1): # show bibliographies and current directory
            showIO(bibliographies, workingDirectory)
        elif(command[0] == "show" and len(command) == 2): # show citation keys in bibliography
            showBibliographyIO(command, bibliographies)
        elif(command[0] == "showBib" and len(command) == 2): # show citations in bibliography as bib formatted string
            showBibliographyBibIO(command, bibliographies)
        elif(command[0] == "show" and len(command) == 3): # show specific citation in bibliography as bib formatted string
            showCitationIO(command, bibliographies)
        elif(command[0] == "help"): # help
            helpString = """
            ----- bibtex handler mainIO commands -----
            cd </directory/>                                          : change current directory
            read </file/>.ext </bibliographyKey/>                     : read bibliography file in current directory to current bibliographies with key bibliographyKey
            merge </bibliographyKey1/> /bibliographyKey2/> TRUE/FALSE : merge 2 bibliographies into new bibliography - True/false for merging citations
            export /bibliographyKey/> ext TRUE/FALSE                  : export bibliograpgy as ext type - True/false wether to include </missing field/> warnings (FOR CSV output ONLY)
            show                                                      : show current bibliographies
            show </bibliographyKey/>                                  : show citation keys in specific current bibliography
            showBib </bibliographyKey/>                               : show citations as bib formatted string in specific current bibliography
            show </bibliographyKey/> </citationKey/>                  : show specific citation in specific current bibliography
            exit                                                      : exit mainIO
            """
            print(helpString)
        else:
            print("inputted command '", commandRaw, "' is invalid - try 'help' for list of commands")
            
    
    os.chdir(curDir)

# returns directory in command - </function verified>
def cdIO(command):   
   print("current working directory set: ", os.getcwd())
   return command[1]
   
# reads bibliography command input into workingDirectory - </function verified>
def readIO(command, bibliographies, workingDirectory):
    # get filename, citationkey
    filename = command[1]
    bibliographyKey = command[2]
    file = filename.split(".")
    
    # check that ext exists
    if(len(file) == 2):
        # check extension and read bibliography using appropriate function
        if(file[1] == "csv"):
            bibliography = getBibFromCSV(workingDirectory, file[0])
            bibliographies[bibliographyKey] = bibliography
        elif(file[1] == "bib"):
            bibliography = getBibFromBib(workingDirectory, file[0])
            bibliographies[bibliographyKey] = bibliography
        else:
            print("incorrect file ext provided (.csv, .bib allowed)")
    else:
        print("Incorrect filename format inputted")

# merge citations by key - </function verified>
def mergeIO(command, bibliographies):
    key1 = command[1]
    key2 = command[2]
    mergeCitations = (command[3] == "TRUE")
    mergBibs(bibliographies, key1, key2, mergeCitations=mergeCitations)
    
# export citation - </function verified>
def exportIO(command, bibliographies, workingDirectory):
    bibliographyKey = command[1]
    ext = command[2]
    includeMissing = (command[3] == "TRUE")
    bibliography = bibliographies.get(bibliographyKey)
    
    if(ext == "csv"):
        saveBibToCSV(bibliography, workingDirectory, bibliographyKey, includeMissingFields=includeMissing)
    elif(ext == "bib"):
        saveBibToBib(bibliography, workingDirectory, bibliographyKey)
    else:
        print("incorrect file ext provided (.csv, .bib allowed)")

# show all current bibliographies keys - </function verified>
def showIO(bibliographies, workingDirectory):
    print("Working directory: ", workingDirectory)
    print("Bibliographies by key: ", list(bibliographies.keys()))
    
# show list of citations in bibliography - </function verified>
def showBibliographyIO(command, bibliographies):
    bibliographyKey = command[1]
    bibliography = bibliographies.get(bibliographyKey)
    print(bibliography.strKeys())
    
# show list of citations in bibliography as bib formatted string - </function verified>
def showBibliographyBibIO(command, bibliographies):
    bibliographyKey = command[1]
    bibliography = bibliographies.get(bibliographyKey)
    print(bibliography.toBib())

# show specific citation in specific bibliography as bib formatted string - </function verified>
def showCitationIO(command, bibliographies):
    bibliographyKey = command[1]
    citationKey = command[2]
    bibliography = bibliographies.get(bibliographyKey)
    print(bibliography.strCitation(citationKey))
