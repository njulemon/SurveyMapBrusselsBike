from typing import Tuple

from pyproj import CRS, Transformer


class LambertTransformer:

    def __init__(self):
        crs_lambert_72 = CRS.from_epsg(31370)
        crs_wgs_84 = CRS.from_epsg(4326)
        self.transformer = Transformer.from_crs(crs_lambert_72, crs_wgs_84)

    def transform2coordinates(self, x, y) -> Tuple[float, float]:
        return self.transformer.transform(x, y)


def test():
    trans = LambertTransformer()
    print(trans.transform2coordinates(*(150032, 170637)))


if __name__ == '__main__':
    test()
