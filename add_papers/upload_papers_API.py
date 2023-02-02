import json                    
import requests
from requests.auth import HTTPBasicAuth
#import csv
import pandas as pd
#from PIL import Image
import numpy as np
import cv2
import base64
import os
import sys
import glob
import django

sys.path.append('../../SLED_api/')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.test import Client

c = Client(SERVER_NAME='localhost')
c.login(username='admin', password='123')

# Specify the URL for the request to be sent
#url = "http://127.0.0.1:8000/api/upload-papers/"

# Specify the directory where the mugshot for each lens is found
json_dir = "../../initialize_database_data/add_papers_csvs/"



#image_files = []
jsons = np.sort(glob.glob(json_dir+'*.json'))

for eachjson in jsons:

    f = open(eachjson)
    data = json.load(f)
    f.close()



    #r = requests.post(url,json=data,auth=HTTPBasicAuth('Cameron','123'))
    r  = c.post('/api/upload-papers/', data=data, content_type="application/json")

    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print("Something went wrong!")
        print(eachjson)
    #x = input()
    #print(r.text)

