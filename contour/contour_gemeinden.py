#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import sys

ogr.UseExceptions()

VRT = "/opt/Geodaten/ch/so/kva/hoehen/2014/dtm/grid/50cm/dtm.vrt"
OUT_PATH = "/home/stefan/tmp/contour2/"
TMP_PATH = "/tmp/contour2/"
BUFFER = 50

shp1 = ogr.Open("../data/gemeindegrenzen/gemeindegrenzen.shp")
layer1 = shp1.GetLayer(0)

for feature1 in layer1:
    gem_bfs = feature1.GetField('gem_bfs')
    
    #if str(int(gem_bfs)) != "2546":
        #continue  
    
    print "**********************: " + str(gem_bfs)
    geom1 = feature1.GetGeometryRef().Buffer(50)

    shp2 = ogr.Open("../tileindex/lidar2014_einzeln.shp")
    layer2 = shp2.GetLayer(0)
    
    #outfile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)))
    #cmd = "mkdir " + outfile
    #os.system(cmd)
    
    for feature2 in layer2:
        geom2 = feature2.GetGeometryRef()

        if geom2.Intersects(geom1): 
            infileName = feature2.GetField('location')
            print "**********************: " + infileName

            env = geom2.GetEnvelope()
            minX = int(env[0] + 0.001)
            minY = int(env[2] + 0.001)
            maxX = int(env[1] + 0.001)
            maxY = int(env[3] + 0.001)
            
            #if minX != 594000 or minY != 230000:
                #continue
        
            outfile = os.path.join(TMP_PATH, "input.tif")
    
            cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781 -te" 
            cmd += " " + str(minX - BUFFER) + " " +  str(minY - BUFFER) + " " +  str(maxX + BUFFER) + " " +  str(maxY + BUFFER)
            cmd += " -tr 0.5 0.5 -wo NUM_THREADS=ALL_CPUS -r bilinear "
            cmd += " " + VRT + " " + outfile;
            print cmd    
            os.system(cmd);


            infile = os.path.join(TMP_PATH, "input.tif")
            outfile = os.path.join(TMP_PATH, "output.tif")
        
            for i in range(10):
                cmd = "/usr/local/gdal/gdal-dev/bin/gdalwarp -overwrite -s_srs epsg:21781 -t_srs epsg:21781"
                cmd += " -r cubicspline " + infile + " " + outfile
                print cmd
                os.system(cmd)
                os.system("cp " + outfile + " " + infile)

            infile = os.path.join(TMP_PATH, "input.tif")
            outfile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
            cmd = "/usr/local/gdal/gdal-dev/bin/gdal_contour -b 1 -3d -a elev -i 1.0 " + infile + " " + outfile
            print cmd
            os.system(cmd)
            os.system("rm " + infile)
    

            infile = "../data/gemeindegrenzen/gemeindegrenzen.shp"
            outfile = os.path.join(TMP_PATH, "tmp_gemeinde.shp")
            cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -dialect SQLITE" 
            cmd += " " + outfile + " " + infile + " -sql \"SELECT * FROM gemeindegrenzen WHERE gem_bfs = " + str(int(gem_bfs)) + "\""  
            print cmd
            os.system(cmd)
            
            clipfile = os.path.join(TMP_PATH, "tmp_gemeinde.shp")    
            infile = os.path.join(TMP_PATH, "contour_tmp_1.shp")
            outfile = os.path.join(TMP_PATH, "contour_tmp_2.shp")
            #cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -skipfailures -where \"OGR_GEOMETRY='LineString'\" -clipsrc" 
            cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -clipsrc" 
            cmd += " " + clipfile + " " + outfile + " " + infile
            print cmd
            os.system(cmd)       
            
            ## Eventuell Zusatzschritt, falls immer noch Probleme:
            ## Zuerst um ganz wenig groesseres Polygon clippen. 
            ## Aber nicht etwas was der Kachelgrösse entspricht, sonst
            ## gibts wieder Problem falls ein Vertexpunkt direkt auf einer
            ## Kachelkante liegt.
            
            infile = os.path.join(TMP_PATH, "contour_tmp_2.shp")
            outfile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)) + ".shp")
            clip = geom2.ExportToWkt()
            #cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -append -skipfailures -where \"OGR_GEOMETRY='LineString'\" -clipsrc '" + clip + "' " + outfile + " " + infile
            cmd = "/usr/local/gdal/gdal-dev/bin/ogr2ogr -append -clipsrc '" + clip + "' " + outfile + " " + infile
            print cmd
            os.system(cmd)


      
            
    infile = os.path.join(TMP_PATH, "contour_" + str(int(gem_bfs)) + ".shp")
    cmd = "/usr/local/gdal/gdal-dev/bin/ogrinfo " + infile 
    cmd += " -sql \"ALTER TABLE contour_" + str(int(gem_bfs)) 
    cmd += " ADD COLUMN bfsnr integer(10)\""
    print cmd
    os.system(cmd)
    
    cmd = "/usr/local/gdal/gdal-dev/bin/ogrinfo " + infile 
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
    
    cmd = "rm " + os.path.join(TMP_PATH, "*tmp*.shp")
    os.system(cmd)
    cmd = "rm " + os.path.join(TMP_PATH, "*tmp*.dbf")
    os.system(cmd)    
    cmd = "rm " + os.path.join(TMP_PATH, "*tmp*.shx")
    os.system(cmd)    
    cmd = "rm " + os.path.join(TMP_PATH, "*tmp*.prj")
    os.system(cmd)
    cmd = "rm " + os.path.join(TMP_PATH, "*.tif")
    os.system(cmd)


    
