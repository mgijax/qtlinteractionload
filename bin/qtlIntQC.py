
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
loadReadyFile = os.getenv("INPUT_FILE_QC")
fpLoadReady = None

# for bcp
bcpin = '%s/bin/bcpin.csh' % os.environ['PG_DBUTILS']
server = os.environ['MGD_DBSERVER']
database = os.environ['MGD_DBNAME']

# lines seen in the input file
distinctLineList = []

# lines that pass QC
goodLineList = []


#
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
    print('inputFile: %s' % inputFile)
    return

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

    return

# end init() -------------------------------

# Purpose: load lookups for verification
# Returns: Nothing
# Assumes: 
# Effects: queries a database, modifies global variables
#

def loadLookups(): 
 
    return

# end loadLookups() -------------------------------

#
# Purpose: Open input and output files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables.
# Throws: Nothing
#
def openFiles ():
    global fpInput, fpLoadReady, fpQcRpt

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
    try:
        fpLoadReady = open(loadReadyFile, 'w')
    except:
        print('Cannot open load ready file: %s' % loadReadyFile)
        sys.exit(1)

    #
    # Open QC report file
    #
    try:
        fpQcRpt = open(qcRptFile, 'w')
    except:
        print('Cannot open report file: %s' % qcRptFile)
        sys.exit(1)

    return

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
    
    return

# end writeReport() -------------------------------

#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Modifies global variables
# Throws: Nothing
#
def closeFiles ():
    global fpInput, fpLoadReady, fpQcRpt
    fpInput.close()
    fpLoadReady.close()
    fpQcRpt.close()

    return

# end closeFiles) -------------------------------

    #
    # Purpose: run all QC checks
    # Returns: Nothing
    # Assumes: file descriptors have been initialized
    # Effects: writes reports and the load ready file to file system
    # Throws: Nothing
    #

def runQcChecks():
    
    header = fpInput.readline()
    line = fpInput.readline()
    while line:
        # do qc
        line = fpInput.readline()
    return

# end runQcChecks() -------------------------------

def writeLoadReadyFile():
    for a in allelesToLoadList:
        fpLoadReady.write(a.toLoad())

    return

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

print('writeLoadReadyFile(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
writeLoadReadyFile()

print('closeFiles(): %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
sys.stdout.flush()
closeFiles()

db.useOneConnection(0)
print('done: %s' % time.strftime("%H.%M.%S.%m.%d.%y", time.localtime(time.time())))
if hasSkipErrors and hasWarnErrors:
    sys.exit(2)
elif hasSkipErrors: 
    sys.exit(3)
elif hasWarnErrors:
    sys.exit(4)
else:
    sys.exit(0)

