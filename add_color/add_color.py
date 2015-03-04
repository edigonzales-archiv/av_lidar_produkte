#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys
import ntpath


ogr.UseExceptions()

#LIDAR_PATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/lidar/"
#ORTHO_SHP = "/opt/Geodaten/ch/so/kva/orthofoto/2014/rgb/12_5cm/ortho2014.shp"
#TMP_PATH = "/home/stefan/tmp/color/"
LIDAR_PATH = "/home/stefan/mr_candie_nas/Geodaten/ch/so/agi/hoehen/2014/lidar/"
ORTHO_SHP = "/home/stefan/mr_candie_nas/Geodaten/ch/so/agi/orthofoto/2014/rgb/12_5cm/ortho2014.shp"
ORTHO_PATH = "/home/stefan/mr_candie_nas/Geodaten/ch/so/agi/orthofoto/2014/rgb/12_5cm/"
TARGET_PATH = "/home/stefan/mr_candie_nas/Geodaten/ch/so/agi/hoehen/2014/lidar/color/"
TMP_PATH = "/home/stefan/tmp/"

shp = ogr.Open(ORTHO_SHP)
layer = shp.GetLayer(0)


for feature in layer:
    ortho_file_name = feature.GetField('location')
    base_name = (ntpath.basename(ortho_file_name)[:-4])[:6]
    print "**********************: " + base_name
    
    laz_file_name = os.path.join(LIDAR_PATH, "LAS_" + base_name + ".laz")
    print laz_file_name
    
    if not os.path.isfile(laz_file_name): 
        continue


    print "vorhanden"
    
    outfile_las = os.path.join(TMP_PATH, "LAS_" + base_name + ".las")
    cmd = "laszip.exe -i " + laz_file_name + " -o " + outfile_las
    #os.system(cmd)
    #print cmd

    ortho_file_name = os.path.join(ORTHO_PATH, base_name + "_12_5cm.tif")
    outfile_color = os.path.join(TMP_PATH, "LAS_color.las")
    cmd = "las2las -i " + laz_file_name + " --color-source " + ortho_file_name + " --file-format 1.2 --point-format 3 -o " + outfile_color
    os.system(cmd)
    #print cmd

    outfile_color_laz = os.path.join(TARGET_PATH, "LAS_" + base_name + ".laz")
    cmd = "laszip.exe -i " + outfile_color + " -o " + outfile_color_laz
    os.system(cmd)
    #print cmd
    
    
    #break
    
    
