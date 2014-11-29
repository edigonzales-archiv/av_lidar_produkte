#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen/2014/dtm/grid/50cm/dtm.vrt"
OUT_PATH = "/home/stefan/tmp/contour/"
TMP_PATH = "/tmp/"
BUFFER = 50

shp = ogr.Open("../tileindex/lidar2014_einzeln.shp")
layer = shp.GetLayer(0)


for feature in layer:
    infileName = feature.GetField('location')
    print "**********************: " + infileName
    
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    minX = int(env[0] + 0.001)
    minY = int(env[2] + 0.001)
    maxX = int(env[1] + 0.001)
    maxY = int(env[3] + 0.001)
    
    outfile = os.path.join(TMP_PATH, "input.tif")
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te" 
    cmd += " " + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -r bilinear "
    cmd += " " + VRT + " " + outfile;
    #print cmd    
    os.system(cmd);


    infile = os.path.join(TMP_PATH, "input.tif")
    outfile = os.path.join(TMP_PATH, "output.tif")
        
    for i in range(10):
        cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781"
        cmd += " -r cubicspline " + infile + " " + outfile
        os.system(cmd)
        os.system("cp " + outfile + " " + infile)

    infile = os.path.join(TMP_PATH, "input.tif")
    outfile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_contour -b 1 -3d -a elev -i 1.0 " + infile + " " + outfile
    #print cmd
    os.system(cmd)
    os.system("rm " + infile)
    
    clip = geom.ExportToWkt()
    
    infile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
    outfile = os.path.join(TMP_PATH, "contour_tmp_2.shp")

    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -clipsrc '" + clip + "' " + outfile + " " + infile
    os.system(cmd)

    infile = os.path.join(TMP_PATH, "contour_tmp_2.shp")
    #outfile = os.path.join(TMP_PATH, "contour_tmp_3.shp")
    outfile = os.path.join(TMP_PATH, "contour.shp")

    #cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -clipsrc ../data/kantonsgrenzen/kantonsgrenze.shp "
    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -append -clipsrc ../data/kantonsgrenzen/kantonsgrenze.shp "
    cmd += " " + outfile + " " + infile
    os.system(cmd)

    infile = os.path.join(TMP_PATH, "contour_tmp_3.shp")
    outfile = os.path.join(TMP_PATH, "contour.shp")
    
    #cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -append -dialect SQLITE"
    #cmd += " " + outfile + " " + infile + " -sql \"SELECT * FROM contour_tmp_3 WHERE ST_Length(GEOMETRY) > 50\""  
    #print cmd
