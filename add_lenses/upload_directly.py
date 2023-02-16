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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.test import Client
from lenses.models import Catalogue, Instrument, Band, Users, Lenses

import glob


# Specify the directory where the mugshot for each lens is found
mugshot_dir = "../../initialize_database_data/images_to_upload/initial_mugshots/"
csv_dir = "../../initialize_database_data/add_lenses_csvs/"

c = Client(SERVER_NAME='localhost')
c.login(username='admin', password='123')

#image_files = []
csvs = np.sort(glob.glob(csv_dir+'*.csv'))


allupdates = []
for eachcsv in csvs:

    lens_dicts = []
    data = pd.read_csv(eachcsv, skipinitialspace=True)

    #this deals with nans where you have empty entries
    data = data.fillna({key:'' for key in data.keys()})

    #loop through each lens in the paper csv
    for i in range(len(data)):
        lens_dict = data.iloc[i].to_dict()

        if lens_dict['imagename']=='':
            lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'

        img = cv2.imread(mugshot_dir+lens_dict['imagename'])
        string_img = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        lens_dict['mugshot'] = string_img 

        #CHECK IF LENS ALREADY EXISTS
        user = Users.objects.get(username='admin')
        lensdata = {'ra':lens_dict['ra'], 'dec':lens_dict['dec'], 'radius':10., 'user':user}
        r  = c.post('/api/query-lenses/', data=lensdata)

        dbquery = json.loads(r.content)
        dblenses = dbquery['lenses']
        
        if len(dblenses)>0:
            dblens = dblenses[0]

            update_data = {'ra':dblens['ra'], 'dec':dblens['dec']}
            send_update = False

            #CONSTRUCT UPDATE PARAMETER LIST
            for field in dblens.keys():
                #ONLY UPDATE FIELDS THAT ARE GIVEN
                if (field in lens_dict.keys()):
                    #AND ARE NOT EMPTY
                    if lens_dict[field]!='':
                        value = lens_dict[field]
                        if (value=='') & (field!='info'):
                            value = None
                        if (value==None)&(field=='z_lens_secure'):
                            value = False
                        if field in ['image_conf', 'lens_type', 'source_type']:
                            if value!=None:
                                value = [x.strip() for x in value.split(',')]
                            else:
                                value = []
                        if value!=dblens[field]:
                            send_update = True
                            print(field)
                            print('new value', value)
                            print('old value', dblens[field])
                            if field=='name':
                                if lens_dict['flag_discovery']:
                                    #print('Would you like to add this name and the current name to the alternative names list? And change the name to J...')
                                    #answer = input()
                                    #if answer.lower()=='y':
                                    if 1==1:
                                        oldname = dblens['name']
                                        for i, character in enumerate(oldname):
                                            if character.isdigit():
                                                break
                                        newname = 'J'+oldname[i:]
                                        if dblens['alt_name']:
                                            altname = dblens['alt_name']+', '+oldname
                                        else:
                                            altname = oldname+', '+lens_dict['name']

                                        update_data['name'] = newname
                                        update_data['alt_name'] = altname
                            else:
                                update_data[field] = lens_dict[field]
                                

            if send_update:
                allupdates.append(update_data)

        else:
            lens_dicts.append(lens_dict)

    form_data = lens_dicts
    if len(form_data)==0:
        continue

    # Sending the request
    r  = c.post('/api/upload-lenses/', data=form_data, content_type="application/json")

    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print(r.text)
        if 'duplicates' in r.text:
            print("Something went wrong!")
            wait = input()
            print('d///f')
    
r  = c.post('/api/update-lens/', data=allupdates, content_type="application/json")