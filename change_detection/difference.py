#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT_ALT = "/opt/Geodaten/ch/so/kva/hoehen/2002/dom/grid/dom.vrt"
VRT_NEU = "/opt/Geodaten/ch/so/kva/hoehen/2014/dom/dom.vrt"
OUT_PATH = "/home/stefan/tmp/change_detection/50cm"
TMP_PATH = "/tmp/"

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
    
    outfile = os.path.join(TMP_PATH, "alt_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX) + " " +  str(minY) + " " +  str(maxX) + " " +  str(maxY)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + VRT_ALT + " " + outfile
    os.system(cmd)
    #print cmd

    outfile = os.path.join(TMP_PATH, "neu_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX) + " " +  str(minY) + " " +  str(maxX) + " " +  str(maxY)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + VRT_NEU + " " + outfile
    os.system(cmd)
    #print cmd

    infileA = os.path.join(TMP_PATH, "neu_" + infileName)
    infileB = os.path.join(TMP_PATH, "alt_" + infileName)
    outfile = os.path.join(OUT_PATH, infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infileA + " -B " + infileB + " --outfile " + outfile
    cmd += " --calc=\"A-B\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    os.system(cmd)
    #print cmd
    
    cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest"
    cmd += " --config COMPRESS_OVERVIEW LZW --config GDAL_TIFF_OVR_BLOCKSIZE 512"
    cmd += " " + outfile + " 2 4 8 16 32 64 128"
    os.system(cmd)
    #print cmd


infiles = os.path.join(OUT_PATH, "*.tif")
outfile = os.path.join(OUT_PATH, "change_detection.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "change_detection.vrt")
outfile = os.path.join(OUT_PATH, "change_detection_5m.tif")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -tr 5.0 5.0 -of GTiff"
cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
cmd += " -co 'COMPRESS=LZW' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'" 
cmd += " -wo NUM_THREADS=ALL_CPUS -s_srs epsg:21781 -t_srs epsg:21781"
cmd += " " + infile + " " + outfile
os.system(cmd)

cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest"
cmd += " --config COMPRESS_OVERVIEW LZW --config GDAL_TIFF_OVR_BLOCKSIZE 512"
cmd += " " + outfile + " 2 4 8 16 32 64 128"
os.system(cmd)


