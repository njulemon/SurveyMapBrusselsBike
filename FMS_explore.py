import io
import json
from typing import Dict

import geopandas
import geoplot.crs
import matplotlib.pyplot as plt
import requests
import shapefile
import geoplot as gplt
from pyproj import CRS
from shapely.geometry import Polygon, Point
import geoplot.crs as gcrs

"""
useful link if crashing
https://stackoverflow.com/questions/69090235/plotting-a-heatmap-kernel-density-using-geopandas-geoplot-crashes-session/69096742#69096742
"""

def main():
    # read the map file
    sf = shapefile.Reader("Data/Map/UrbAdm_MUNICIPALITY")
    shapes = sf.shapes()
    records = sf.records()
    patches = []
    colors = []

    geo_array = dict()

    # data = get_data()

    for i in range(len(shapes)):
        geometry = Polygon([point for point in shapes[i].points])
        commune = records[i]['NAME_FRE']
        value = i

        geo_array.update({i: {'commune': commune, 'geometry': geometry, 'value': value}})

    gdf = geopandas.GeoDataFrame.from_dict(geo_array, orient='index', geometry='geometry', crs='EPSG:31370')
    gdf_ = gdf.to_crs(crs='epsg:4326')
    print(gdf_.crs)

    ax = gplt.polyplot(gdf_, projection=gcrs.AlbersEqualArea(), figsize=(12, 12))

    data = get_data(mode_api=False, filename='data.json', save=True)

    reports = dict()
    for idx, report in zip(range(len(data)), data):
        report_info = {
            idx: {
                'date': report['creationDate'],
                'geometry': Point(report['location']['coordinates']['x'], report['location']['coordinates']['y']),
                'name': report['category']['nameFr'],
                'actor': report['responsibleOrganisation']['nameFr']
            }
        }
        reports.update(report_info)

    reports_df = geopandas.GeoDataFrame.from_dict(reports, orient='index', geometry='geometry', crs=31370)

    reports_df_ = reports_df.to_crs(crs='epsg:4326')

    # gplt.kdeplot(
    #     reports_df_, cmap='viridis', figsize=(12, 12),
    #     shade=True, ax=ax, extent=gdf_.total_bounds
    # )

    gplt.pointplot(
        reports_df_, figsize=(16, 16),
        ax=ax, extent=gdf_.total_bounds
    )

    gplt.polyplot(gdf_, projection=gcrs.AlbersEqualArea(), ax=ax, facecolor='white')

    plt.show()

    print(gdf)


def get_data(mode_api: bool, filename: str = None, save: bool = False) -> Dict:
    if mode_api:
        print('ask a token on your application in https://api.brussels/store/site/pages/applications.jag')
        token = json.load(io.open('./token.json'))['token']

        headers = {'Accept': 'application/hal+json', 'Authorization': f'Bearer {token}'}

        categories = requests.get('https://api.brussels:443/api/fixmystreet/1.0.0/categories', headers=headers)

        print(json.dumps(categories.json()['response'], indent=4))

        start_date = '2021-01-01'
        end_date = '2022-03-01'

        size = 10_000

        category = 3407

        incidents = requests.get((
            f'https://api.brussels:443/api/fixmystreet/1.0.0/incidents'
            f'?category={category}&startDate={start_date}&endDate={end_date}&size={size}'),
            headers=headers
        )

        data = incidents.json()['_embedded']['response']

        if save:
            with open(filename, 'w') as file:
                json.dump(data, file)

        return data
    else:
        with open(filename) as file:
            data = json.load(file)

            return data


if __name__ == '__main__':
    main()
