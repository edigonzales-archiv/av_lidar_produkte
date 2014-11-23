#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

BASEPATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/"
OUTPATH = "/home/stefan/tmp/ndsm/"

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
    
    infileA = os.path.join(BASEPATH, "dom", infileName)
    infileB = os.path.join(BASEPATH, "dtm", infileName)
    outfile = os.path.join(OUTPATH, infileName)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infileA + " -B " + infileB + " --outfile " + outfile
    cmd += " --calc=\"A-B\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)

infiles = os.path.join(OUTPATH, "*.tif")
outfile = os.path.join(OUTPATH, "ndsm.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUTPATH, "ndsm.vrt")
outfile = os.path.join(OUTPATH, "ndsm_5m.tif")
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
