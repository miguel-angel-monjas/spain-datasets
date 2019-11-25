#!/usr/bin/env python
# coding: utf-8
"""Turns census tracts shapefiles from the Spain National Statistics Institute into GeoJSON

Conversion from shape files into GeoJSON is made according to Alexis de Varennes'
answer in Stackoverflow
(https://stackoverflow.com/questions/43119040/shapefile-into-geojson-conversion-python-3).

Coordinate unprojection (from UTM to WSG84) uses scripts from Tom Payne (see
https://gist.github.com/twpayne/4409500)
"""
from io import BytesIO
import json
import logging
import os
import pandas as pd
import requests
import shutil
import time
import zipfile

import geojson
import shapefile

from utm_convert import unproject

__author__ = "Miguel-Angel Monjas"
__copyright__ = "Copyright 2019"
__credits__ = ["Miguel-Angel Monjas", "Alexis de Varennes", "Tom Payne"]
__license__ = "Apache 2.0"
__version__ = "0.1.2"
__maintainer__ = "Miguel-Angel Monjas"
__email__ = "mmonjas@gmail.com"
__status__ = "Proof-of-Concept"


HEMISPHERE = "N"
MAIN_ZONE = 30
CANARY_ISLANDS_ZONE = 28

BASE_URL = 'https://www.ine.es/prodyser/cartografia/'
YEAR = 2019

logging.basicConfig(level=logging.INFO)

def main():
    start = time.time()
    logging.info("Starting transformation process")
    current_folder = os.getcwd()
    parent_folder = os.path.dirname(current_folder)

    # ISO codes extraction
    data_folder = os.path.join(parent_folder, 'data')
    iso_codes_file_path = os.path.join(data_folder, 'ISO 3166-2.csv')
    
    iso_codes_df = pd.read_csv(iso_codes_file_path, sep='\t')
    iso_codes_aut_com_df = iso_codes_df[(iso_codes_df['categoría de subdivisión'] == 'comunidad autónoma') | (iso_codes_df['categoría de subdivisión'] == 'ciudad autónoma')]
    iso_codes = list(iso_codes_aut_com_df['código 3166-2'].unique())
    autonomous_communities = list(iso_codes_aut_com_df['nombre de la subdivisión'].unique())

    # census tracts extraction
    census_tracts_folder = os.path.join(parent_folder, 'data', 'census')
    if not os.path.exists(census_tracts_folder):
        os.mkdir(census_tracts_folder)
        logging.info(f"Folder {census_tracts_folder} created")

    aut_com_dict = dict(zip(autonomous_communities, iso_codes))

    # Save the files in a local folder
    url = f'{BASE_URL}seccionado_{YEAR}.zip'
    logging.info(f"Retrieving {url}")
    response = requests.get(url)
    logging.info("File retrieved")
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_folder = os.path.join(os.getcwd(), f'seccionado{YEAR}')
        zip_ref.extractall(zip_folder)
        logging.info(f"Zip archive extracted to {zip_folder}")

    # Read the shapefile from the folder
    sf = shapefile.Reader(os.path.join(zip_folder, f"SECC_CE_{YEAR}0101.sbn"))
    logging.info(f"Found {len(sf)} shapes")
    fields = sf.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    buffer_aut_comm = {}
    for code in iso_codes:
        buffer_aut_comm[code] = []

    # Iterate over the shape records and transform them to the GeoJSON formal
    for counter, sr in enumerate(sf.shapeRecords()):
        if (counter + 1) % 1000 == 0:
            logging.info(f"Processed {counter + 1} shapes")
        atr = dict(zip(field_names, sr.record))
        if atr['NCA'] == "Islas Canarias":
            zone = CANARY_ISLANDS_ZONE
        else:
            zone = MAIN_ZONE

        geom = sr.shape.__geo_interface__
        converted_geom = {"type": geom['type'], "coordinates": []}
        if geom['type'] == 'MultiPolygon':
            for i, element_i in enumerate(geom['coordinates']):
                converted_geom['coordinates'].append([])
                for j, element_j in enumerate(element_i):
                    converted_geom['coordinates'][i].append([])
                    for k, element_k in enumerate(element_j):
                        point = list(element_k)
                        x2, y2 = unproject(zone, HEMISPHERE, point[0], point[1])
                        converted_geom['coordinates'][i][j].append([x2, y2])
        elif geom['type'] == 'Polygon':
            for i, element_i in enumerate(geom['coordinates']):
                converted_geom['coordinates'].append([])
                for j, element_j in enumerate(element_i):
                    point = list(element_j)
                    x2, y2 = unproject(zone, HEMISPHERE, point[0], point[1])
                    converted_geom['coordinates'][i].append([x2, y2])
        buffer.append(dict(type="Feature", geometry=converted_geom, properties=atr))

        # Saving autonomous communities
        if atr['NCA'] in aut_com_dict:
            pol = dict(type="Feature", geometry=converted_geom, properties=atr)
            geojson_str = json.dumps(pol)
            geojson_object = geojson.loads(geojson_str)
            if not geojson_object.is_valid:
                print(geojson_object.errors())
                print(json.dumps(pol))
            buffer_aut_comm[aut_com_dict[atr['NCA']]].append(pol)

    # write the GeoJSON file
    geojson_file_path = os.path.join(census_tracts_folder, f"SECC_CE_{YEAR}0101.json")
    geojson_file = open(geojson_file_path, "w", encoding="utf-8")
    geojson_file.write(json.dumps({"type": "FeatureCollection", "features": buffer}) + "\n")
    geojson_file.close()
    logging.info(f"File SECC_CE_{YEAR}0101.json created")

    for code in iso_codes:
        file_path = os.path.join(census_tracts_folder, f"SECC_CE_{code}_{YEAR}0101.json")
        geojson_file = open(file_path, "w", encoding="utf-8")
        geojson_file.write(json.dumps({"type": "FeatureCollection", "features": buffer_aut_comm[code]}) + "\n")
        geojson_file.close()
        logging.info(f"File SECC_CE_{code}_{YEAR}0101.json created")

    try:
        shutil.rmtree(zip_folder)
        logging.info(f"Removing {zip_folder} folder")
    except PermissionError:
        logging.warning(f"Shape files not released. Cannot delete {zip_folder}")

    logging.info(f"Transformation process has taken {time.time() - start} seconds")


if __name__ == "__main__":
    main()
