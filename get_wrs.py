import ogr
import shapely.geometry
import shapely.wkt

class ConvertToWRS:

    def __init__(self, shapefile="./wrs2_descending.shp"):
        self.shapefile = ogr.Open(shapefile)
        self.layer = self.shapefile.GetLayer(0)

        self.polygons = []

        for i in range(self.layer.GetFeatureCount()):
            feature = self.layer.GetFeature(i)
            path = feature['PATH']
            row = feature['ROW']
            geom = feature.GetGeometryRef()
            shape = shapely.wkt.loads(geom.ExportToWkt())
            self.polygons.append((shape, path, row))


    def get_wrs(self, lat, lon):
        pt = shapely.geometry.Point(lon, lat)
        res = []
        for poly in self.polygons:
            if pt.within(poly[0]):
                res.append({'path': poly[1], 'row': poly[2]})

        return res