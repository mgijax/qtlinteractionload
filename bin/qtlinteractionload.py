#  Purpose:
#
#      Load QTL to QTL Interaction relationships
#
#  Inputs:
#
#       File of relationships
#
#  Outputs:
#
#	1 BCP file:
#	A pipe-delimited file:
#       	MGI_Relationship.bcp
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#      2:  bcp fails
#
#  Assumes:
#
#	
#  Implementation:
#
#      1) Validate the arguments to the script.
#      2) Perform initialization steps.
#      3) Parse input file
#      4) Resolve MGI IDs to QTL marker keys
#      5) Resolve interaction terms to term keys
#      5) Write out to relationship bcp
#      6) Delete existing relationships
#      7) BCP in new relationships:
#
# History:
#
# sc	06/22/2022
#	- WTS2-284
#

import sys
import os
import string
import db
import mgi_utils

#db.setTrace()

CRT = '\n'
TAB = '\t'

# from configuration file
user = os.environ['MGD_DBUSER']
passwordFileName = os.environ['MGD_DBPASSWORDFILE']
outputDir = os.environ['OUTPUTDIR']
reportDir = os.environ['RPTDIR']

inputFileName = os.getenv('INPUT_FILE_DEFAULT')
bcpFile = 'MGI_Relationship.bcp'
relationshipFileName = '%s/%s' % (outputDir, bcpFile)

cdate  = mgi_utils.date("%m/%d/%Y")
fpRelationship = ''
fpInput = ''

# The category key 'qtl_to_candidate_gene'
catKey = 1010

# the qualifier key 'Not Specified'
qualKey = 11391898

# the evidence key 'Not Specified'
evidKey = 17396909

# qtl candidate geneload user key
userKey = 1632

# database primary keys, will be set to the next available from the db
nextRelationshipKey = 1000	# MGI_Relationship._Relationship_key

#
# Purpose: open files, create db connection, gets max keys from the db
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables, exits if a file can't be opened,
#
def init():

    global nextRelationshipKey

    #
    # Open input and output files
    #
    openFiles()

    #
    # create database connection
    #
    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFileName)

    #
    # get next MGI_Relationship key
    #
    results = db.sql('''select nextval('mgi_relationship_seq') as nextKey''', 'auto')
    if results[0]['nextKey'] is None:
        nextRelationshipKey = 1000
    else:
        nextRelationshipKey = results[0]['nextKey']

    return 0

# end init() -------------------------------

# Purpose: Open input/output files.
# Returns: exit 1 if cannot open input or output file
# Assumes: Nothing
# Effects: sets global variables, exits if a file can't be opened
#
def openFiles ():

    global fpRelationship, fpInput

    try:
        fpInput = open(inputFileName, 'r')
    except:
        print(('Cannot open input file: %s' % inputFileName))
        sys.exit(1)

    try:
        fpRelationship = open(relationshipFileName, 'w')
    except:
        print(('Cannot open relationships bcp file: %s' % relationshipFileName))
        sys.exit(1)

    return 0

# end openFiles() -------------------------------

#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
#
def closeFiles ():

    global fpRelationship, fpInput

    fpRelationship.close()
    fpInput.close()

    return 0

# end closeFiles() -------------------------------

# Purpose: read input, resolve to keys, write to bcp file
# Returns: None
# Assumes: None
# Effects: None
#

def processRelationships():
    header = fpInput.readline()
    line = fpInput.readline()
    while line:
        print(line)
        line = fpInput.readline()
        
    return 0

# end processRelationships ----------------------

# Purpose: write QC report
# Returns: None
# Assumes: None
# Effects: None
#

def writeReports():
    # stub in case we end up needing it
    return 0

# Purpose: deletes existing relationships
# Returns: None
# Assumes: None
# Effects: None
#
def doDeletes():
    db.sql('''delete from MGI_Relationship where _CreatedBy_key = %s ''' % userKey, None)
    db.commit()
    db.useOneConnection(0)

    return 0

# end doDeletes() -------------------------------------

# Purpose: loads bcp file
# Returns: exist 2 if bcp fails
# Assumes: None
# Effects: None
#
def bcpFiles():

    bcpCommand = os.environ['PG_DBUTILS'] + '/bin/bcpin.csh'

    bcpCmd = '%s %s %s %s %s %s "|" "\\n" mgd' % \
            (bcpCommand, db.get_sqlServer(), db.get_sqlDatabase(), 'MGI_Relationship', outputDir, bcpFile)
    print(bcpCmd)
    rc = os.system(bcpCmd)

    if rc != 0:
        closeFiles()
        sys.exit(2)
    # update mgi_relationship auto-sequence
    db.sql(''' select setval('mgi_relationship_seq', (select max(_Relationship_key) from MGI_Relationship)) ''', None)

    return 0

# end bcpFiles() -------------------------------------

#
# Main
#

print('%s' % mgi_utils.date())
print ('init()')
if init() != 0:
    exit(1, 'Error in  init \n' )

print('%s' % mgi_utils.date())
print('processRelationships()')
# determine qtl candidate genes and write to bcp
if processRelationships() != 0:
    exit(1, 'Error in  processRelationships \n' )

#print('%s' % mgi_utils.date())
#print('writeReports()')
## write out info for each bucket of relationships
#if writeReports() != 0:
#    exit(1, 'Error in  writeReports \n' )

print('%s' % mgi_utils.date())
print('doDeletes()')
# delete existing relationships
if doDeletes() != 0:
    exit(1, 'Error in  doDeletes \n' )

print('%s' % mgi_utils.date())
print('closeFiles()')
# close all output files
if closeFiles() != 0:
    exit(1, 'Error in  closeFiles \n' )

print('%s' % mgi_utils.date())
print('bcpFiles()')
# bcp the relationships
if bcpFiles() != 0:
    exit(1, 'Error in  bcpFiles \n' )

print('%s' % mgi_utils.date())
print('done')
sys.exit(0)
