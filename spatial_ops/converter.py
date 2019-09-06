#-*- coding: utf-8 -*-
"""converter.py -- Part of spatialops Module

Bundle of helper functions for converting spatial data.

Utilizes OGR and GDAL to do conversions between different vector types, and
also for different raster types. The module will simplify input polygons,
and generate output polygons.

.. topic:: Contact

    Shaun Cullen (shaun [dot] cullen [at] canada [dot] ca)
    January 29 2018
    https://github.com/sscullen/sentinel2dd

"""

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

from pathlib import Path
from os import makedirs
import os
import logging
import glob
from datetime import datetime

gdal.UseExceptions()

class Converter:
    """ Class that bundles the helper spatial conversion functions."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Converter constructor running')

    def create_tile_footprint(self, wkt, output):
        """Creates a geojson vector file from the tile footprint.

        Args:
            wkt (str): Wellknown Text (wkt) representation of a polygon
                obtained from the tile product metadata.
            output (str): Path to save the resulting GeoJson converted file.

        """

        # Get Tile Footprint
        fp = ogr.CreateGeometryFromWkt(wkt)
        # Create the output Driver
        out_driver = ogr.GetDriverByName('GeoJSON')

        # Create the output GeoJSON
        out_data_source = out_driver.CreateDataSource(output)

        out_layer = out_data_source.CreateLayer(output,
                                                geom_type=ogr.wkbPolygon)

        # Get the output Layer's Feature Definition
        feature_defn = out_layer.GetLayerDefn()
        # create a new feature
        out_feature = ogr.Feature(feature_defn)
        # Set new geometry
        out_feature.SetGeometry(fp)
        # Add new feature to output Layer
        out_layer.CreateFeature(out_feature)

        # Not sure if this is necessary (might be for GC purposes)
        # # dereference the feature
        out_feature = None

        # # Save and close DataSources
        out_data_source = None

    def convert_jp2_to_tif(self, original_file,
                                 destination_dir,
                                 atmos_cor,
                                 new_path):
        """ Converts jp2 to tif, renames/reorganizes original .SAFE download.

        This function utilizes GDAL to convert the original .jp2 image data to \
        .tif image data. It takes the original folder name, and a destination \
        folder, and then puts the converted file in the correctly named folder \
        inside the destination folder.

        Args:
            original_file (str): Name of the folder for the original .SAFE
                data.
            destination_dir (str): Name of the folder where the converted \
                file will be copied to.
            atmos_cor (int): If atmos correction is specified, value will be
                int of 10, 20, or 60. If atmos correction is not specified,
                value will be 0.
            new_path (str): Path to directory to save the converted jp2 files.

        """

        # Create the output destination file name and path as a string
        # need to account for non-corrected files
        if atmos_cor in [10, 20, 60]:
            output_file = str(Path(new_path, "{}_{}_{}m.tif"
                                                .format(destination_dir,
                                                         str(original_file)[
                                                         -11:-8],
                                                         atmos_cor)))
            self.logger.debug('Output path: {}'.format(output_file))

        else:
            output_file = str(Path(new_path, "{}_{}.tif"
                                            .format(destination_dir,
                                             str(original_file)[-7:-4])))
            self.logger.debug('Output path: {}'.format(output_file))

        if not new_path.exists():
            self.self.logger.debug('dir doesnt exist, creating')
            makedirs(new_path)
        else:
            self.logger.debug('dir already exists, not creating')

        if Path(output_file).exists():
            self.logger.debug('geotiff already exists, skipping')
        else:
            self.logger.debug('converting geotiff')
            file = gdal.Open(str(original_file))

            prj = file.GetProjection()
            self.logger.debug('projection {}'.format(prj))

            srs = osr.SpatialReference(wkt=prj)

            if srs.IsProjected:
                self.logger.debug('{}'.format(srs.GetAttrValue('projcs')))

            self.logger.debug('{}'.format(srs.GetAttrValue('geogcs')))

            driver = gdal.GetDriverByName("GTiff")
            ds_out = driver.CreateCopy(output_file, file)
            ds_out.SetProjection(srs.ExportToWkt())

            file = None
            ds_out = None

    def create_coverage_poly(self, product_dict, date_string, output_folder):
        """Creates a vector file representing the geog coverage of the data.

        The function utilizes a product dict to create a multipolygon vector file \
        representing the geographic coverage of data that was downloaded based on \
        the query parameters specified when the program is run. Select attributes \
        are extracted from the product dict and added to each polygon of the \
        vector file, which adds metadata to the visualization vector file.

        Args:
            product_dict (dict): Dictionary containing all the attributes found in
                ``product_attribute_list.txt``.
            date_string (str): String representation of the date when the query \
                was started.
            output_folder (str): Str repr of the name of folder to write the
                resulting geojson file to.

        """

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        attribute_list = []

        # TODO: Parse val['title'] to extract MGRS tile

        for key, value in product_dict.items():
            # Get Tile Footprint
            wkt = value['footprint']
            fp = ogr.CreateGeometryFromWkt(wkt)

            if 'mgrs' in value.keys():
                mgrs_tile = value['mgrs']
            else:
                mgrs_tile = "None"

            self.logger.debug('Product: %s' % value)

            if value['platform_name'] == 'Sentinel-1':
                attribute_list.append((value['detailed_metadata']['platformname'],
                                        value['detailed_metadata']['producttype'],
                                        value['detailed_metadata']['format'],
                                        value['detailed_metadata']['polarisationmode'],
                                        value['detailed_metadata']['sensoroperationalmode'],
                                        value['detailed_metadata']['beginposition'],
                                        value['detailed_metadata']['uuid'],
                                        value['detailed_metadata']['title'],
                                        mgrs_tile,
                                        fp))

            elif value['platform_name'] == 'Sentinel-2':

                attribute_list.append((value['platform_name'],
                                    value['cloud_percent'],
                                    value['acquisition_start'],
                                    value['uuid'],
                                    mgrs_tile,
                                    fp,
                                    value['sat_name'],
                                    value['vendor_name']))


        out_driver = ogr.GetDriverByName('GeoJSON')
        out_vector_file_path =  os.path.join(output_folder, date_string + 'coverage.geojson')

        # Create the output GeoJSON
        if os.path.exists(os.path.split(out_vector_file_path)[0]):
            out_data_source = out_driver.CreateDataSource(out_vector_file_path)
        else:
            print('something broke, byeeeeeee')
            return None

        out_layer = out_data_source.CreateLayer(
            os.path.join(output_folder,
                    date_string + 'coverage.geojson'),
                        geom_type=ogr.wkbPolygon)

        # Create the fields for the meta data
        # Add metadata to coverage multi-poly
        # idField = ogr.FieldDefn('tileid', ogr.OFTString)
        # out_layer.CreateField(idField)
        # maybe add later

        titleField = ogr.FieldDefn('title', ogr.OFTString)
        out_layer.CreateField(titleField)

        dateField = ogr.FieldDefn('date', ogr.OFTDateTime)
        out_layer.CreateField(dateField)

        platformNameField = ogr.FieldDefn('platformname', ogr.OFTString)
        out_layer.CreateField(platformNameField)

        productidField = ogr.FieldDefn('productid', ogr.OFTString)
        out_layer.CreateField(productidField)

        productTypeField = ogr.FieldDefn('producttype', ogr.OFTString)
        out_layer.CreateField(productTypeField)

        productFormatField = ogr.FieldDefn('format', ogr.OFTString)
        out_layer.CreateField(productFormatField)

        polarizationField = ogr.FieldDefn('polarization', ogr.OFTString)
        out_layer.CreateField(polarizationField)

        sensorModeField = ogr.FieldDefn('sensormode', ogr.OFTString)
        out_layer.CreateField(sensorModeField)

        cloudField = ogr.FieldDefn('cloud', ogr.OFTInteger)
        out_layer.CreateField(cloudField)

        idField = ogr.FieldDefn('tileid', ogr.OFTString)
        out_layer.CreateField(idField)

        satelliteNameField = ogr.FieldDefn('sat_name', ogr.OFTString)
        out_layer.CreateField(satelliteNameField)

        vendorNameField = ogr.FieldDefn('vendor_name', ogr.OFTString)
        out_layer.CreateField(vendorNameField)

        # Get the output Layer's Feature Definition
        feature_defn = out_layer.GetLayerDefn()

        for feature in attribute_list:

            if feature[0] == 'Sentinel-1':

                # create a new feature
                out_feature = ogr.Feature(feature_defn)
                # Set new geometry
                out_feature.SetGeometry(feature[9])
                out_feature.SetField('title', feature[7])
                out_feature.SetField('productid', feature[6])
                out_feature.SetField('date', feature[5].isoformat(' ', 'seconds'))
                out_feature.SetField('platformname', feature[0])
                out_feature.SetField('producttype', feature[1])
                out_feature.SetField('format', feature[2])
                out_feature.SetField('polarization', feature[3])
                out_feature.SetField('sensormode', feature[4])

                # Add new feature to output Layer
                out_layer.CreateFeature(out_feature)

            else:
                out_feature = ogr.Feature(feature_defn)
                # Set new geometry
                out_feature.SetGeometry(feature[5])
                out_feature.SetField('tileid', feature[4])
                out_feature.SetField('productid', feature[3])
                out_feature.SetField('date', feature[2].isoformat(' ', 'seconds'))
                out_feature.SetField('cloud', int(float(feature[1])))
                out_feature.SetField('sat_name', feature[6])
                out_feature.SetField('vendor_name', feature[7])
                # Add new feature to output Layer
                out_layer.CreateFeature(out_feature)


    def simplify_query_poly(self, input_path, output_path):
        """Converts input extent polygon to geojson and simplifies each part.

        Args:
            input_path (str): Path to the input vector file.
            output_path (str): Path to the directory where the output simplified
                vector file should be saved.

        Returns:
            (list): List of footprints in .wkt format from the broken up and
                simplified multipolygon vector file is returned, or None if
                something goes wrong.
        """

        # Convert SHP or KML to GEOJSON here
        if Path(input_path).suffix == '.shp':
            self.logger.debug('Input area mask is a SHP')
            in_driver = ogr.GetDriverByName('ESRI Shapefile')

        elif Path(input_path).suffix == '.kml':
            self.logger.debug('Input area mask is a KML')

        elif Path(input_path).suffix == '.geojson':
            self.logger.debug('Input area mask is a GeoJson')
            in_driver = ogr.GetDriverByName('GEOJson')
        else:
            print('Invalid vector polygon file provided...')
            return None

        self.logger.info('input_path: %s', input_path)
        
        data_source = in_driver.Open(input_path, 0)

        if data_source:
            layer = data_source.GetLayer()
            multipoly = ogr.Geometry(ogr.wkbMultiPolygon)

            # TODO: Only simplify to a convex hull if the points > 199
            for idx, feature in enumerate(layer):
                self.logger.debug('Feature is... {}'.format(feature))

                # Create a wkt of the convex hull around each linear ring
                # which is a basic primitive to represent a polygon
                # Simplify the footprint before adding to the list
                # simplify uses the units of projection of the file
                # in this case it is decimal degrees
                fp = ogr.CreateGeometryFromWkt(
                    feature.GetGeometryRef().ConvexHull().ExportToWkt()).Simplify(0.001)

                multipoly.AddGeometry(fp)

            # write out the multipoly of the simple coverage
            out_driver = ogr.GetDriverByName('ESRI Shapefile')
            # Create the output GeoJSON
            out_data_source = out_driver.CreateDataSource(output_path)
            out_layer = out_data_source.CreateLayer("test",
                                                    geom_type=ogr.wkbPolygon)

            # Set new geometry
            unioned_geometry = multipoly.UnionCascaded()
            fp_list = []

            for geom_part in unioned_geometry:

                if geom_part.GetGeometryName() == 'LINEARRING':
                    # Its a linear ring
                    #convert to polygon
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(geom_part)

                    fp_list.append(poly.ExportToWkt())
                    self.addPolygon(poly.ExportToWkb(), out_layer )
                else:
                    fp_list.append(geom_part.ExportToWkt())
                    self.addPolygon(geom_part.ExportToWkb(), out_layer )

            else:
                pass
                    # self.addPolygon(geom.ExportToWkb(), out_lyr)
            out_data_source = None

            return fp_list
        else:
            return None

    def multipoly2poly(self, in_lyr, out_lyr):
        for in_feat in in_lyr:
            geom = in_feat.GetGeometryRef()
            if geom.GetGeometryName() == 'MULTIPOLYGON':
                for geom_part in geom:
                    self.addPolygon(geom_part.ExportToWkb(), out_lyr)
            else:
                self.addPolygon(geom.ExportToWkb(), out_lyr)

    def addPolygon(self, simplePolygon, out_lyr):
        featureDefn = out_lyr.GetLayerDefn()
        polygon = ogr.CreateGeometryFromWkb(simplePolygon)
        out_feat = ogr.Feature(featureDefn)
        out_feat.SetGeometry(polygon)
        out_lyr.CreateFeature(out_feat)
        # print('Polygon added.')


    def createDS(self, ds_name, ds_format, geom_type, srs, overwrite=False):
        """ code taken from
        https://stackoverflow.com/questions/47038407/dissolve-overlapping-polygons-with-gdal-ogr-while-keeping-non-connected-result
        """

        drv = ogr.GetDriverByName(ds_format)
        if os.path.exists(ds_name) and overwrite is True:
            for filename in glob.glob(ds_name + "*"):
                os.remove(filename)
        ds = drv.CreateDataSource(ds_name)
        lyr_name = os.path.splitext(os.path.basename(ds_name))[0]
        lyr = ds.CreateLayer(lyr_name, srs, geom_type)
        return ds, lyr

    def dissolve(self, input, output, multipoly=False, overwrite=False):
        """ code taken from
        https://stackoverflow.com/questions/47038407/dissolve-overlapping-polygons-with-gdal-ogr-while-keeping-non-connected-result
        """
        ds = ogr.Open(str(input))
        lyr = ds.GetLayer()
        out_ds, out_lyr = self.createDS(output, ds.GetDriver().GetName(), lyr.GetGeomType(), lyr.GetSpatialRef(), overwrite)
        defn = out_lyr.GetLayerDefn()
        multi = ogr.Geometry(ogr.wkbMultiPolygon)
        for feat in lyr:
            if feat.geometry():
                feat.geometry().CloseRings() # this copies the first point to the end
                wkt = feat.geometry().ExportToWkt()
                multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))
        union = multi.UnionCascaded()
        if multipoly is False:
            for geom in union:
                poly = ogr.CreateGeometryFromWkb(geom.ExportToWkb())
                feat = ogr.Feature(defn)
                feat.SetGeometry(poly)
                out_lyr.CreateFeature(feat)
        else:
            out_feat = ogr.Feature(defn)
            out_feat.SetGeometry(union)
            out_lyr.CreateFeature(out_feat)
            out_ds.Destroy()

        ds.Destroy()
        return True

    def get_footprint_from_simple_poly(self, input_path):
        """Converts input vector file into a WKT footprint.

        Used to do a conversion of a simple input polygon vector. No
        multipoly and vertices < 200.

        Args:
            input_path (str): Path to the input vector polygon.

        Returns:
            (str): Wellknown Text repr of the single polygon input, or None
                if something went wrong with the conversion.

        """

        # Convert SHP or KML to GEOJSON here
        if Path(input_path).suffix == '.shp':
            self.logger.debug('Input area mask is a SHP')
            in_driver = ogr.GetDriverByName('ESRI Shapefile')

        elif Path(input_path).suffix == '.kml':
            self.logger.debug('Input area mask is a KML')
        elif Path(input_path).suffix == '.geojson':
            self.logger.debug('Input area mask is a GEOJSON')
            in_driver = ogr.GetDriverByName('GeoJson')

        self.logger.info('input_path: %s', input_path)

        data_source = in_driver.Open(input_path, 0)

        if data_source:

            layer = data_source.GetLayer()
            self.logger.debug('layer is {}'.format(layer))

            if (layer.GetFeatureCount() > 1):
                self.logger.info('Too many polygons in the input, cant be a simple \
                poly')
                return None

            # iterate over the features and grab the first one, since we know
            # there is no more features in the layer
            for feature in layer:
                return feature.GetGeometryRef().Simplify(0.01).ExportToWkt()

        else:

            self.logger.debug('Data source not working')
            return None

    def get_polygon_for_path_row(self, path, row):
        # takes a path and row, returns a WKT polygon representing the extent of the path row
        wrs2_desc_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'wrs2_desc.shp')
        self.logger.debug(f'+++++++++++++++++++ {os.path.dirname(os.path.realpath(__file__))} ++++++++++++++')
        self.logger.debug(f'=============== {__file__}=====================')
        self.logger.debug(wrs2_desc_path)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(wrs2_desc_path, 0)

        layer = dataSource.GetLayer()

        wkt_poly = None

        for feature in layer:
            p = feature.GetField("PATH")
            if p == path:
                r = feature.GetField("ROW")
                if r == row:
                    wkt_poly = feature.GetGeometryRef().ExportToWkt()

        layer.ResetReading()

        return wkt_poly

    def check_poly_intersection(self, poly_wkt1, poly_wkt2):
        ''' Takes 2 poly in wkt format, used ogr to create geomtry,
            checks for intersection, returns true or false
        '''

        poly1 = ogr.CreateGeometryFromWkt(poly_wkt1)
        poly2 = ogr.CreateGeometryFromWkt(poly_wkt2)

        intersection = poly1.Intersection(poly2)

        if intersection.IsEmpty():
            return False
        else:
            return True


if __name__ == '__main__':
    pass