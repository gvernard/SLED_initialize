import json                    
import requests
from requests.auth import HTTPBasicAuth
import glob
import django
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.test import Client

c = Client(SERVER_NAME='localhost')
c.login(username='admin', password='123')


# Specify the json file with the papers' properties
collections = glob.glob('../../initialize_database_data/add_collections_jsons/*json')


for collection_json in collections:
    # Opening the JSON file with the lens properties
    f = open(collection_json)
    data = json.load(f)
    f.close()


    # Sending the request
    r  = c.post('/api/upload-collection/', data=data, content_type="application/json")


    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print("Something went wrong!")
    print(r.content)
