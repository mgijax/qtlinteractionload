
#  qtlIntQC.py
###########################################################################
#
#  Purpose:
#
#	This script will generate a QC report for a curator allele
#	    input file
#
#  Usage:
#
#      qtlIntQC.py  filename
#
#      where:
#          filename = path to the input file
#
#  Inputs:
#      - input file as parameter - see USAGE
#
#  Outputs:
#
#      - QC report (${QC_RPT})
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#      2:  
#
#  Assumes:
#
#  Implementation:
#
#      This script will perform following steps:
#
#      1) Validate the arguments to the script.
#      2) Perform initialization steps.
#      3) Open the input/output files.
#      4) Generate the QC reports.
#      6) Close the input/output files.
#
#  History:
#
# 06/22/2022   sc   
#       - https://mgi-jira.atlassian.net/browse/CRM-284
#
###########################################################################

import sys
import os
import string
import db
import time
import Set

#
#  CONSTANTS
#
TAB = '\t'
CRT = '\n'

USAGE = 'Usage: qtlIntQC.py  inputFile'

#
#  GLOBALS
#

# intermediate load ready file
#loadReadyFile = os.getenv("INPUT_FILE_QC")
#fpLoadReady = None

# from stdin
inputFile = None

# QC report file
qcRptFile = os.getenv('QC_RPT')

# lines seen in the input file
distinctLineList = []

# duplicated lines in the input
dupeLineList = []

# lines with < 6 columns
missingColumnList = []

# lines with missing data in columns
reqColumnList = []

# a QTL id is not found in the database
badQtlIdList = []

# org and part are same ID
orgPartSameList = []

# a QTL id does not match symbol in the database
idSymDiscrepList = []

# interactions not valid
badIntTermList = []

# no reciprocal for  org/part
noReciprocalList = []

# Jnum not in database
badJnumList = []

# to determine that the reciprocal is in the input file
qtlPairDict = {}

# lines that pass QC
#goodLineList = []

# 1 if any QC errors in the input file
hasFatalErrors = 0

# lookup of QTL MGI IDs {qtlID: qtlSymbol, ...}
qtlLookupDict = {}

# list if QTL Interactions vocabulary terms 
interactionLookupList = []

# reference ID (JNum) lookup 
jNumLookupList = []

# Purpose: Validate the arguments to the script.
# Returns: Nothing
# Assumes: Nothing
# Effects: sets global variable, exits if incorrect # of args
# Throws: Nothing
#
def checkArgs ():
    global inputFile

    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)

    inputFile = sys.argv[1]
    return 0

# end checkArgs() -------------------------------

# Purpose: create lookups, open files
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables, exits if a file can't be opened,
#  creates files in the file system, creates connection to a database

def init ():

    # open input/output files
    openFiles()
    db.useOneConnection(1)

    #
    # create lookups
    #

    loadLookups()

    return 0

# end init() -------------------------------

# Purpose: load lookups for verification
# Returns: Nothing
# Assumes: 
# Effects: queries a database, modifies global variables
#

def loadLookups(): 
    global qtlLookupDict, interactionLookupList, jNumLookupList

    results = db.sql('''select a.accid, m.symbol
        from acc_accession a, mrk_marker m
        where m._marker_type_key = 6 --qtl
        and m._marker_status_key = 1 -- official
        and m._marker_key = a._object_key
        and a._mgitype_key = 2
        and a._logicaldb_key = 1
        and a.preferred = 1
        and a.private = 0
        and a.prefixPart = 'MGI:' ''', 'auto')

    for r in results:
        qtlLookupDict[r['accid']] = r['symbol']
    
    results = db.sql('''select term
        from voc_term
        where _vocab_key = 178 -- QTL Interactions ''', 'auto')

    for  r in results:
        interactionLookupList.append(r['term'])

    results = db.sql('''select a.accid
        from acc_accession a
        where a._mgitype_key = 1
        and a._logicaldb_key = 1
        and a.preferred = 1
        and a.private = 0
        and a.prefixpart = 'J:' ''', 'auto')
    for r in results:
        jNumLookupList.append(r['accid'])

    return 0

# end loadLookups() -------------------------------

#
# Purpose: Open input and output files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables.
# Throws: Nothing
#
def openFiles ():
    #global fpInput, fpLoadReady, fpQcRpt
    global fpInput, fpQcRpt

    #
    # Open the input file
    #
    # encoding='utf-8' no
    # encoding=u'utf-8' no

    try:
        fpInput = open(inputFile, 'r', encoding='utf-8', errors='replace')
    except:
        print('Cannot open input file: %s' % inputFile)
        sys.exit(1)

    #
    # Open load ready input file
    #
    #try:
    #    fpLoadReady = open(loadReadyFile, 'w')
    #except:
    #    print('Cannot open load ready file: %s' % loadReadyFile)
    #    sys.exit(1)

    #
    # Open QC report file
    #
    try:
        fpQcRpt = open(qcRptFile, 'w')
    except:
        print('Cannot open report file: %s' % qcRptFile)
        sys.exit(1)

    return 0

# end openFiles() -------------------------------

#
# Purpose: writes out errors to the qc report
# Returns: Nothing
# Assumes: Nothing
# Effects: writes report to the file system
# Throws: Nothing
#

def writeReport():
    #
    # Now write any errors to the report
    #
    if not hasFatalErrors:
         fpQcRpt.write('No QC Errors')
         return 0
    fpQcRpt.write('Fatal QC - if published the file will not be loaded')

    if len(dupeLineList):
        fpQcRpt.write(CRT + CRT + str.center('Lines Duplicated In Input',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(dupeLineList))
        fpQcRpt.write(CRT + 'Total: %s' % len(dupeLineList))

    if len(missingColumnList):
        fpQcRpt.write(CRT + CRT + str.center('Lines with < 6 Columns',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(CRT.join(missingColumnList))
        fpQcRpt.write(CRT + 'Total: %s' % len(missingColumnList))

    if len(reqColumnList):
        hasSkipErrors = 1
        fpQcRpt.write(CRT + CRT + str.center('Missing Data in Required Columns',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(reqColumnList))
        fpQcRpt.write(CRT + 'Total: %s' % len(reqColumnList))

    if len(orgPartSameList):
        fpQcRpt.write(CRT + CRT + str.center('Organizer and Participant have same ID',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(orgPartSameList))
        fpQcRpt.write(CRT + 'Total: %s' % len(orgPartSameList))

    if len(badQtlIdList):
        fpQcRpt.write(CRT + CRT + str.center('Invalid Organizer and/or Participant ID',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(badQtlIdList))
        fpQcRpt.write(CRT + 'Total: %s' % len(badQtlIdList))

    if len(idSymDiscrepList):
        fpQcRpt.write(CRT + CRT + str.center('Organizer and/or Participant ID does not match Symbol',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(idSymDiscrepList))
        fpQcRpt.write(CRT + 'Total: %s' % len(idSymDiscrepList))

    if len(badIntTermList):
        fpQcRpt.write(CRT + CRT + str.center('Interaction Term does not Resolve',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(badIntTermList))
        fpQcRpt.write(CRT + 'Total: %s' % len(badIntTermList))

    if len(badJnumList):
        fpQcRpt.write(CRT + CRT + str.center('JNumber value is not in the Database',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#','Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(badJnumList))
        fpQcRpt.write(CRT + 'Total: %s' % len(badJnumList))

    if len(noReciprocalList):
        fpQcRpt.write(CRT + CRT + str.center('No Reciprocal for Organizer/Participant',60) + CRT)
        fpQcRpt.write('%-12s  %-20s%s' % ('Line#', 'Line', CRT))
        fpQcRpt.write(12*'-' + '  ' + 20*'-' + CRT)
        fpQcRpt.write(''.join(noReciprocalList))
        fpQcRpt.write(CRT + 'Total: %s' % len(noReciprocalList))

    return 0

# end writeReport() -------------------------------

#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Modifies global variables
# Throws: Nothing
#
def closeFiles ():
    #global fpInput, fpLoadReady, fpQcRpt
    global fpInput, fpQcRpt
    fpInput.close()
    #fpLoadReady.close()
    fpQcRpt.close()

    return 0

# end closeFiles) -------------------------------

    #
    # Purpose: run all QC checks
    # Returns: Nothing
    # Assumes: file descriptors have been initialized
    # Effects: writes reports and the load ready file to file system
    # Throws: Nothing
    #

def runQcChecks():
    global hasFatalErrors, distinctLineList, dupeLineList, qtlPairDict
    global missingColumnList, reqColumnList, orgPartSameList, badQtlIdList
    global idSymDiscrepList, badIntTermList, noReciprocalList, badJnumList


    header = fpInput.readline()
    line = fpInput.readline()
    lineNum = 1
    while line:
        lineNum += 1
        #print('lineNum: %s line: %s' % (lineNum, line))
        if line not in distinctLineList:
            distinctLineList.append(line)
        else:
            dupeLineList.append('%s  %s' % (lineNum, line))
        # check that the file has at least 23 columns
        if len(str.split(line, TAB)) < 6:
            missingColumnList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
            line = fpInput.readline()
            continue
        # get columns 1-6 
        (orgID, orgSym, partID, partSym, interactionType, jNum) = list(map(str.strip, str.split(line, TAB)))[:6]

        # all columns required
        if orgID == '' or orgSym == '' or partID == '' or partSym == '' or interactionType == '' or jNum == '':
            reqColumnList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1

        # add the qtl org and part to the qtlPairDict - later we will check for reciprocals
        key = '%s|%s' % (orgID, partID)
        if key not in qtlPairDict:
            qtlPairDict[key] = []
        qtlPairDict[key].append('%s %s' % (lineNum, line))

        # Now verify each column

        # are the organizer and participant different?
        if orgID == partID:
            orgPartSameList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
        # is orgID a qtl ID?
        if orgID not in qtlLookupDict:
            badQtlIdList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
        else:
            # does orgSym match orgID?
           if orgSym != qtlLookupDict[orgID]:
                idSymDiscrepList.append('%s  %s' % (lineNum, line))
                hasFatalErrors = 1
        # is partID  a qtl ID?
        if partID not in qtlLookupDict:
            badQtlIdList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
        else:
            # does partSym match partID?
           if partSym != qtlLookupDict[partID]:
                idSymDiscrepList.append('%s  %s' % (lineNum, line))
                hasFatalErrors = 1
        # is interactionType a real term?
        if interactionType not in interactionLookupList:
            badIntTermList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
        
        if jNum not in jNumLookupList:
            badJnumList.append('%s  %s' % (lineNum, line))
            hasFatalErrors = 1
        
        line = fpInput.readline()
    # now check for reciprocals
    #for key in qtlPairDict:
    #    print('%s: %s' % (key, qtlPairDict[key]))
    for pair in qtlPairDict:
        (org, part) =  str.split(pair, '|')
        reciprocal = '%s|%s' % (part, org)
        if reciprocal not in qtlPairDict:
            #print('reciprocal not found')
            pList = qtlPairDict[pair]
            for p in pList:
                noReciprocalList.append(p)
            hasFatalErrors = 1
    return 0

# end runQcChecks() -------------------------------

def writeLoadReadyFile():
    for a in allelesToLoadList:
        fpLoadReady.write(a.toLoad())

    return 0

# end writeLoadReadyFile() -------------------------------

#
# Main
#
print('checkArgs(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
sys.stdout.flush()
checkArgs()

print('init(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
sys.stdout.flush()
init()

print('runQcChecks(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
sys.stdout.flush()
runQcChecks()

print('writeReport(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
writeReport()

# everything is fatal right now - keep to see if we will need
#print('writeLoadReadyFile(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
#writeLoadReadyFile()

print('closeFiles(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
sys.stdout.flush()
closeFiles()

db.useOneConnection(0)
print('done: %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))

if hasFatalErrors == 1 :
    sys.exit(2)
else:
    sys.exit(0)

