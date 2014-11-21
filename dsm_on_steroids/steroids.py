#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

BUILDINGS = "buildings.shp"
BUFFER_DISTANCE = "2"
BASEPATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/"
NDVIPATH = "/opt/Geodaten/ch/so/kva/orthofoto/2014/ndvi/12_5cm/"
OUTPATH = "/home/stefan/tmp/steroids/"

# the loop...

shp = ogr.Open("tileindex/lidar2014_einzeln.shp")
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
    
    # difference: dom - dtm = nDSM
    infileA = os.path.join(BASEPATH, "dom", infileName)
    infileB = os.path.join(BASEPATH, "dtm", infileName)
    outfile = os.path.join(OUTPATH, "diff_dom_dtm", "diff_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py -A " + infileA 
    cmd += " -B " + infileB + " --outfile " + outfile + " --calc=\"A-B\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)
    
    
    
    # doch erst am schluss?!
    # NDVI
    infile = os.path.join(NDVIPATH, infileName[0:6] + "_12_5cm.tif")
    outfile = os.path.join(OUTPATH, "ndvi", infileName[0:6] + "_50cm.tif")
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -tr 0.5 0.5 " + infile + " " + outfile
    print cmd
    print infile
    print outfile
    os.system(cmd)
    
    
    
    
    
    # export buildings and single objects from database
    polygon = "ST_PolygonFromText('POLYGON(("+minX+" " +minY+","+maxX+" "+minY+","+maxX+" "+maxY+","+minX+" "+maxY+","+minX+" "+minY+"))',21781)"
    
    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -overwrite " + BUILDINGS
    cmd +=" PG:\"dbname='xanadu2' host='localhost' port='5432' user='mspublic' password='mspublic'\"" 
    cmd += " -sql \"SELECT ogc_fid, art, ST_Buffer(geometrie, "+BUFFER_DISTANCE+") FROM av_mopublic.bodenbedeckung__boflaeche"
    cmd += " WHERE geometrie && " + polygon 
    cmd += " AND ST_Intersects(geometrie, " + polygon + ")"
    cmd += " AND art = 'Gebaeude'\""
    #os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -append " + BUILDINGS
    cmd +=" PG:\"dbname='xanadu2' host='localhost' port='5432' user='mspublic' password='mspublic'\"" 
    cmd += " -sql \"SELECT ogc_fid, typ as art, ST_Buffer(geometrie, "+BUFFER_DISTANCE+") FROM av_mopublic.einzelobjekte__flaechenelement"
    cmd += " WHERE geometrie && " + polygon 
    cmd += " AND ST_Intersects(geometrie, " + polygon + ")"
    cmd += " AND typ IN ('Unterstand','uebriger_Gebaeudeteil','Silo_Turm_Gasometer','Hochkamin')"
    cmd += " AND geometrie IS NOT NULL\""
    #os.system(cmd)
        
    # get only raster within buildings
    infile = os.path.join(OUTPATH, "diff_dom_dtm", "diff_" + infileName)
    outfile = os.path.join(OUTPATH, "diff_dom_dtm_gebaeude", "geb_diff_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -cutline " + BUILDINGS + " " + infile + " " + outfile
    #os.system(cmd)
    
    # nDSM - Raster-Buildings = Forest
    infileA = os.path.join(OUTPATH, "diff_dom_dtm", "diff_" + infileName)
    infileB = os.path.join(OUTPATH, "diff_dom_dtm_gebaeude", "geb_diff_" + infileName)
    outfile = os.path.join(OUTPATH, "diff_dom_dtm_wald", "diff_" + infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py -A " + infileA 
    cmd += " -B " + infileB + " --outfile " + outfile + " --calc=\"A-B\""
    cmd += " --NoDataValue=-99 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #os.system(cmd)

    



