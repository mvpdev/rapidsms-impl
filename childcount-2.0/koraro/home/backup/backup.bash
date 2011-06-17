#!/bin/bash

# Koraro Backup Script
# 17 June 2011, Henry Corrigan-Gibbs
#
# Dumps OMRS and CC+ DB, compresses them with gzip
# and copies them to the Windows file server.

FILESERVER=192.168.0.2
OMRS_IP=intomrs
DATE=`date +%F_%H-%M-%S`
GZIP_EXT=".gz"

BACKUP_DIR=/home/mvp/backup/
RSMS_FILENAME=childcount-$DATE.sql
OMRS_FILENAME=omrs-$DATE.sql

RSMS_FILEPATH=$BACKUP_DIR$RSMS_FILENAME
OMRS_FILEPATH=$BACKUP_DIR$OMRS_FILENAME

RSMS_FILENAME_COMP=$RSMS_FILENAME$GZIP_EXT
OMRS_FILENAME_COMP=$OMRS_FILENAME$GZIP_EXT

RSMS_FILEPATH_COMP=$RSMS_FILENAME_COMP$GZIP_EXT
OMRS_FILEPATH_COMP=$OMRS_FILENAME_COMP$GZIP_EXT

LOGFILE=/home/mvp/backup/backup.log

echo "=== Backup operations for date: $DATE ===" &>>$LOGFILE

# Dump CC+ DB
echo "Dumping CC+ DB" &>> $LOGFILE
mysqldump -u childcount -pchildcount childcount > $RSMS_FILEPATH 2>> $LOGFILE
echo "Finished dumping CC+ DB" &>> $LOGFILE

# Dump OpenMRS DB
echo "Dumping OpenMRS DB" &>> $LOGFILE
mysqldump -u openmrs -h $OMRS_IP -popenmrs openmrs > $OMRS_FILEPATH 2>> $LOGFILE
echo "Finished dumping OpenMRS DB" &>> $LOGFILE

# Compress CC+ DB
echo "Compressing CC+ DB $RSMS_FILEPATH => $RSMS_FILEPATH_COMP" &>> $LOGFILE
gzip $RSMS_FILEPATH 2>> $LOGFILE
echo "Finished compressing CC+ DB $RSMS_FILEPATH => $RSMS_FILEPATH_COMP" &>> $LOGFILE

# Compress OpenMRS DB
echo "Compressing OpenMRS DB $OMRS_FILEPATH => $OMRS_FILEPATH_COMP" &>> $LOGFILE
gzip $OMRS_FILEPATH 2>> $LOGFILE
echo "Finished compressing OpenMRS DB $OMRS_FILEPATH => $OMRS_FILEPATH_COMP" &>> $LOGFILE

# Transfer CC+ DB
echo "Transfering $RSMS_FILENAME" &>> $LOGFILE
smbclient \\\\server\\ChildCount -U Administrator -c "put $RSMS_FILENAME_COMP" pp@@ssword &>> $LOGFILE
echo "Finished transfering $RSMS_FILENAME_COMP" &>> $LOGFILE

# Transfer OpenMRS DB
echo "Transfering $OMRS_FILENAME_COMP" &>> $LOGFILE
smbclient \\\\server\\ChildCount -U Administrator -c "put $OMRS_FILENAME_COMP" pp@@ssword &>> $LOGFILE
echo "Finished transfering $OMRS_FILENAME_COMP" &>> $LOGFILE

END_DATE=`date +%F~%T`
echo "Script finished at $END_DATE"
