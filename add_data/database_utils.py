import os
import datetime
import numpy as np 

import requests
from requests.auth import HTTPBasicAuth

import sys
sys.path.append('../../SLED_api')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()

from django.conf import settings
from lenses.models import Catalogue, Imaging, Spectrum, Instrument, Band, Users, Lenses, AdminCollection, Redshift
from api.serializers import ImagingDataUploadSerializer
from django.db.models import Q, F, Func, FloatField, CheckConstraint
from django.utils.timezone import make_aware
from django.core.files import File
from actstream import action


def match_to_lens(ra, dec, radius=5.):
    qset = Lenses.objects.all().annotate(distance=Func(F('ra'),F('dec'),ra,dec,function='distance_on_sky',output_field=FloatField())).filter(distance__lt=radius)
    if qset.count() > 0:
        return qset
    else:
        return False


'''
def upload_data_to_db_API(datalist, datatype, username, password):
    """
    datalist: list of json files containing the neccessary metadata for the Imaging table
    this function goes through the API, and requires confirmation
    datatype: one of 'Imaging', 'Spectrum', 'Catalogue'
    username, password: strings
    """
    url = "http://127.0.0.1:8000/api/upload-data/"

    form_data = [
       ('N', ('',str(len(datalist)))),
       ('type', ('',datatype))
    ]
    for datum in datalist:
       dum = []
       for key in datum.keys():
          if key != 'image':
            if datum[key]==None:
                dum.append( (key,('','')) )
            else:
                dum.append( (key,('',str(datum[key]))) )
          else:
             dum.append( ('image',open(datum[key],'rb')) )
       form_data.extend(dum)

    r = requests.post(url,files=form_data,auth=HTTPBasicAuth(username, password))

    if r.ok:
        print("Upload completed successfully!")
    else:
        print("Something went wrong!")
    #print(r.text)
    return 0
'''


def upload_imaging_to_db_direct(datalist, username):
    """
    datalist: list of json files containing the neccessary metadata for the Imaging table
    this function creates objects directly in the database; to be used by automatic uploads
    """
    imaging_list = []
    for data in datalist:
        finaldata = data.copy()

        finaldata['instrument'] = Instrument.objects.get(name=data['instrument'])

        #if data['band'] not in list(Band.objects.all().values_list('name', flat=True).distinct()):
        #    create_band(data['band'])

        finaldata['band'] = Band.objects.get(name=data['band'])

        #indices,neis = Lenses.proximate.get_DB_neighbours_anywhere_many([data['ra']], [data['dec']])
        lens = match_to_lens(data['ra'], data['dec'])
        if not lens:
            print('No lens found for the following data upload')
            print(data)
            continue
        finaldata['lens'] = lens[0]
        finaldata.pop('ra')
        finaldata.pop('dec')

        imaging = Imaging(**finaldata)
        print(lens,imaging)
        imaging.owner_id = Users.objects.get(username=username).id


        #check if the data exists and therefore should have an image
        if data['exists']:
            if '/' in data['image']:
                savename = data['image'].split('/')[-1]
            else:
                savename = data['image']
            f = open(data['image'],mode="rb")
            myfile = File(f)
            imaging.image.save(savename,myfile,save=False)
        if 'date_taken' in finaldata.keys():
            print(finaldata['date_taken'])
            imaging.date_taken = make_aware( datetime.datetime.strptime(finaldata['date_taken'],'%Y-%m-%d %H:%M:%S.%f').replace(hour=0,minute=0,second=0,microsecond=0) )
        imaging.save()

        imaging_list.append(imaging)
        if len(imaging_list) == 1000:
            ad_col = AdminCollection.objects.create(item_type="Imaging",myitems=imaging_list)
            action.send(Users.objects.get(username='admin'),target=Users.getAdmin().first(),verb='AddHome',level='success',action_object=ad_col)
            imaging_list.clear()
            
    return None

def upload_spectrum_to_db_direct(datalist, username):

    spectrum_list = []

    for i, data in enumerate(datalist):
        #print(i, len(datalist), 'uploading')
        if i in np.arange(0, 100000, 100):
            print(i, len(datalist))
        finaldata = data.copy()

        finaldata['instrument'] = Instrument.objects.get(name=data['instrument'])
        lens = match_to_lens(float(data['ra']), float(data['dec']))
        if not lens:
            print('No lens found for the following data upload')
            print(data)
            continue

        if len(lens)>1:
            print('too many lens matches found for ', lens)
            print(data)
            continue

        finaldata['lens'] = lens[0]
        finaldata.pop('ra')
        finaldata.pop('dec')


        spectrum = Spectrum(**finaldata)
        spectrum.owner_id = Users.objects.get(username=username).id
        if data['exists']:
            if '/' in data['image']:
                savename = data['image'].split('/')[-1]
            else:
                savename = data['image']
            f = open(data['image'],mode="rb")
            myfile = File(f)
            spectrum.image.save(savename,myfile,save=False)
        if 'date_taken' in finaldata.keys():
            spectrum.date_taken = make_aware( datetime.datetime.strptime(finaldata['date_taken'],'%Y-%m-%d %H:%M:%S.%f').replace(hour=0,minute=0,second=0,microsecond=0) )
        else:
            #we apparently made the date taken a NOT_NULL field
            spectrum.date_taken = make_aware(datetime.datetime.strptime('1858-11-17','%Y-%m-%d'))
        spectrum.save()

        spectrum_list.append(spectrum)
        if len(spectrum_list) == 1000:
            ad_col = AdminCollection.objects.create(item_type="Spectrum",myitems=spectrum_list)
            action.send(Users.objects.get(username='admin'),target=Users.getAdmin().first(),verb='AddHome',level='success',action_object=ad_col)
            spectrum_list.clear()

    return 0


'''def create_band(bandname):

    #WFC3 bands
    bands = ['F098M', 'G102', 'F105W', 'F110W', 'F125W', 'F126N', 'F127M', 'F128N', 'F130N', 'F132N', 'F139M', 'F140W', 'G141', 'F153M', 'F160W', 'F218W', 'FQ232N', 'F225W', 'FQ243N', 'F275W', 'F280N', 'F300X', 'F336W', 'F343N', 'F373N', 'FQ378N', 'FQ387N', 'F390M', 'F395N', 'F390W', 'F410M', 'FQ422M', 'F438W', 'FQ436N', 'FQ437N', 'F467M', 'F469N', 'G280', 'F475W', 'F487N', 'FQ492N', 'F502N', 'F475X', 'FQ508N', 'F555W', 'F547M', 'FQ575N', 'F606W', 'F200LP', 'FQ619N', 'F621M', 'F625W', 'F631N', 'FQ634N', 'F645N', 'F350LP', 'F656N', 'F657N', 'F658N', 'F665N', 'FQ672N', 'FQ674N', 'F673N', 'F680N', 'F689M', 'FQ727N', 'FQ750N', 'F763M', 'F600LP', 'F775W', 'F814W', 'F845M', 'FQ889N', 'FQ906N', 'F850LP', 'FQ924N', 'FQ937N', 'F953N']
    wavelengths = [9862.72, 9989.86, 10550.25, 11534.46, 12486.07, 12585.43, 12741.07, 12836.65, 13010.38, 13193.46, 13841.81, 13923.21, 13886.72, 15332.75, 15370.34, 2225.17, 2327.04, 2371.15, 2420.51, 2709.29, 2796.88, 2819.96, 3354.43, 3435.16, 3730.09, 3792.39, 3873.56, 3897.22, 3955.17, 3923.67, 4108.81, 4219.19, 4326.24, 4367.35, 4371.27, 4682.2, 4688.21, 3749.25, 4773.1, 4871.43, 4933.48, 5009.81, 4940.7, 5091.13, 5308.42, 5447.5, 5756.91, 5889.16, 4972.03, 6198.39, 6218.87, 6242.56, 6304.19, 6349.26, 6453.41, 5873.9, 6561.53, 6566.61, 6585.63, 6655.89, 6717.12, 6730.58, 6765.99, 6877.61, 6876.76, 7275.75, 7502.44, 7614.39, 7468.12, 7651.37, 8039.03, 8439.08, 8892.27, 9057.9, 9176.14, 9247.72, 9372.66, 9530.87]
    
    #ACS bands
    bands += ['FR388N', 'FR423N', 'F435W', 'FR459M', 'FR462N', 'F475W', 'F502N', 'FR505N', 'F555W', 'FR551N', 'F550M', 'FR601N', 'F606W', 'F625W', 'FR647M', 'FR656N', 'F658N', 'F660N', 'FR716N', 'POL_UV', 'POL_V', 'G800L', 'F775W', 'FR782N', 'F814W', 'FR853N', 'F892N', 'FR914M', 'F850LP', 'FR931N', 'FR1016N', 'F220W', 'F250W', 'F330W', 'F344N', 'FR388N', 'F435W', 'FR459M', 'F475W', 'F502N', 'FR505N', 'F555W', 'F550M', 'F606W', 'F625W', 'FR656N', 'F658N', 'F660N', 'PR200L', 'POL_UV', 'POL_V', 'F775W', 'G800L', 'F814W', 'F892N', 'FR914M', 'F850LP', 'F122M', 'F115LP', 'PR110L', 'F125LP', 'PR130L', 'F140LP', 'F150LP', 'F165LP']
    wavelengths += [3881.44, 4230.12, 4329.85, 4588.26, 4619.85, 4746.94, 5023.02, 5050.02, 5361.03, 5510, 5581.4, 6010.12, 5921.88, 6311.85, 6469.58, 6559.94, 6583.95, 6599.46, 7159.61, 6634.16, 6911.09, 7471.4, 7693.47, 7818.97, 8045.53, 8528.34, 8914.98, 9067.53, 9031.48, 9305.64, 10149.49, 2254.44, 2716.13, 3362.99, 3433.9, 3880.26, 4323.09, 4592.74, 4775.73, 5023.03, 5050.05, 5355.74, 5579.69, 5887.08, 6295.19, 6559.82, 6583.91, 6599.44, 5655.72, 6231.95, 6959.12, 7665.08, 7504.96, 8100.44, 8916.4, 9105.81, 9143.95, 1267.08, 1392.59, 1416.61, 1426.2, 1427.25, 1518.84, 1605.02, 1757.29]

    kappa, gamma = np.unique(bands, True)
    bands = np.array(bands)[gamma]
    wavelengths = np.array(wavelengths)[gamma]

    k = np.where(bands==bandname)[0]
    wavelength = wavelengths[k]

    b = Band(name=bandname, info='', wavelength=wavelength)
    b.save()
    return 0'''



def upload_catalogue_to_db_direct(datalist, username):

    catalogue_list = []
    m = len(datalist)
    for i, data in enumerate(datalist):
        #print(i, m)
        finaldata = data.copy()

        finaldata['instrument'] = Instrument.objects.get(name=data['instrument'])
        finaldata['band'] = Band.objects.get(name=data['band'])
        lens = match_to_lens(float(data['ra']), float(data['dec']))

        if not lens:
            print('No lens found for the following data upload')
            print(data)
            continue

        if len(lens)>1:
            print('too many lens matches found for ', lens)
            print(data)
            continue

        if lens:
            finaldata['lens'] = lens[0]
            finaldata.pop('ra')
            finaldata.pop('dec')
            catalogue = Catalogue(**finaldata)
            catalogue.owner_id = Users.objects.get(username=username).id
            if 'date_taken' in finaldata.keys():
                catalogue.date_taken = make_aware( datetime.datetime.strptime(finaldata['date_taken'],'%Y-%m-%d %H:%M:%S.%f').replace(hour=0,minute=0,second=0,microsecond=0) )
            else:
                #we apparently made the date taken a NOT_NULL field
                catalogue.date_taken = make_aware(datetime.datetime.strptime('1858-11-17','%Y-%m-%d'))
            catalogue.save()
            
            catalogue_list.append(catalogue)
        else:
            print(data, 'no lens to match to this position')

        if len(catalogue_list) == 1000:
            ad_col = AdminCollection.objects.create(item_type="Catalogue",myitems=catalogue_list)
            action.send(Users.objects.get(username='admin'),target=Users.getAdmin().first(),verb='AddHome',level='success',action_object=ad_col)
            catalogue_list.clear()

    return 0

def upload_redshifts_to_db_direct(datalist, username):

    m = len(datalist)
    for i, data in enumerate(datalist):
        print(i, m)
        finaldata = data.copy()
        lens = match_to_lens(float(data['ra']), float(data['dec']))

        if not lens:
            print('No lens found for the following data upload')
            print(data)
            #df
            continue

        if len(lens)>1:
            print('too many lens matches found for ', lens)
            print(data)
            #df
            continue

        if lens:
            finaldata['lens'] = lens[0]
            finaldata.pop('ra')
            finaldata.pop('dec')
            redshift = Redshift(**finaldata)
            redshift.owner_id = Users.objects.get(username=username).id
            redshift.save()
