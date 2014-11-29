#!/bin/bash

for FILE in /home/stefan/tmp/Lidar/01_LAS/*.las
do
  BASENAME=$(basename $FILE .las)
  OUTFILE=/opt/Geodaten/ch/so/kva/hoehen/2014/lidar/${BASENAME}.laz
  echo "Processing: ${BASENAME}"
  if [ -f $OUTFILE ] #skip if exists
  then
    echo "Skipping: $OUTFILE"
  else
    /home/stefan/Apps/laszip/laszip.exe -i $FILE -o $OUTFILE
  fi
done
