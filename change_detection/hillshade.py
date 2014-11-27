#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT_ALT = "/opt/Geodaten/ch/so/kva/hoehen/2002/dom/grid/dom.vrt"
VRT_NEU = "/opt/Geodaten/ch/so/kva/hoehen/2014/dom/dom.vrt" 
OUT_PATH = "/home/stefan/tmp/change_detection/"
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
    
    outfileName = os.path.join(TMPPATH, infileName)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + VRT + " " + outfileName
    os.system(cmd)
    #print cmd

    infile = outfileName
    outfile = os.path.join(TMPPATH, "tmp_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 50 -az 270 -compute_edges " + infile + " " + outfile
    os.system(cmd)
    #print cmd
    
    infile = outfile
    outfile = os.path.join(OUTPATH, infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX) + " " +  str(minY) + " " +  str(maxX) + " " +  str(maxY)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + infile + " " + outfile
    os.system(cmd)
    #print cmd

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    os.system(cmd)

infiles = os.path.join(OUTPATH, "*.tif")
outfile = os.path.join(OUTPATH, "dom_relief.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUTPATH, "dom_relief.vrt")
outfile = os.path.join(OUTPATH, "dom_relief_5m.tif")
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



