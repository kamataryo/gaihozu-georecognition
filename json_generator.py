#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script contains a function which generates a json to import a map to Map Warper.
"""

def generate_json(map_path, csv_path):

    import base64
    import csv
    import json
    import os

    map_name = os.path.basename(map_path)

    with open(csv_path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        header = list(readCSV)[0]

    with open(csv_path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if map_name in row:
                attributes = list(row)

    attributes = dict(zip(header, attributes))

    with open(map_path, 'rb') as map_file:
        encoded_file = base64.b64encode(map_file.read())
    
    attributes["upload"] = "data:image/jpeg;base64," + str(encoded_file)[1:]  # [1:] is necessary to remove the begging "b"

    attributes["upload_file_name"] = map_name

    attributes = {k: v for k, v in attributes.items() if v and v[0]}

    import_json = {"data": {"type": "maps", "attributes": attributes}}
    import_json = json.dumps(import_json)  # .encode('utf-8')

    return import_json

