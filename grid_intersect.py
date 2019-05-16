"""
grid_intersect.py
April 16 2019
Shaun Cullen (shaun.cullen@canada.ca)

Purpose: Given a shapefile input, return a list of WRS2 or MGRS grid tiles
         that intersect that shapefile.

         Given a list of WRS2 or MGRS tiles, return a list of WKT footprints 
         for each.

         Given a list of WRS2 or MGRS tiles, return a list of the equiv
         opposing format tiles. If a list of WRS2, return the overlapping
         MGRS tiles, vice versa.

Requirements: GDAL 2.*,"grid_files" data directory containing MGRS and WRS2 
              grids.
"""

import os
from pathlib import Path
import json
import zipfile
import argparse
import re

from osgeo import ogr, osr

ogr.UseExceptions()

GRID_DIR = Path(os.path.dirname(os.path.abspath(__file__)), "grid_files")

def cleanup():
    for file_name in Path(GRID_DIR).iterdir():
        print(file_name)
        if file_name.is_file():
            print('is a file')
            os.remove(file_name)

def unzip_mgrs_100km_shp(full_zip_path):
    file_name_stem = full_zip_path.name
    # 1. unzip the appropriate shapefile
    with zipfile.ZipFile(full_zip_path, 'r') as zf:
        actual_file_stem = ""
        for zip_info in zf.infolist():
            if zip_info.filename[-1] == '/':
                continue
            zip_info.filename = zip_info.filename.split('/')[-1]

            if actual_file_stem == "":
                actual_file_stem = zip_info.filename.split('.')[0]

            # Extract only the files to a specific dir
            zf.extract(zip_info, GRID_DIR)

    if actual_file_stem != file_name_stem:
        file_name_stem = actual_file_stem
    
    return file_name_stem

def get_wkt_from_shapefile(shp_path):
    """
    Open shapefile, simplify, merge, create and return WKT version of geometry.
    """
    
    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")
    input_ds = shapefile_driver.Open(shp_path, 0)

    # Check if input_ds has multiple features, if so, union cascade it to flatten it (merge)
    # Create the feature and set values
    in_layer = input_ds.GetLayer()

    multipoly = ogr.Geometry(ogr.wkbMultiPolygon)

    for feature in in_layer:
        print(feature.GetGeometryRef().GetGeometryName())
        geom = feature.GetGeometryRef()
        geom.FlattenTo2D()
        geom_type = geom.GetGeometryName()

        if geom_type == 'POLYGON':
            # print(feature.GetGeometryRef().Simplify(0.005).ConvexHull())
            print(feature.GetGeometryRef().Simplify(0.005))
            simplified_convex_hull = feature.GetGeometryRef().Simplify(0.005)

            print(simplified_convex_hull)
            
            if simplified_convex_hull.GetGeometryName() == 'POLYGON':
                print(simplified_convex_hull)
                simplified_convex_hull.FlattenTo2D()
                print(simplified_convex_hull)
                multipoly.AddGeometry(simplified_convex_hull)

        elif geom_type == 'MULTIPOLYGON':
            for geom_part in geom:
                if geom_part.GetGeometryName() == 'POLYGON':
                    multipoly.AddGeometry(geom_part)
                else:
                    print('unknown geom')
                    print(geom_part.GetGeometryName())

    cascade_union = multipoly.UnionCascaded()
    print(cascade_union)

    wkt_geometry = cascade_union.ExportToWkt()

    return wkt_geometry

def get_wkt_for_wrs_tile(wrs_tile_pathrow):
    """
    Given a WRS path and row, return a WKT footprint of that tile.
    
    wrs_tile_pathrow: (string) 6 char pathrow string, zero padded.
    Iterate over features until path row is found.
    Export the feature geometry as  WKT.
    """

    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

    wrs2_grid_dir = Path(GRID_DIR, 'WRS2_descending')
    wrs2_master_shp_file = Path(wrs2_grid_dir, 'WRS2_descending.shp')

    grid_ds = shapefile_driver.Open(str(wrs2_master_shp_file), 0)
    grid_layer = grid_ds.GetLayer()

    feature = None

    for f in grid_layer:

        if wrs_tile_pathrow == f.GetField('PR'):
            feature = f

    if feature:
        geom = feature.GetGeometryRef()
        grid_ds = None
        return geom.ExportToWkt()
    else:
        grid_ds = None
        return None

def convert_mgrs_to_wrs(mgrs_100km_id):
    """
    Given a MGRS 100km tile id, return the overlapping WRS pathrow list.

    1. Convert MGRS to WKT footprint
    2. Call find_wrs_intersection
    """

    wkt_footprint = get_wkt_for_mgrs_tile(mgrs_100km_id)

    wrs_list = find_wrs_intersection(wkt_footprint)

    return wrs_list


def convert_wrs_to_mgrs(wrs_pathrow):
    """
    Given a pathrow tile id, return the overlapping MGRS 100km tile id list.

    1. Convert WRS to WKT footprint
    2. Call find_mgrs_intersection
    """
    wkt_footprint = get_wkt_for_wrs_tile(wrs_pathrow)

    mgrs_list = find_mgrs_intersection(wkt_footprint)

    return mgrs_list

def convert_wrs_to_mgrs_list(wrs_list):

    footprint_list = []
    tile_list = []

    for wrs in wrs_list:
        footprint_list.append(get_wkt_for_wrs_tile(wrs))

    for footprint in footprint_list:
        tile_list += find_mgrs_intersection(footprint)

    return set(tile_list)

def convert_mgrs_to_wrs_list(mgrs_list):

    footprint_list = []
    tile_list = []

    for mgrs in mgrs_list:
        footprint_list.append(get_wkt_for_mgrs_tile(mgrs))

    for footprint in footprint_list:
        tile_list += find_wrs_intersection(footprint)

    return set(tile_list)


def get_wkt_for_mgrs_tile(mgrs_100km_id):
    """
    Given a MGRS GZD and 100km_ID (U14UR), return a WKT footprint of that tile.
    
    mgrs_100km_id: (string) 5 char GZD String.
    Iterate over features until path row is found.
    Export the feature geometry as  WKT.

    Unzip the appropriate shapefile.
    Load the shapefile.
    Interate over features until found.
    Return geometry as WKT.
    Clean up unziped files.
    """

    # Use a regex to verify a valid MGRS_100km id

    m = re.search(r'[01234656]\d{1}[C-HJ-NP-X][A-HJ-NP-Z][A-HJ-NP-V]', mgrs_100km_id)
    
    if m.group(0):
        print('Valid mgrs 100km id')
        gzd_id = mgrs_100km_id[:3]
        print(gzd_id)
    else:
        print('Invalid mgrs 100km id')
        return None

    # unzip the specific GZD shapefile
    gzd_shapefile_name = f"MGRS_100kmSQ_ID_{gzd_id}"
    mgrs_grid_dir = Path(GRID_DIR, 'MGRS_100kmSQ_ID')
    mgrs_zip_file = Path(mgrs_grid_dir, gzd_shapefile_name + '.zip')

    mgrs_name = unzip_mgrs_100km_shp(mgrs_zip_file)
    mgrs_shp_file = Path(GRID_DIR, mgrs_name + '.shp')

    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

    grid_ds = shapefile_driver.Open(str(mgrs_shp_file), 0)
    grid_layer = grid_ds.GetLayer()

    feature = None

    # transform coords from local UTM proj to lat long
    sourceSR = grid_layer.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326) # WGS84
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)

    for f in grid_layer:
        if mgrs_100km_id == f.GetField('MGRS'):
            feature = f
    
    geom = feature.GetGeometryRef()
    geom.Transform(coordTrans)
    
    if geom:
        wkt_result = geom.ExportToWkt()

        grid_ds = None
        cleanup()
        return wkt_result
    else:
        grid_ds = None
        cleanup()
        return None

def find_wrs_intersection(wkt_footprint):
    """
    Return (or write to file) the list of WRS path rows that intersect the given wkt footprint
    """

    # 1. Load shapefile
    # 2. If multiple features, union cascade to get just the outline
    # 3. Iterate over each wrs, test intersection with shapefile, if intersects add the field name to a list
    # 4. Write out list to a file

    polygon_geom = ogr.CreateGeometryFromWkt(wkt_footprint)

    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

    wrs2_grid_dir = Path(GRID_DIR, 'WRS2_descending')
    wrs2_master_shp_file = Path(wrs2_grid_dir, 'WRS2_descending.shp')

    grid_ds = shapefile_driver.Open(str(wrs2_master_shp_file), 0)
    grid_layer = grid_ds.GetLayer()

    intersect_list = []

    # multipoly_intersect = ogr.Geometry(ogr.wkbMultiPolygon)

    for f in grid_layer:
        geom = f.GetGeometryRef()

        intersect_result = geom.Intersection(polygon_geom)

        if not intersect_result.IsEmpty():
            print("FOUND INTERSECT")
            print(f.GetField('PR'))
            print(geom.GetGeometryName())
            intersect_list.append(f.GetField('PR'))

    return intersect_list

def create_shp_file_from_tile_list_wrs(tile_list):
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(4326)

    # Create the output Driver
    # out_driver = ogr.GetDriverByName("ESRI Shapefile")

    # Create the output GeoJSON
    out_datasource = shapefile_driver.CreateDataSource('intersecting_wrstiles.shp')
    # out_layer = out_datasource.CreateLayer('wrs', geom_type=ogr.wkbPolygon )

    out_layer = out_datasource.CreateLayer("wrs", spatial_ref, geom_type=ogr.wkbMultiPolygon)

    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)

    out_layer.CreateField(idField)

    pathrow_field = ogr.FieldDefn("pr", ogr.OFTString)
    path_field = ogr.FieldDefn("path", ogr.OFTString)
    row_field = ogr.FieldDefn("row", ogr.OFTString)

    out_layer.CreateField(pathrow_field)
    out_layer.CreateField(path_field)
    out_layer.CreateField(row_field)

    featureDefn = out_layer.GetLayerDefn()

    for idx, feat in enumerate(intersect_list):
        print('Tryng to create a feature.')
        feature = ogr.Feature(featureDefn)

        feature.SetField("id", idx + 1)
        feature.SetField("pr", feat[0])
        feature.SetField("path", feat[0][:3])
        feature.SetField("row", feat[0][3:])
        print('trying to set geometry')
        feature.SetGeometry(ogr.CreateGeometryFromWkb(feat[1]))
        # print(feat)

        out_layer.CreateFeature(feature)
        print('created feature')
        feature = None

    out_datasource = None

    # all done!
    grid_ds = None
    input_ds = None

def create_shapefile_from_tile_list(tile_id_list, dst_name=None):
    """
    Given a list of tiles (wrs or mgrs, will auto detect based on length
    and content), use the approp functions to get the wkt representations
    and add features with that geometry and tilename field. Optionally,
    specify the name and destination for the resulting shapefile
    """
    # will contain tile name, tile type, and geometry
    shapefile_content_list = []
    
    for tile_id in tile_id_list:
        tile_type = determine_tile_mgrs_or_wrs(tile_id)
        wkt_footprint = ''
        if tile_type == 'mgrs':
            wkt_footprint = get_wkt_for_mgrs_tile(tile_id)
        elif tile_type == 'wrs':
            wkt_footprint = get_wkt_for_wrs_tile(tile_id)
        
        tile_tuple = (tile_id, tile_type, wkt_footprint)
        shapefile_content_list.append(tile_tuple)
    
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(4326)

    # Create the output Driver
    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

    output_dst = dst_name or 'tile_coverage.shp'
    # Create the output GeoJSON
    out_datasource = shapefile_driver.CreateDataSource(str(output_dst))
    out_layer = out_datasource.CreateLayer("tiles", spatial_ref, geom_type=ogr.wkbMultiPolygon)

    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    tile_id_field = ogr.FieldDefn("tile_id", ogr.OFTString)
    tile_type_field = ogr.FieldDefn("tile_type", ogr.OFTString)
    
    out_layer.CreateField(idField)
    out_layer.CreateField(tile_id_field)
    out_layer.CreateField(tile_type_field)

    featureDefn = out_layer.GetLayerDefn()

    for idx, feat in enumerate(shapefile_content_list):
        print('Tryng to create a feature.')
        feature = ogr.Feature(featureDefn)

        feature.SetField("id", idx + 1)
        feature.SetField("tile_id", feat[0])
        feature.SetField("tile_type", feat[1])
        
        print('trying to set geometry')
        feature.SetGeometry(ogr.CreateGeometryFromWkt(feat[2]))

        out_layer.CreateFeature(feature)
        print('created feature')
        feature = None

    out_datasource = None


def find_mgrs_intersection(wkt_footprint):
    """
    Given a WKT polygon, return the list of MGRS 100km grids that intersect it

    Utilize the helper function find_mgrs_intersection_single for each GZD
    """

    total_mgrs_100km_list = []
    gzd_list = find_mgrs_gzd_intersections(wkt_footprint)

    for gzd in gzd_list:
        sub_list = find_mgrs_intersection_100km(wkt_footprint, gzd)
        for mgrs_id in sub_list:
            total_mgrs_100km_list.append(mgrs_id)

    return total_mgrs_100km_list

def find_mgrs_gzd_intersections(wkt_footprint):
    """ Given a WKT polygon, return the list of MGRS tiles that intersect it

    the MGRS grid names retured are (generally) 6 x 8 degrees, each with
    a GZD (grid-zone designation) of AQ

    There are 1200 grid files to iterate over to check intersection

    A master MGRS GZD file has all GZD's, once the overall GZD's are known,
    use the individual shapefiles to find the fine-grained 100km tiles
    (ex:60WUT)

    Steps:
    1. Find intersections between footprint and master mgrs shp

    NOTES:
    Only supports WGS84 coord system for now. May add auto conversion in the 
    future.
    """

    polygon_geom = ogr.CreateGeometryFromWkt(wkt_footprint)

    mgrs_grid_file_dir = Path(GRID_DIR, 'MGRS_100kmSQ_ID')

    mgrs_master_shp_file = Path(mgrs_grid_file_dir, 'mgrs_gzd_final.shp')

    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

    grid_ds = shapefile_driver.Open(str(mgrs_master_shp_file), 0)

    layer = grid_ds.GetLayer()

    # sourceSR = layer.GetSpatialRef()
    # targetSR = osr.SpatialReference()
    # targetSR.ImportFromEPSG(4326) # WGS84
    # coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)

    feature_count = layer.GetFeatureCount()
    layerDefinition = layer.GetLayerDefn()

    for i in range(layerDefinition.GetFieldCount()):
        print(layerDefinition.GetFieldDefn(i).GetName())

    intersect_list = []

    for f in layer:
        geom = f.GetGeometryRef()
    
        intersect_result = geom.Intersection(polygon_geom)

        if not intersect_result.IsEmpty():
            print("FOUND INTERSECT")
            print(f.GetField('gzd'))
            intersect_list.append(f.GetField('gzd'))
    
    return intersect_list

def determine_tile_mgrs_or_wrs(tile_id):
    """
    Returns 'mgrs' if mgrs tile, 'wrs' if wrs tile id, or 'unknown' if neither
    """
    mgrs_search = re.search(r'[01234656]\d{1}[C-HJ-NP-X][A-HJ-NP-Z][A-HJ-NP-V]', tile_id)
    wrs_search = re.search(r'\d{6}', tile_id)

    tile_type = None
    if mgrs_search:
        tile_type = 'mgrs'
    elif wrs_search:
        tile_type = 'wrs'
    else:
        tile_type = 'unknown'
    
    return tile_type

def find_mgrs_intersection_100km(footprint, gzd):
    """
    Given a WKT polygon and a GZD (grid zone designator)
    return the list of 100km MGRS gzd that intersect the WKT polygon

    Overview:
    1. Based on the GZD, unzip the matching .shp and load
    2. Run interesction check on each feature of the .shp
    3. Save intersections to a list, the field is 100kmSQ_ID
    4. Clean up unziped files, return list of intersecting 100kmSQ_ID's
    """

    polygon_geom = ogr.CreateGeometryFromWkt(footprint)

    zip_name = f'MGRS_100kmSQ_ID_{gzd}.zip'
    file_name_stem = f'MGRS_100kmSQ_ID{gzd}'
    full_zip_path = Path(GRID_DIR, 'MGRS_100kmSQ_ID', zip_name)

    # 1. unzip
    file_name_stem = unzip_mgrs_100km_shp(full_zip_path)

    file_path = Path(GRID_DIR, file_name_stem + '.shp')

    # 2. Load the shp file and run intersection check on each feature
    shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")
    grid_ds = shapefile_driver.Open(str(file_path), 0)
    layer = grid_ds.GetLayer()

    # transform coords from local UTM proj to lat long
    sourceSR = layer.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326) # WGS84
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)

    intersect_list = []

    for f in layer:
        geom = f.GetGeometryRef()
        geom.Transform(coordTrans)

        intersect_result = geom.Intersection(polygon_geom)

        if not intersect_result.IsEmpty():
            print("FOUND INTERSECT")
            print(f.GetField('100kmSQ_ID'))
            intersect_list.append(f'{gzd}{f.GetField("100kmSQ_ID")}')

    # all done!
    grid_ds = None

    # clean up
    cleanup()

    return intersect_list