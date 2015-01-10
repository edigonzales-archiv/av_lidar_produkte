#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen//differenzen/2014vs2002/dom/grid/50cm/change_detection.vrt"
INPATH = "/home/stefan/tmp/steroids/ndvi_50cm/"
OUTPATH = "/home/stefan/tmp/ndvi_reclass_15/"
TMPPATH = "/tmp/diff_reclass/"
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
    
    
    infile = os.path.join(INPATH, infileName)
    outfile = os.path.join(OUTPATH, infileName)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infile + " --outfile " + outfile
    cmd += " --calc=\"(A<15)*1 + (A>=15)*0\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    print(cmd)
    os.system(cmd)




