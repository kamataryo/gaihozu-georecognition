#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script imports a gaihozu (外邦図) published in Stanford Digital Repository (https://purl.stanford.edu/) to Map Warper.
"""

import argparse
import json
import sys
import re
import requests
from json_generator import generate_json

parser = argparse.ArgumentParser(description='generate a json file from a CSV to import a map to Map Warper.')
parser.add_argument('map', type=str, help='name of the map you import')
parser.add_argument('url', type=str, help='Map Warper URL')
parser.add_argument('-u', '--user', action='store', type=str, required=True, help='a username')
parser.add_argument('-p', '--password', action='store', type=str, required=True, help='the password for the username')
"""
MAP_NAME = parser.parse_args().map
USER = parser.parse_args().user
PASSWORD = parser.parse_args().password
URL = parser.parse_args().url

"""
MAP_NAME = "gomanbunnoichichikeizu898.jpg"
USER = "super@example.com"
PASSWORD = "your_password"
URL = "http://ec2-52-198-241-210.ap-northeast-1.compute.amazonaws.com:8080"


authentication_url = URL + "/u/sign_in.json"
authentication_url = re.sub(r'//u/sign_in', '/u/sign_in', authentication_url)

authentication_headers = {"Content-Type": "application/json"}

authentication_data = {"email": USER, "password": PASSWORD}
authentication_data = {"user": authentication_data}
authentication_data = json.dumps(authentication_data)

s = requests.Session()
s.post(authentication_url, headers=authentication_headers, data=authentication_data)

import_headers = authentication_headers = {"Content-Type": "application/json", "Accept": "application/json"}

import_url = URL + "/api/v1/maps"
import_url = re.sub(r'//api/vi', '/api/vi', import_url)

import_data = generate_json(MAP_NAME)

response = s.post(import_url, headers=import_headers, data=import_data, stream=True)

print(response)
