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

csv_dir = "../../initialize_database_data/add_lenses_csvs/"
csvs = np.sort(glob.glob(csv_dir+'*.csv'))

datas = []
for file in csvs:
    data = pd.read_csv(file)
    data = data.fillna('')
    
    data = data[list(data.keys()[:-2])]
    
    year = int(file.split('/')[-1][:4])
    data['year'] = year
    datas.append(data)

all_data = pd.concat(datas,ignore_index=True)

ras = all_data['ra'].to_numpy().astype('float')
decs = all_data['dec'].to_numpy().astype('float')

def match_to_year(ra, dec, radius=5.):
    dists = 3600.*((np.cos(dec*np.pi/180.)*(ras-ra))**2. + (decs-dec)**2.)**0.5
    kappa = np.where(dists<radius)[0]
    years = all_data['year'][kappa].values
    return years.min()

#image_files = []
jsons = np.sort(glob.glob(json_dir+'*.json'))
#jsons = jsons[200:]
for i, eachjson in enumerate(jsons):
    print(i, eachjson)
    #if i<142:
    #    continue

    f = open(eachjson)
    data = json.load(f)
    f.close()
    year = int(data[0]['bibcode'][:4])

    for k in range(len(data[0]['lenses'])):
        system = data[0]['lenses'][k]
        ra, dec = system['ra'], system['dec']
        if year-match_to_year(ra, dec)>2:
            system['discovery'] = False

    r  = c.post('/api/upload-papers/', data=data, content_type="application/json")

    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print("Something went wrong!")
        print(eachjson)
        df
    #x = input()
    #print(r.text)

