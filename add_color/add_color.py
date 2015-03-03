#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys
import ntpath


ogr.UseExceptions()

LIDAR_PATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/lidar/"
ORTHO_SHP = "/opt/Geodaten/ch/so/kva/orthofoto/2014/rgb/12_5cm/ortho2014.shp"
TMP_PATH = "/home/stefan/tmp/color/"
BUFFER = 50

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
    os.system(cmd)
    
    outfile_color = os.path.join(TMP_PATH, "LAS_" + base_name + "_color.las")
    cmd = "las2las -i " + outfile_las + " --color-source " + ortho_file_name + " --file-format 1.2 --point-format 3 -o " + outfile_color
    os.system(cmd)

    outfile_color_laz = os.path.join(TMP_PATH, "LAS_" + base_name + ".laz")
    cmd = "laszip.exe -i " + outfile_color + " -o " + outfile_color_laz
    os.system(cmd)

    print cmd
    
    
    break
    
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    minX = int(env[0] + 0.001)
    minY = int(env[2] + 0.001)
    maxX = int(env[1] + 0.001)
    maxY = int(env[3] + 0.001)
    
    outfile = os.path.join(TMP_PATH, "input.tif")
    
