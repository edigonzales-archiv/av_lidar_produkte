#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen/2002/dom/grid/dom.vrt"
DOM_PATH = "/opt/Geodaten/ch/so/kva/hoehen/2002/dom/grid/"
OUT_PATH = "/home/stefan/tmp/dom_2002/hillshade_50/"
TMP_PATH = "/tmp/"
BUFFER = 20

shp = ogr.Open("../tileindex/dtm_dom_idx.shp")
layer = shp.GetLayer(0)


for feature in layer:
    nummer = feature.GetField('nummer')
    
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    minX = int(env[0] + 0.001)
    minY = int(env[2] + 0.001)
    maxX = int(env[1] + 0.001)
    maxY = int(env[3] + 0.001)

    infileBaseName = "dom" + nummer.replace("-", "")
    domfile = os.path.join(DOM_PATH, infileBaseName + ".tif")
    
    if os.path.isfile(domfile):
        outfile = os.path.join(TMP_PATH, infileBaseName + "_tmp_1.tif")
        print outfile

        cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
        cmd += " -tr 2.0 2.0 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
        cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
        cmd += " -r bilinear " + VRT + " " + outfile
        os.system(cmd)
        #print cmd

        infile = os.path.join(TMP_PATH, infileBaseName + "_tmp_1.tif")
        outfile = os.path.join(TMP_PATH, infileBaseName + "_tmp_2.tif")
        cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 50 -az 270 -compute_edges " + infile + " " + outfile
        os.system(cmd)
        #print cmd
    
        infile = os.path.join(TMP_PATH, infileBaseName + "_tmp_2.tif")
        outfile = os.path.join(OUT_PATH, infileBaseName + ".tif")
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
        #print cmd

infiles = os.path.join(OUT_PATH, "*.tif")
outfile = os.path.join(OUT_PATH, "dom.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
#print cmd
os.system(cmd)

infile = os.path.join(OUT_PATH, "dom.vrt")
outfile = os.path.join(OUT_PATH, "dom_5m.tif")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -tr 5.0 5.0 -of GTiff"
cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
cmd += " -co 'COMPRESS=LZW' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'" 
cmd += " -wo NUM_THREADS=ALL_CPUS -s_srs epsg:21781 -t_srs epsg:21781"
cmd += " " + infile + " " + outfile
#print cmd
os.system(cmd)

cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest"
cmd += " --config COMPRESS_OVERVIEW LZW --config GDAL_TIFF_OVR_BLOCKSIZE 512"
cmd += " " + outfile + " 2 4 8 16 32 64 128"
#print cmd
os.system(cmd)
