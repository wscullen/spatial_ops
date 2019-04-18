import ogr
import argparse
import pathlib
import logging
import sys

# tasks:
# read in shapefile
# iterate over each polygon
# iterate over each point in the current polygon
# test each point against all other polygons, track if the point is inside
# other polygons
# if all points of the current polygon are inside any polygon that we test, we
# mark the current polygon for deletion

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def cli_setup():
    parser = argparse.ArgumentParser(
            description='Try to simplify a complex multipart polygon')

    parser.add_argument('-p', metavar='polygon', dest="polygon", action='store',
                        type=str,
                        help='Region to retrieve imagery. '
                             'Specify filename of polygon (SHP, GEOJSON, KML)')

    args = parser.parse_args()

    return args


def convert_shp_to_json(file_name):
    # Convert SHP or KML to GEOJSON here
    if pathlib.Path(file_name).suffix == '.shp':
        logging.info('Input area mask is a SHAPEFILE')
        in_driver = ogr.GetDriverByName('ESRI Shapefile')

        dataSource = in_driver.Open(file_name, 0)

        layer = dataSource.GetLayer()

        multipoly = ogr.Geometry(ogr.wkbMultiPolygon)

        geometryList = []
        allVertices = 0

        for i, feature in enumerate(layer):
            logging.debug('Feature----------------------------------------- ')
            logging.debug(feature.GetGeometryRef())
            logging.debug('count', i)

            convex_hull = feature.GetGeometryRef().ConvexHull()
            logging.debug('convex hull', convex_hull)
            simplified = convex_hull.Simplify(0.01)
            logging.debug('simplified: ', simplified)

            for j, point in enumerate(feature.GetGeometryRef()):
                logging.debug('PART OF FEATURE =================================')
                logging.debug(point)

                logging.debug('vertices', point.GetPointCount())
                logging.debug('part count', j)
                allVertices += point.GetPointCount()

            multipoly.AddGeometry(simplified)

        logging.debug(multipoly)

        simplifiedVertices = 0
        newPoly = ogr.Geometry(ogr.wkbMultiPolygon)

        multipolyList = []

        for thing in multipoly:
            logging.debug(thing)

            for simple in thing:
                logging.debug(simple)
                logging.debug(simple.GetPointCount())

                if simplifiedVertices + simple.GetPointCount() > 200:
                    logging.debug('reached maxiumum vertices size, creating new polygon')
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(simple)
                    newPoly.AddGeometry(poly)
                    multipolyList.append(newPoly)
                    newPoly = ogr.Geometry(ogr.wkbMultiPolygon)

                    simplifiedVertices = 0

                else:
                    logging.debug('still space in this multi poly')
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(simple)
                    newPoly.AddGeometry(poly)

                simplifiedVertices += simple.GetPointCount()


        logging.debug('finished')
        logging.debug('Simplified Vertices: ', simplifiedVertices)

        # write out the multipoly of the simple coverage
        out_driver = ogr.GetDriverByName('GeoJSON')

        # Create the output GeoJSON
        out_data_source = out_driver.CreateDataSource(
            str(pathlib.PurePath('simplifiedquerytest.geojson')))
        out_layer = out_data_source.CreateLayer(
            str(pathlib.PurePath('simplifiedquerytest.geojson')),
            geom_type=ogr.wkbPolygon)

        # Get the output Layer's Feature Definition
        feature_defn = out_layer.GetLayerDefn()

        for it in multipolyList:
            logging.debug(it)

            # create a new feature
            out_feature = ogr.Feature(feature_defn)

            # Set new geometry
            out_feature.SetGeometry(it)

            # Add new feature to output Layer
            out_layer.CreateFeature(out_feature)


            vertexCount = 0
            for i in it:
                logging.debug(i)
                for j in i:
                    vertexCount += j.GetPointCount()

            logging.debug('VertexCount', vertexCount)

        logging.debug('All Vertices in file', allVertices)

        return multipolyList

if __name__ == 'main':
    args = cli_setup()

    convert_shp_to_json(args.polygon)