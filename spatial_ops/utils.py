from osgeo import ogr, osr

ogr.UseExceptions()

def polygons_intersect(polygon1, polygon2):
    """Given 2 polygons defined as WKT strings, return True if they intersect"""
    poly1 = ogr.CreateGeometryFromWkt(polygon1)
    poly2 = ogr.CreateGeometryFromWkt(polygon2)

    print(poly1)
    print(poly2)

    intersection = poly1.Intersects(poly2)
    print(intersection)
    if intersection:
        print('INTERSECT FOUND')
    else:
        print('NO INTERSECT FOUND')

    return True if intersection else False
   