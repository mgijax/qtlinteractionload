#!/bin/sh

#
# This script is a wrapper around the process that loads 
# QTL to QTL Interaction relationships
#
#
#     qtlinteractionload.sh 
#

if [ -z ${MGICONFIG} ]
then
        MGICONFIG=/usr/local/mgi/live/mgiconfig
        export MGICONFIG
fi

. ${MGICONFIG}/master.config.sh

CONFIG=${QTLINTERACTIONLOAD}/qtlinteractionload.config

#
# verify & source the configuration file
#

if [ ! -r ${CONFIG} ]
then
    echo "Cannot read configuration file: ${CONFIG}"
    exit 1
fi

. ${CONFIG}

#
#  Source the DLA library functions.
#

if [ "${DLAJOBSTREAMFUNC}" != "" ]
then
    if [ -r ${DLAJOBSTREAMFUNC} ]
    then
        . ${DLAJOBSTREAMFUNC}
    else
        echo "Cannot source DLA functions script: ${DLAJOBSTREAMFUNC}" | tee -a ${LOG}
        exit 1
    fi
else
    echo "Environment variable DLAJOBSTREAMFUNC has not been defined." | tee -a ${LOG}
    exit 1
fi

#
# createArchive including OUTPUTDIR, startLog, getConfigEnv
# sets "JOBKEY"
#

preload ${OUTPUTDIR}

#
# rm all files/dirs from OUTPUTDIR
#

cleanDir ${OUTPUTDIR}

# There should be a "lastrun" file in the input directory that was created
# the last time the load was run for this input file. If this file exists
# and is more recent than the input file, the load does not need to be run.
#
LASTRUN_FILE=${INPUTDIR}/lastrun
if [ -f ${LASTRUN_FILE} ]
then
    if test ${LASTRUN_FILE} -nt ${INPUT_FILE_DEFAULT}
    then

        echo "Input file has not been updated - skipping load" | tee -a ${LOG_PROC}
        # set STAT for shutdown
        STAT=0
        echo 'shutting down'
        shutDown
        exit 0
    fi
fi

echo "" >> ${LOG_DIAG}
date >> ${LOG_DIAG}
echo "Run QC checks"  | tee -a ${LOG_DIAG}
${QTLINTERACTIONLOAD}/bin/qtlIntQC.sh ${INPUT_FILE_DEFAULT} live
STAT=$?
if [ ${STAT} -eq 1 ]
then
    checkStatus ${STAT} "An error occurred while generating the QC reports - See ${QC_LOGFILE}. qtlIntQC.sh"

    # run postload cleanup and email logs
    shutDown
fi

if [ ${STAT} -eq 2 ]
then
    checkStatus ${STAT} "QC errors detected. The load will not run. See ${QC_RPT}. qtlIntQC.sh"

    # run postload cleanup and email logs
    shutDown

fi

#
# run the load
#
echo "" >> ${LOG_DIAG}
date >> ${LOG_DIAG}
echo "Run qtlinteractionload.py"  | tee -a ${LOG_DIAG}
${PYTHON} ${QTLINTERACTIONLOAD}/bin/qtlinteractionload.py | tee -a ${LOG_DIAG}
STAT=$?
checkStatus ${STAT} "${QTLINTERACTIONLOAD}/bin/qtlinteractionload.py"

#
# Touch the "lastrun" file to note when the load was run.
#
if [ ${STAT} = 0 ]
then
    touch ${LASTRUN_FILE}
fi

# run postload cleanup and email logs

shutDown

