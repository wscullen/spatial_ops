# Spatial_Ops

Python module for working with MGRS and WRS2 tile grids. Can determine the list of MGRS and WRS tile ids that intersect a given shapefile. Converts between MGRS and WRS. Can generate the WKT footprint for tile id, or create a shapefile from a list of tiles.

## Usage

This module is useful for generating tile id lists from an Area of Interest shapefile. See the `test_grid_intersect.py` file for usage examples.

## Dependencies

GDAL 2.2.*, GDAL Python bindings are required.

## Required Data Files

This module relies on shapefiles for the WRS2 and MGRS grids to work. Download the data files from here:

https://drive.google.com/open?id=1okNgc2V6ZTpWQOFZ-p_zNNa-sGaBwQtc

Place the `grid_files` directory in the module root directory. Place the `data` directory in the `test` directory.
