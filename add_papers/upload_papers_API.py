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
import socket

sys.path.append('../../SLED_api/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.test import Client

hostname = socket.gethostbyname(socket.gethostname())
c = Client(SERVER_NAME=hostname)
c.login(username='admin', password='123')


# Specify the directory where the mugshot for each lens is found
json_dir = "../../initialize_database_data/add_papers_csvs/"



#image_files = []
jsons = np.sort(glob.glob(json_dir+'*.json'))
#jsons = jsons[200:]
for i, eachjson in enumerate(jsons):
    print(i, eachjson)
    #if i<191:
    #    continue

    f = open(eachjson)
    data = json.load(f)
    f.close()



    r  = c.post('/api/upload-papers/', data=data, content_type="application/json")

    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print("Something went wrong!")
        print(eachjson)
    #x = input()
    #print(r.text)

