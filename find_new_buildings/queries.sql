SELECT ((ST_DumpAsPolygons(rast)).geom), (ST_DumpAsPolygons(rast)).val
FROM av_lidar_2014.diff_2014_2002
WHERE rid = 1;

DROP TABLE av_lidar_2014.diff_reclass_5m;
CREATE TABLE av_lidar_2014.diff_reclass_5m as
SELECT rid, ST_Reclass(rast, 1, '[-200-5]:0,(5-200]:1', '4BUI', 0) as rast
FROM av_lidar_2014.diff_2014_2002;
--LIMIT 10;

CREATE INDEX diff_reclass_5m_gist
  ON av_lidar_2014.diff_reclass_5m
  USING gist
  (st_convexhull(rast));


DROP TABLE av_lidar_2014.diff_reclass_5m_poly;
CREATE TABLE av_lidar_2014.diff_reclass_5m_poly as
SELECT ST_MakeValid(((ST_DumpAsPolygons(rast)).geom)) as the_geom, (ST_DumpAsPolygons(rast)).val
FROM av_lidar_2014.diff_reclass_5m; 

CREATE INDEX diff_reclass_5m_poly_gist
  ON av_lidar_2014.diff_reclass_5m_poly
  USING gist
  (the_geom);