#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

#GEMEINDEGRENZEN = "../data/gemeindegrenzen/gemeindegrenzen.shp"
GEMEINDEGRENZEN = "../data/gemeindegrenzen_zh/gemeindegrenzen.shp"
#VRT_DTM = "/opt/Geodaten/ch/so/kva/hoehen/2014/dtm/grid/50cm/dtm.vrt"
VRT_DTM = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dtm/grid/50cm/dtm2014.vrt"
TILEINDEX_DTM = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/tileindex/dtm2014.shp"
OUT_PATH = "/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/isohypsen/"
TMP_PATH = "/home/stefan/tmp/contour_zh/"
BUFFER = 50

#shp1 = ogr.Open(GEMEINDEGRENZEN)
shp1 = ogr.Open(GEMEINDEGRENZEN)
layer1 = shp1.GetLayer(0)

for feature1 in layer1:
    gem_bfs = feature1.GetField('gem_bfs')
        
    print "Prozessiere BfS-Nr.: " + str(gem_bfs)
    
    file_name = os.path.join(OUT_PATH, "contour_" + str(int(gem_bfs)) + ".zip")
    print file_name
    if os.path.isfile(file_name):
        print "Contours bereits vorhanden..."
        continue
    
#    if gem_bfs <> 117:
#        continue
    
    geom1 = feature1.GetGeometryRef().Buffer(50)
    
    shp2 = ogr.Open(TILEINDEX_DTM)
    layer2 = shp2.GetLayer(0)
    
    #outfile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)))
    #cmd = "mkdir " + outfile
    #os.system(cmd)
    
    cmd = "rm -rf " + TMP_PATH
    os.system(cmd)
    
    cmd = "mkdir " + TMP_PATH
    os.system(cmd)
    
    for feature2 in layer2:
        geom2 = feature2.GetGeometryRef()
#        infileName = feature2.GetField('location')
#        if infileName <> "7070_2400.tif":
#            continue        

        if geom2.Intersects(geom1): 
            infileName = feature2.GetField('location')
            print "************** DTM-File: " + infileName
            
            env = geom2.GetEnvelope()
            minX = int(env[0] + 0.001)
            minY = int(env[2] + 0.001)
            maxX = int(env[1] + 0.001)
            maxY = int(env[3] + 0.001)
    
            outfile = os.path.join(TMP_PATH, "input.tif")
            cmd = "gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te" 
            cmd += " " + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
            cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -r bilinear "
            cmd += " " + VRT_DTM + " " + outfile;
            print cmd    
            os.system(cmd);
            
            infile = os.path.join(TMP_PATH, "input.tif")
            outfile = os.path.join(TMP_PATH, "output.tif")
            for i in range(10):
                cmd = "gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781"
                cmd += " -r cubicspline " + infile + " " + outfile
                print cmd
                os.system(cmd)
                os.system("cp " + outfile + " " + infile)

            infile = os.path.join(TMP_PATH, "input.tif")
            outfile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
            cmd = "rm " + outfile
            os.system(cmd)
            
            cmd = "gdal_contour -b 1 -3d -a elev -i 1.0 " + infile + " " + outfile
            print cmd
            os.system(cmd)
            os.system("rm " + infile)
    
            infile = GEMEINDEGRENZEN
            outfile = os.path.join(TMP_PATH, "tmp_gemeinde.shp")
            cmd = "ogr2ogr -overwrite -dialect SQLITE" 
            #cmd += " " + outfile + " " + infile + " -sql \"SELECT * FROM gemeindegrenzen WHERE gem_bfs = " + str(int(gem_bfs)) + "\""  
            cmd += " " + outfile + " " + infile + " -sql \"SELECT * FROM gemeindegrenzen WHERE gem_bfs = " + str(int(gem_bfs)) + "\""  
            print cmd
            os.system(cmd)
            
            clipfile = os.path.join(TMP_PATH, "tmp_gemeinde.shp")    
            infile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
            outfile = os.path.join(TMP_PATH, "contour_tmp_2.shp")
            cmd = "ogr2ogr -overwrite -clipsrc" 
            cmd += " " + clipfile + " " + outfile + " " + infile
            print cmd
            os.system(cmd)       

            ## Probleme gibts, wenn ein Vertexpunkt genau auf der Schnittkante liegt.
            ## Daraus entstehen GeometryCollections. Diese müssen jetzt bisschen 
            ## fricklig auseinandergepfrimelt werden.
            ## Geht wahrscheinlich eleganter mit GDAL >= 2.0 (-dialect INDIRECT_SQLITE)
            infile = os.path.join(TMP_PATH, "contour_tmp_2.shp")
            outfile = os.path.join(TMP_PATH, "contour_tmp_3.gpkg")
            cmd = "ogr2ogr -overwrite -f GPKG " + outfile + " " + infile
            print cmd
            os.system(cmd)
            
            infile = os.path.join(TMP_PATH, "contour_tmp_3.gpkg")
            outfile = os.path.join(TMP_PATH, "contour_tmp_4.gpkg")
            clip = geom2.ExportToWkt()            
            cmd = "ogr2ogr -overwrite -clipsrc '" + clip + "' -f GPKG " + outfile + " " + infile
            print cmd
            os.system(cmd)
            
            infile = os.path.join(TMP_PATH, "contour_tmp_4.gpkg")
            outfile = os.path.join(TMP_PATH, "contour_tmp_5.gpkg")
            cmd = "ogr2ogr -overwrite -explodecollections -f GPKG " + outfile + " "  + infile
            print cmd
            os.system(cmd)
            
            infile = os.path.join(TMP_PATH, "contour_tmp_5.gpkg")
            outfile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)) + ".shp")
            clip = geom2.ExportToWkt()
            cmd = "ogr2ogr -nlt LINESTRING25D -skipfailures -append " + outfile + " " + infile
            print cmd
            os.system(cmd)
            
    infile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)) + ".shp")
    cmd = "ogrinfo " + infile 
    cmd += " -sql \"ALTER TABLE contour_" + str(int(gem_bfs)) 
    cmd += " ADD COLUMN bfsnr integer(10)\""
    print cmd
    os.system(cmd)
    
    cmd = "ogrinfo " + infile 
    cmd += " -dialect SQLITE -sql \"UPDATE contour_" + str(int(gem_bfs)) 
    cmd += " SET bfsnr = " + str(int(gem_bfs)) + "\""
    print cmd
    os.system(cmd)
            
    #infiles = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)), "contour_" + str(int(gem_bfs)) + ".*")
    infiles = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)) + ".*")
    outfile = os.path.join(OUT_PATH, "contour_" + str(int(gem_bfs)))
    cmd = "zip -j " + outfile + " " + infiles
    print cmd
    os.system(cmd)
    
    # shp -> gpkg    
    infile = "/vsizip/" + outfile + ".zip"
    outfile = os.path.join(OUT_PATH, "contour_" + str(int(gem_bfs)) + ".gpkg")
    cmd = "ogr2ogr -f GPKG " + outfile + " " + infile 
    #print cmd
    #os.system(cmd)
    


    
