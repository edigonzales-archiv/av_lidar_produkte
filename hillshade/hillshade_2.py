#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen/2014/dtm/grid/50cm/dtm.vrt"
OUTPATH = "/home/stefan/tmp/hillshade/dtm_v2/"
TMPPATH = "/tmp/dtm_v2/"
BUFFER = 10

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
    
    print minX 
    print minY
    
    outfileName = os.path.join(TMPPATH, infileName)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + VRT + " " + outfileName
    #print cmd
    os.system(cmd)

    infile = outfileName
    outfile = os.path.join(TMPPATH, "tmp_1" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 30 -az 315 -compute_edges " + infile + " " + outfile
    #cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem slope -compute_edges " + infile + " " + outfile
    #cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -combined -alt 45 -az 315 -compute_edges " + infile + " " + outfile
    #print cmd
    os.system(cmd)
    
    infile = outfile
    outfile = os.path.join(TMPPATH, "tmp_1_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem color-relief " + infile +  " ramp_2.txt " + outfile
    #print cmd
    os.system(cmd)
    
    infile = outfile
    outfile = os.path.join(OUTPATH, infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te "  + str(minX) + " " +  str(minY) + " " +  str(maxX) + " " +  str(maxY)
    cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -co 'TILED=YES' -co 'PROFILE=GeoTIFF'"
    cmd += " -co 'INTERLEAVE=PIXEL' -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -r bilinear " + infile + " " + outfile
    #print cmd
    os.system(cmd)
    

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r average "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #print cmd
    os.system(cmd)

infiles = os.path.join(OUTPATH, "*.tif")
outfile = os.path.join(OUTPATH, "dtm_kombiniert.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUTPATH, "dtm_kombiniert.vrt")
outfile = os.path.join(OUTPATH, "dtm_kombiniert_5m.tif")
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



