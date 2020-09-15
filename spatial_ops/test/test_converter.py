import unittest
from pathlib import Path
import datetime
import os
import json
import time

from .. import converter as conv

# Python 3 with pathlib
# For the directory of the script being run:
# pathlib.Path(__file__).parent.absolute()
# For the current working directory:

TEST_DIR = Path(__file__).absolute().parent
GRID_DIR = Path(TEST_DIR.parent, "grid_files")

class TestConverter(unittest.TestCase):

    def setUp(self):
        self.test_polygon_shapefile = Path(TEST_DIR, "data", "lethbridge_rdc_area_wgs84.shp")
        self.test_polygon_geojson_string = '{ "type": "Polygon", "coordinates": [ [ [ -112.779560139758999, 49.932275503662368 ], [ -112.431137893719537, 49.931095084815254 ], [ -112.429304092424587, 49.60835285286938 ], [ -112.774975636521646, 49.611917681051217 ], [ -112.776809437816581, 49.684345985047244 ], [ -112.779560139758999, 49.932275503662368 ] ] ] }'
        self.test_polygon_wkt_string = "POLYGON ((-112.779560139759 49.9322755036624,-112.43113789372 49.9310950848153,-112.429304092425 49.6083528528694,-112.774975636522 49.6119176810512,-112.776809437817 49.6843459850472,-112.779560139759 49.9322755036624))"

    def test_shapefile_to_geojson(self):
        converter = conv.Converter()
        geojson_string = converter.shapefile_to_geojson(str(self.test_polygon_shapefile))
        print(geojson_string)
        self.assertEqual(geojson_string, self.test_polygon_geojson_string)

    def test_shapefile_to_wkt(self):
        converter = conv.Converter()
        wkt_string = converter.shapefile_to_wkt(str(self.test_polygon_shapefile))
        print(wkt_string)
        self.assertEqual(wkt_string, self.test_polygon_wkt_string)

if __name__ == '__main__':
    unittest.main()