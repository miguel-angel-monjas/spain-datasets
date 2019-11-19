#!/usr/bin/env python
# coding: utf-8

import geojson
from io import BytesIO
import json
import logging
import os
import requests
import shapefile
import shutil
import time
import zipfile
from utm_convert import unproject

aut_com = ['Andalucía',
           'Aragón',
           'Canarias',
           'Cantabria',
           'Castilla y León',
           'Castilla-La Mancha',
           'Cataluña',
           'Ceuta',
           'Comunidad Foral de Navarra',
           'Comunidad de Madrid',
           'Comunitat Valenciana',
           'Extremadura',
           'Galicia',
           'Illes Balears',
           'La Rioja',
           'Melilla',
           'País Vasco',
           'Principado de Asturias',
           'Región de Murcia']

iso_codes = ['ES-AN', 'ES-AR', 'ES-CN', 'ES-CB', 'ES-CL', 'ES-CM', 'ES-CT', 'ES-CE', 'ES-NC',
             'ES-MD', 'ES-VC', 'ES-EX', 'ES-GA', 'ES-IB', 'ES-RI', 'ES-ML', 'ES-PV', 'ES-AS', 'ES-MC']

hemisphere = "N"

logging.basicConfig(level=logging.INFO)


def main():
    start = time.time()
    logging.info("Starting transformation process")
    current_folder = os.getcwd()
    census_tracts_folder = os.path.join(current_folder, 'data', 'census')
    if not os.path.exists(census_tracts_folder):
        os.mkdir(census_tracts_folder)
        logging.info(f"Folder {census_tracts_folder} created")

    aut_com_dict = dict(zip(aut_com, iso_codes))

    # From https://stackoverflow.com/questions/43119040/shapefile-into-geojson-conversion-python-3
    # (to transform shape files)
    # From https://gist.github.com/twpayne/4409500
    # (to handle properly the coordinates)
    # Save the files in a folder
    url = 'https://www.ine.es/prodyser/cartografia/seccionado_2019.zip'
    response = requests.get(url)
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_folder = os.path.join(os.getcwd(), 'seccionado2019')
        zip_ref.extractall(zip_folder)
        logging.info(f"Zip archive extracted to {zip_folder}")
    # Read the shapefile from the folder
    sf = shapefile.Reader(os.path.join(zip_folder, "SECC_CE_20190101.sbn"))
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
            zone = 28
        else:
            zone = 30

        geom = sr.shape.__geo_interface__
        converted_geom = {"type": geom['type'], "coordinates": []}
        if geom['type'] == 'MultiPolygon':
            for i, element_i in enumerate(geom['coordinates']):
                converted_geom['coordinates'].append([])
                for j, element_j in enumerate(element_i):
                    converted_geom['coordinates'][i].append([])
                    for k, element_k in enumerate(element_j):
                        point = list(element_k)
                        x2, y2 = unproject(zone, hemisphere, point[0], point[1])
                        converted_geom['coordinates'][i][j].append([x2, y2])
        elif geom['type'] == 'Polygon':
            for i, element_i in enumerate(geom['coordinates']):
                converted_geom['coordinates'].append([])
                for j, element_j in enumerate(element_i):
                    point = list(element_j)
                    x2, y2 = unproject(zone, hemisphere, point[0], point[1])
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
    geojson_file = open("SECC_CE_20190101.json", "w", encoding="utf-8")
    geojson_file.write(json.dumps({"type": "FeatureCollection", "features": buffer}) + "\n")
    geojson_file.close()
    logging.info("File SECC_CE_20190101.json created")

    for code in iso_codes:
        file_path = os.path.join(census_tracts_folder, f"SECC_CE_{code}_20190101.json")
        geojson_file = open(file_path, "w", encoding="utf-8")
        geojson_file.write(json.dumps({"type": "FeatureCollection", "features": buffer_aut_comm[code]}) + "\n")
        geojson_file.close()
        logging.info(f"File SECC_CE_{code}_20190101.json created")

    try:
        shutil.rmtree(zip_folder)
        logging.info(f"Removing {zip_folder} folder")
    except PermissionError:
        logging.warning(f"Files not released. Cannot delete {zip_folder}")

    logging.info(f"Transformation process has taken {time.time() - start} seconds")


if __name__ == "__main__":
    main()
