#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

BUILDINGS = "buildings.shp"
BUILDINGS_UNION = "buildings_union.shp"
BUFFER_DISTANCE = "2"

NDSM_PATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/ndsm/"
OUT_PATH = "/home/stefan/tmp/steroids/"

BASEPATH = "/opt/Geodaten/ch/so/kva/hoehen/2014/"
NDVIPATH_2014 = "/opt/Geodaten/ch/so/kva/orthofoto/2014/ndvi/12_5cm/"
NDVIPATH_2013 = "/opt/Geodaten/ch/so/kva/orthofoto/2013/ndvi/12_5cm/"
NDVIPATH_2012 = "/opt/Geodaten/ch/so/kva/orthofoto/2012/ndvi/12_5cm/"

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
    
    ## Buildings
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
    cmd += " AND typ IN ('Unterstand','uebriger_Gebaeudeteil','Silo_Turm_Gasometer','Hochkamin','Mauer','wichtige_Treppe')"
    cmd += " AND geometrie IS NOT NULL\""
    #os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -overwrite " + BUILDINGS_UNION
    cmd += " " + BUILDINGS + " -dialect SQLITE -sql \"SELECT 1 as ogc_fid,"
    cmd += " ST_Union(GEOMETRY) as geom FROM buildings\""
    #os.system(cmd)
        
    # get only raster within buildings
    # We have to set dstnodata to none. 'nodata' will be 0. 
    # Or we get problems with gdal_calc.
    infile = os.path.join(NDSM_PATH, infileName)
    outfile = os.path.join(OUT_PATH, "buildings", "dom", infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -s_srs epsg:21781 -t_srs epsg:21781 "
    cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF' -co 'INTERLEAVE=PIXEL'"
    cmd += " -co 'COMPRESS=DEFLATE' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"
    cmd += " -dstnodata None"
    cmd += " -cutline " + BUILDINGS_UNION + " " + infile + " " + outfile
    #os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)
    
    # ok, eigentlich müssten wir hier wieder über das VRT gehen...
    # jetzt bei buildings nodata=0 setzen, sonst wird überall das
    # relief gerechnet.
    # Wieder rückgängig machen?
    infile = os.path.join(OUT_PATH, "buildings", "dom", infileName)
    infile = os.path.join(OUT_PATH, "buildings", "dom", infileName)
    outfile = os.path.join(OUT_PATH, "buildings", "hillshade", infileName)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_edit.py -a_nodata 0 " + infile
    #os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 60 -az 270 -compute_edges " + infile + " " + outfile
    #os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)
    
    
    ## Forest
    # 1) NDSM - Buildings = Forest_DOM
    infileA = os.path.join(NDSM_PATH, infileName)
    infileB = os.path.join(OUT_PATH, "buildings", infileName)
    outfile = os.path.join(OUT_PATH, "forest", "dom", infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdal_calc.py "
    cmd += " -A " + infileA + " -B " + infileB + " --outfile " + outfile 
    cmd += " --calc=\"((A-B)<0.5)*0 + ((A-B)>=0.5)*(A-B)\""
    cmd += " --NoDataValue=0 --co 'TILED=YES' --co 'PROFILE=GeoTIFF'"
    cmd += " --co 'INTERLEAVE=PIXEL' --co 'COMPRESS=DEFLATE'" 
    cmd += " --co 'BLOCKXSIZE=512' --co 'BLOCKYSIZE=512'"
    #print cmd
    #os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)
    
    # 2) Forest_DOM -> Hillshading (hillshade forest above blue rivers)
    # ok, eigentlich müssten wir hier wieder über das VRT gehen...
    infile = os.path.join(OUT_PATH, "forest", "dom", infileName)
    outfile = os.path.join(OUT_PATH, "forest", "hillshade", infileName)
    cmd = "/usr/local/gdal/gdal-dev/bin/gdaldem hillshade -alt 60 -az 270 -compute_edges " + infile + " " + outfile
    #os.system(cmd)

    cmd = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest "
    cmd += "--config COMPRESS_OVERVIEW DEFLATE --config GDAL_TIFF_OVR_BLOCKSIZE 512 " 
    cmd += outfile + " 2 4 8 16 32 64 128"
    #os.system(cmd)

    
#/usr/local/gdal/gdal-dev/bin/gdal_calc.py -A diff_603231_50cm.tif --outfile=wald_dom_3.tif --calc="(A<=1)*0 + (A>1)*A" nodata 0?

## VRT and 5m Overview

# Hillshading fehlt noch.


#Buildings DOM
infiles = os.path.join(OUT_PATH, "buildings", "dom", "*.tif")
outfile = os.path.join(OUT_PATH, "buildings", "dom", "buildings.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "buildings", "dom", "buildings.vrt")
outfile = os.path.join(OUT_PATH, "buildings", "dom", "buildings_5m.tif")
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

#Buildings Hillshading
infiles = os.path.join(OUT_PATH, "buildings", "hillshade", "*.tif")
outfile = os.path.join(OUT_PATH, "buildings", "hillshade", "buildings.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "buildings", "hillshade", "buildings.vrt")
outfile = os.path.join(OUT_PATH, "buildings", "hillshade", "buildings_5m.tif")
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

#Forest DOM
infiles = os.path.join(OUT_PATH, "forest", "dom", "*.tif")
outfile = os.path.join(OUT_PATH, "forest", "dom", "forest.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "forest", "dom", "forest.vrt")
outfile = os.path.join(OUT_PATH, "forest", "dom", "forest_5m.tif")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -tr 5.0 5.0 -of GTiff"
cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
cmd += " -co 'COMPRESS=LZW' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'" 
cmd += " -wo NUM_THREADS=ALL_CPUS -s_srs epsg:21781 -t_srs epsg:21781"
cmd += " " + infile + " " + outfile
os.system(cmd)

cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest"
cmd += " --config COMPRESS_OVERVIEW LZW --config GDAL_TIFF_OVR_BLOCKSIZE 512"
cmd += " " + outfile + " 2 4 8 16 32 64 128"
#os.system(cmd)

#Forest Hillshade
infiles = os.path.join(OUT_PATH, "forest", "hillshade", "*.tif")
outfile = os.path.join(OUT_PATH, "forest", "hillshade", "forest.vrt")
cmd = "/usr/local/gdal/gdal-dev/bin/gdalbuildvrt " + outfile + " " + infiles 
os.system(cmd)

infile = os.path.join(OUT_PATH, "forest", "hillshade", "forest.vrt")
outfile = os.path.join(OUT_PATH, "forest", "hillshade", "forest_5m.tif")
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
