#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

BUILDINGS = "buildings.shp"
BUFFER_DISTANCE = "2"
BASEPATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/"
NDVIPATH_2014 = "/opt/Geodaten/ch/so/kva/orthofoto/2014/ndvi/12_5cm/"
NDVIPATH_2013 = "/opt/Geodaten/ch/so/kva/orthofoto/2013/ndvi/12_5cm/"
NDVIPATH_2012 = "/opt/Geodaten/ch/so/kva/orthofoto/2012/ndvi/12_5cm/"
OUTPATH = "/home/stefan/tmp/steroids/"

# the loop...

shp = ogr.Open("../tileindex/lidar2014_einzeln.shp")
layer = shp.GetLayer(0)


for feature in layer:
    infileName = feature.GetField('location')
    print "**********************: " + infileName
    
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    minX = str(int(env[0] + 0.001))
    minY = str(int(env[2] + 0.001))
    maxX = str(int(env[1] + 0.001))
    maxY = str(int(env[3] + 0.001))
        
    # NDVI 2014 - 2012
    
    infile = os.path.join(NDVIPATH_2012, infileName[0:6] + "_12_5cm.tif")
    outfile = os.path.join(OUTPATH, "ndvi", infileName[0:6] + "_50cm.tif")
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -tr 0.5 0.5 " + infile + " " + outfile
    os.system(cmd)
    
    infile = os.path.join(NDVIPATH_2013, infileName[0:6] + "_12_5cm.tif")
    outfile = os.path.join(OUTPATH, "ndvi", infileName[0:6] + "_50cm.tif")
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -tr 0.5 0.5 " + infile + " " + outfile
    os.system(cmd)

    infile = os.path.join(NDVIPATH_2014, infileName[0:6] + "_12_5cm.tif")
    outfile = os.path.join(OUTPATH, "ndvi", infileName[0:6] + "_50cm.tif")
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -tr 0.5 0.5 " + infile + " " + outfile
    os.system(cmd)



