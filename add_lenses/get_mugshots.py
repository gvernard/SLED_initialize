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
import django

sys.path.append('../../SLED_api/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()


from lenses.models import Catalogue, Instrument, Band, Users, Lenses

sys.path.append('../add_data/')
import panstarrs_utils
import  legacysurvey_utils
import glob

download_missing_images_from_panstarrs_or_des = True


# Specify the directory where the mugshot for each lens is found
mugshot_dir = "../../initialize_database_data/images_to_upload/initial_mugshots/"
csv_dir = "../../initialize_database_data/add_lenses_csvs/"


#image_files = []
csvs = np.sort(glob.glob(csv_dir+'*.csv'))


allupdates = []
for eachcsv in csvs:

    lens_dicts = []
    data = pd.read_csv(eachcsv, skipinitialspace=True)

    #this deals with nans where you have empty entries
    data = data.fillna({key:'' for key in data.keys()})
    for i in range(len(data)):
        lens_dict = data.iloc[i].to_dict()

        if lens_dict['imagename']=='':
            lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'
        print(lens_dict['name'])
        if not os.path.exists(mugshot_dir+lens_dict['imagename']):
            print('The following mugshot does not exist:', mugshot_dir+lens_dict['imagename'])

            if download_missing_images_from_panstarrs_or_des:
                print('Querying PS to make it')
                try:
                    print('trying panstarrs with ra, dec', lens_dict['ra'], lens_dict['dec'])
                    panstarrs_utils.savecolorim(ra=lens_dict['ra'], dec=lens_dict['dec'], arcsec_width=10, outpath=mugshot_dir+lens_dict['imagename'])
                except Exception:
                    try:
                        legacysurvey_utils.savecolorim(ra=lens_dict['ra'], dec=lens_dict['dec'], arcsec_width=10, outpath=mugshot_dir+lens_dict['imagename'])
                    except Exception:
                        pass
