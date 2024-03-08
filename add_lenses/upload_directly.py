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
import socket

sys.path.append('../../SLED_api/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.test import Client
from lenses.models import Catalogue, Instrument, Band, Users, Lenses

import glob

print('uploading lenses asfijdajsdnasjidknaskj')


# Specify the directory where the mugshot for each lens is found
mugshot_dir = "../../initialize_database_data/images_to_upload/initial_mugshots/"
csv_dir = "../../initialize_database_data/add_lenses_csvs/"

hostname = socket.gethostbyname(socket.gethostname())

print(hostname)
c = Client(SERVER_NAME=hostname)
c.login(username='admin', password='123')

#image_files = []
csvs = np.sort(glob.glob(csv_dir+'*.csv'))
#csvs = csvs[171:]


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

'''#check that there are no <5" duplicates in any csv
for eachcsv in csvs:
    data = pd.read_csv(eachcsv, skipinitialspace=True)

    #this deals with nans where you have empty entries
    data = data.fillna({key:'' for key in data.keys()})
    ras = data['ra']
    decs = data['dec']
    if len(ras)>1:
        for i in range(len(ras)):
            dists = 3600.*((np.cos(decs[i]*np.pi/180.)*(ras[i]-ras))**2. + (decs[i]-decs)**2.)**0.5
            if (dists<5).sum()>1:
                print('duplicatesss!!', eachcsv, ras[i], decs[i])
        print('passed')'''

for zzz, eachcsv in enumerate(csvs):
    #print(zzz,zzz,zzz)
    allupdates = []
    #if zzz < 234:
    #    continue
    #print(eachcsv)
    lens_dicts = []
    
    data = pd.read_csv(eachcsv, skipinitialspace=True)
    year = int(eachcsv.split('/')[-1][:4])

    #this deals with nans where you have empty entries
    data = data.fillna({key:'' for key in data.keys()})

    #loop through each lens in the paper csv
    for i in range(len(data)):
        #remove duplicate uploads, they are often multiple redshifts that were put into too many columns
        #Ive checked to make sure they are the same lens now...

        lens_dict = data.iloc[i].to_dict()
        if lens_dict['name'] in [lens['name'] for lens in lens_dicts]:
            print('duplicate name found, maybe need to rename the lens', lens_dict['name'], eachcsv) #, eachcsv)
            #dfdf
            continue
        lens_dict['access_level'] = 'PUB'
        lens_dict['name'] = lens_dict['name'].replace(' ', '')
        lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'

        if ',' in lens_dict['name']:
            lens_dict['altname'] = ','.join(lens_dict['name'].split(',')[1:])
            lens_dict['name'] = lens_dict['name'].split(',')[0]
        else:
            lens_dict['altname'] = ''
        lens_dict['ra'] = float("{:.5f}".format(lens_dict['ra']))
        lens_dict['dec'] = float("{:.5f}".format(lens_dict['dec']))
        if lens_dict['score']!='':
            lens_dict['score'] = float("{:.2f}".format(lens_dict['score']))
        if lens_dict['image_sep']!='':
            lens_dict['image_sep'] = float("{:.2f}".format(lens_dict['image_sep']))
        k = 0
        
        flags_dict = {'flag_confirmed':'CONFIRMED', 'flag_candidate':'CANDIDATE', 'flag_contaminant':'CONTAMINANT'}
        for flagstring in ['flag_confirmed', 'flag_candidate', 'flag_contaminant']:
            #print(lens_dict[flagstring])
            if lens_dict[flagstring] in ['F', '', False]:
                lens_dict[flagstring] = False
            else:
                lens_dict[flagstring] = True
            k += lens_dict[flagstring]
            if lens_dict[flagstring]:
                lens_dict['flag'] = flags_dict[flagstring]

        #if someone already reported the object 3 or more years ago, you cannot claim discovery
        if year-match_to_year(lens_dict['ra'], lens_dict['dec'])>2:
            lens_dict['flag_discovery'] = False

        if k==0:
            lens_dict['flag'] = 'CANDIDATE'
            k = 1

        if k!=1:
            print('bad!', lens_dict)
            df

        #if lens_dict['imagename']=='':
        #    lens_dict['imagename'] = lens_dict['name'].split(',')[0].strip()+'.png'

        img = cv2.imread(mugshot_dir+lens_dict['imagename'])
        string_img = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        lens_dict['mugshot'] = string_img 

        #CHECK IF LENS ALREADY EXISTS
        user = Users.objects.get(username='admin')
        lensdata = {'ra':lens_dict['ra'], 'dec':lens_dict['dec'], 'radius':5., 'user':user}
        r  = c.post('/api/query-lenses/', data=lensdata)

        dbquery = json.loads(r.content)
        dblenses = dbquery['lenses']
        '''if len(dblenses)==0:
            lensdata = {'ra':lens_dict['ra'], 'dec':lens_dict['dec'], 'radius':20., 'user':user}
            dbquery = json.loads(r.content)
            dblenses = dbquery['lenses']
            if len(dblenses)>0:
                if dblenses[0]['name']==lens_dict['name']:
                    print('20 arcsecond lens with name of ', lens_dict['name'])
                    df'''

        #what if there is a match?
        if len(dblenses)>0:
            dblens = dblenses[0]
            if len(dblenses)>1:
                print('why are there multiple matches?')
                df
            #no updates for a confirmed lens
            #if dblens['flag_confirmed']:
            #    continue
            update_data = {'ra':dblens['ra'], 'dec':dblens['dec']}
            send_update = False

            #CONSTRUCT UPDATE PARAMETER LIST
            for field in dblens.keys():
                #ONLY UPDATE FIELDS THAT ARE GIVEN
                if (field in lens_dict.keys()):
                    #AND ARE NOT EMPTY
                    if lens_dict[field]!='':
                        value = lens_dict[field]
                        if field in ['image_conf', 'lens_type', 'source_type']:
                            if value!=None:
                                value = [x.strip() for x in value.split(',')]
                            else:
                                value = []

                        if value!=dblens[field]:
                            send_update = True
                            ##print('new value', value)
                            #print('old value', dblens[field])
                            if field=='name':
                                if lens_dict['flag_discovery']:
                                    oldname = dblens['name']
                                    uploadname = lens_dict['name']
                                    if len(oldname)>=len(uploadname):
                                        if ('PS1' in oldname) or ('SL2S' in oldname):
                                            if 'PS1' in oldname:
                                                oldname = oldname.strip('PS1')
                                            else:
                                                oldname = oldname.strip('SL2S')
                                        for i, character in enumerate(oldname):
                                            if character.isdigit():
                                                break
                                        newname = 'J'+oldname[i:]
                                    else:
                                        if ('PS1' in uploadname) or ('SL2S' in uploadname):
                                            if 'PS1' in oldname:
                                                uploadname = uploadname.strip('PS1')
                                            else:
                                                uploadname = uploadname.strip('SL2S')
                                        for i, character in enumerate(uploadname):
                                            if character.isdigit():
                                                break
                                        newname = 'J'+uploadname[i:]
                                    #print(oldname, newname, dblens)
                                    if dblens['alt_name']:
                                        altname = dblens['alt_name']+', '+oldname+', '+uploadname
                                    else:
                                        altname = oldname+', '+uploadname
                                    if lens_dict['altname']!='':
                                        altname += ','+lens_dict['altname']
                                    altname = ', '.join(list(np.unique(altname.split(', '))))
                                    update_data['name'] = newname
                                    update_data['alt_name'] = altname
                            elif field=='info':
                                update_data[field] = dblens['info'] + ' / ' +lens_dict['info']
                            elif field in ['flag']:
                                if dblens['flag'] in ['CONFIRMED', 'CONTAMINANT']:
                                    update_data[field] = dblens[field]
                                else:
                                    update_data[field] = lens_dict[field]
                            elif field in ['image_conf', 'lens_type', 'source_type']:
                                update_data[field] = ','.join(list(np.unique([x.strip() for x in lens_dict[field].split(',')] + dblens[field])))
                            else:
                                update_data[field] = lens_dict[field]
                                

            if send_update:
                allupdates.append(update_data)
        else:
            if lens_dict['flag_confirmed']:
                lens_dict['score'] = None
            lens_dicts.append(lens_dict)

    form_data = lens_dicts
    if len(form_data)==0:
        continue

    # Sending the request
    print(form_data)
    for key, value in your_dict.items():
        if key not in ['nugshot']:
            print value
    r  = c.post('/api/upload-lenses/', data=form_data, content_type="application/json")

    # Printing the response of the request
    if r.status_code==200:
        print("Upload completed successfully!")
    else:
        print(r.content)
        if 'text' in r:
            if 'duplicates' in r.text:
                print("Something went wrong!")
                wait = input()
                print('d///f')
        else:
                print("Something went wrong!")


    if len(allupdates)>0:
        r  = c.post('/api/update-lens/', data=allupdates, content_type="application/json")
        if r.status_code==200:
            print("Upload completed successfully!")
        else:
            print(r.content)
            df
