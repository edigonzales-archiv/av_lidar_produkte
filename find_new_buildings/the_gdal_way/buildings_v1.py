#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen//differenzen/2014vs2002/dom/grid/50cm/change_detection.vrt"
INPATH_DIFF = "/opt/Geodaten/ch/so/kva/hoehen/differenzen/2014vs2002/dom/grid/50cm/"
INPATH_NDVI = "/home/stefan/tmp/ndvi_reclass_15/"
OUTPATH_RECLASS = "/home/stefan/tmp/diff_reclass/"
OUTPATH_DIFF_NDVI = "/home/stefan/tmp/diff_ndvi/"
TMPPATH = "/tmp/diff_reclass/"
BUFFER = 10

shp = ogr.Open("../../tileindex/lidar2014_einzeln.shp")
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
    
    
    infile = os.path.join(INPATH_DIFF, infileName)
    outfile = os.path.join(OUTPATH_RECLASS, infileName)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infile + " --outfile " + outfile
    cmd += " --calc=\"(A<5)*0 + (A>=5)*1\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #cmd += " --co 'NBITS=1'"
    #print(cmd)
    #os.system(cmd)

    infileA = os.path.join(OUTPATH_RECLASS, infileName)
    infileB = os.path.join(INPATH_NDVI, infileName)
    outfile = os.path.join(OUTPATH_DIFF_NDVI, infileName)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infileA + " -B " + infileB + " --outfile " + outfile
    cmd += " --calc=\"((A+B)<2)*0 + ((A+B)>=2)*A\""
    cmd += " --NoDataValue=0 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    print(cmd)
    os.system(cmd)

    #break


    infile = os.path.join(OUTPATH_DIFF_NDVI, infileName)
    outfile = os.path.join(OUTPATH_RECLASS, infileName[0:11] + ".shp")
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_polygonize.py"
    cmd += " " + infile + " -f ESRI Shapefile " + outfile + " " + infileName[0:11]
    print(cmd)
    #os.system(cmd)
    
    break


