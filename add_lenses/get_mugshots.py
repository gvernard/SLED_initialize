import json                    
import pandas as pd

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

# Specify the directory where the mugshot for each lens is found
mugshot_dir = "../../initialize_database_data/images_to_upload/initial_mugshots/"
csv_dir = "../../initialize_database_data/add_lenses_csvs/"

N = int(sys.argv[1])
Nmax = int(sys.argv[2])

#image_files = []
csvs = np.sort(glob.glob(csv_dir+'*.csv'))

for i, eachcsv in enumerate(csvs):
    print(i, len(csvs))
    if (i<N) or (i>Nmax):
        continue

    lens_dicts = []
    data = pd.read_csv(eachcsv, skipinitialspace=True)

    #this deals with nans where you have empty entries
    data = data.fillna({key:'' for key in data.keys()})
    print('Fetching mugshots of', len(data), 'systems for the paper:', eachcsv.split('/')[-1])
    for i in range(len(data)):
        lens_dict = data.iloc[i].to_dict()
        if lens_dict['imagename']=='':
            lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'
        if not os.path.exists(mugshot_dir+lens_dict['imagename']):
            try:
                print('trying panstarrs with ra, dec', lens_dict['ra'], lens_dict['dec'])
                panstarrs_utils.savecolorim(ra=lens_dict['ra'], dec=lens_dict['dec'], arcsec_width=10, outpath=mugshot_dir+lens_dict['imagename'])
            except Exception:
                try:
                    legacysurvey_utils.savecolorim(ra=lens_dict['ra'], dec=lens_dict['dec'], arcsec_width=10, outpath=mugshot_dir+lens_dict['imagename'], layer='ls-dr10')
                except Exception:
                    try:
                        legacysurvey_utils.savecolorim(ra=lens_dict['ra'], dec=lens_dict['dec'], arcsec_width=10, outpath=mugshot_dir+lens_dict['imagename'], layer='unwise-neo7')
                    except Exception:
                        print('No mugshot made for', lens_dict['name'])
                    
    #if not os.path.exists(mugshot_dir+lens_dict['imagename']):
    #    os.system('cp /Users/cameron/Desktop/comingsoon.png '+mugshot_dir+lens_dict['imagename'])


for i, eachcsv in enumerate(csvs):
    lens_dicts = []
    data = pd.read_csv(eachcsv, skipinitialspace=True)

    data = data.fillna({key:'' for key in data.keys()})
    for i in range(len(data)):
        lens_dict = data.iloc[i].to_dict()
        if lens_dict['imagename']=='':
            lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'
        if not os.path.exists(mugshot_dir+lens_dict['imagename']):
            print(mugshot_dir+lens_dict['imagename'], lens_dict['name'], lens_dict['ra'], lens_dict['dec'])