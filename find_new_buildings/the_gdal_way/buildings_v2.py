#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen/differenzen/2014vs2002/dom/grid/50cm/change_detection.vrt"
INPATH_NDSM = "/opt/Geodaten/ch/so/kva/hoehen/2014//ndsm/50cm/"
OUTPATH_NDSM_RECLASS = "/home/stefan/tmp/ndsm_reclass/"
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
    

    infile = os.path.join(INPATH_NDSM, infileName)
    outfile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp1.tif")

    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py --overwrite "
    cmd += " -A " + infile + " --outfile " + outfile
    cmd += " --calc=\"(A<2)*0 + (A>=2)*1\""
    cmd += " --NoDataValue=0 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #cmd += " --co 'NBITS=1'"
    print(cmd)
    os.system(cmd)
    
    infile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp1.tif")
    outfile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp2.tif")
        
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -tr 1.0 1.0 -of GTiff "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'" 
    cmd += " -wo NUM_THREADS=ALL_CPUS -s_srs epsg:21781 -t_srs epsg:21781"
    cmd += " " + infile + " " + outfile
    print(cmd)
    os.system(cmd)

    infile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp2.tif")
    outfile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.shp")
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_polygonize.py"
    cmd += " " + infile + " -f \"ESRI Shapefile\" " + outfile
    print(cmd)
    os.system(cmd)
    
    infile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.shp")
    outfile = os.path.join(OUTPATH_NDSM_RECLASS, "ndsm.sqlite")
    
    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr "
    cmd += " -f \"SQLite\" -dsco SPATIALITE=YES -append -gt 65536 --config OGR_SQLITE_SYNCHRONOUS OFF "
    cmd += " -dialect SQLITE -sql 'SELECT 9999 as gem_bfs, ST_PointOnSurface(GEOMETRY) FROM ndsm_tmp3 WHERE ST_Area(GEOMETRY) > 2' " 
    cmd += " -s_srs epsg:21781 -t_srs epsg:21781 " + outfile + " " + infile + " -nln ndsm_centroids"
    print(cmd)
    os.system(cmd)


    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp1.tif"))
    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp2.tif"))
    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.shp"))
    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.shx"))
    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.dbf"))
    os.system("rm " + os.path.join(OUTPATH_NDSM_RECLASS, "ndsm_tmp3.prj"))
    #break


