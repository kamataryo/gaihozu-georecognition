#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script imports a gaihozu (外邦図) published in Stanford Digital Repository (https://purl.stanford.edu/) to Map Warper.
"""

import argparse
import re
import sys
import json
import requests
from mapwarper_interface.json_generator import generate_json

parser = argparse.ArgumentParser(description='generate a json file from a CSV to import a map to Map Warper.')
parser.add_argument('map', type=str, help='path of the map you import')
parser.add_argument('url', type=str, help='Map Warper URL')
parser.add_argument('-u', '--user', action='store', type=str, required=True, help='a username')
parser.add_argument('-p', '--password', action='store', type=str, required=True, help='the password for the username')
parser.add_argument('-c', '--csv', action='store', type=str, required=True, help='path of a CSV file for the username')

MAP_PATH = parser.parse_args().map

USER = parser.parse_args().user
PASSWORD = parser.parse_args().password
URL = parser.parse_args().url
if URL[-1] == "/":
    URL = URL[:-1]

CSV_PATH = parser.parse_args().csv

authentication_url = URL + "/u/sign_in.json"
authentication_headers = {"Content-Type": "application/json"}

authentication_data = {"email": USER, "password": PASSWORD}
authentication_data = {"user": authentication_data}
authentication_data = json.dumps(authentication_data)

s = requests.Session()
s.post(authentication_url, headers=authentication_headers, data=authentication_data)

import_headers = {"Content-Type": "application/json", "Accept": "application/json"}
import_url = URL + "/api/v1/maps"
import_data = generate_json(MAP_PATH, CSV_PATH)

response = s.post(import_url, headers=import_headers, data=import_data)

