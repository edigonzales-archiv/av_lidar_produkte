SELECT * 
FROM av_lidar_2014.ndsm
WHERE rid = 1;

SELECT ST_Neighborhood(rast)
FROM av_lidar_2014.ndsm
WHERE rid = 1;
