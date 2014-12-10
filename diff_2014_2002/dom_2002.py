#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

DOM_ROH_PATH = "/opt/Geodaten/ch/so/kva/hoehen/2002/dom/roh/"
OUT_PATH = "/home/stefan/tmp/dom_2002/dom/"
TMP_PATH = "/tmp/"

shp = ogr.Open("../tileindex/dtm_dom_idx.shp")
layer = shp.GetLayer(0)


for feature in layer:
    nummer = feature.GetField('nummer')
    #print "**********************: " + nummer
    
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope()

    minX = int(env[0] + 0.001)
    minY = int(env[2] + 0.001)
    maxX = int(env[1] + 0.001)
    maxY = int(env[3] + 0.001)
    
    infileBaseName = "dom" + nummer.replace("-", "")
    gzFileName = os.path.join(DOM_ROH_PATH, infileBaseName + ".xyz.gz")
    xyzFileName = os.path.join(TMP_PATH, infileBaseName + ".xyz")
    csvFileName = os.path.join(TMP_PATH, "dom_xyz.csv")
    vrtFileName = os.path.join(TMP_PATH, "dom_xyz.vrt")
    
    if os.path.isfile(gzFileName):
        print gzFileName

        os.system("gunzip -c " + gzFileName + " > " + xyzFileName)
        os.system("fromdos " + xyzFileName)

        # Leerschlag mit Komma ersetzen und in andere Datei schreiben.
        # Datei heisst bei jedem Durchlauf gleich (einfacher zu 
        # handhaben für folgend 'sed' Befehle).
        cmd = "sed -e 's/\s/,/g' " + xyzFileName + " > " + csvFileName
        #print cmd
        os.system(cmd)
    
        # Header (x,y,z) einfügen.
        cmd = "sed -i '1s/^/x,y,z\\n/' " + csvFileName
        #print cmd
        os.system(cmd)
        
        # VRT-Datei kopieren und Pfad zu CSV-Datei richtig setzen.
        cmd = "sed -e 's|dom_xyz.csv|"+csvFileName+"|g' dom_xyz.vrt > " + vrtFileName
        #print cmd
        os.system(cmd)
        
        # +1 Meter: 1/16-Kacheln sind in x-Richtung nicht durch 2 teilbar.
        dx = maxX - minX + 1;
        dy = maxY - minY;
    
        px = dx / 2;
        py = dy / 2;    

        outfile = os.path.join(TMP_PATH, infileBaseName + "_tmp_1.tif")
        cmd = "/usr/local/gdal/gdal-dev/bin/gdal_grid -a_srs epsg:21781"
        cmd += " -a nearest:min_points=9:radius1=5.0:radius2=5.0:nodata=-9999" 
        cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
        cmd += " -co 'COMPRESS=LZW' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'" 
        cmd += " -txe " + str(minX) + " " + str(maxX+1) + " -tye " +str(minY) + " " + str(maxY) 
        cmd += " -outsize " + str(px) + " " + str(py) + " -of GTiff -ot Float32 -l dom_xyz " 
        cmd += " " + vrtFileName + " " + outfile
        #print cmd
        os.system(cmd)
                
        #infile = os.path.join(TMP_PATH, infileBaseName + "_tmp_1.tif")                
        #outfile = os.path.join(TMP_PATH, infileBaseName + "_tmp_2.tif")                
        #cmd = "/usr/local/gdal/gdal-dev/bin/gdal_fillnodata.py -md 50 " + infile + " " + outfile
        #os.system(cmd)
                
        infile = os.path.join(TMP_PATH, infileBaseName + "_tmp_1.tif")
        outfile = os.path.join(OUT_PATH, infileBaseName + ".tif")
        cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite" 
        cmd += " -co 'TILED=YES' -co 'PROFILE=GeoTIFF'  -co 'INTERLEAVE=PIXEL'"
        cmd += " -co 'COMPRESS=LZW' -co 'BLOCKXSIZE=512' -co 'BLOCKYSIZE=512'"         
        cmd += " -te " + str(minX) + " " + str(minY) + " " + str(maxX+1) + " " + str(maxY) 
        cmd += " -tr 2 2 -r near " + infile + " " + outfile
        os.system(cmd)
  
                
        cmd  = "/usr/local/gdal/gdal-dev/bin/gdaladdo -r nearest"
        cmd += " --config COMPRESS_OVERVIEW LZW --config GDAL_TIFF_OVR_BLOCKSIZE 512"
        cmd += " " + outfile + " 2 4 8 16 32 64 128"
        os.system(cmd)
    
        #sys.exit(1)
        
        
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

