import os
import json
from astropy.table import Table
import sys
import django
from django.conf import settings
from django.db.models import Q, F, Func, FloatField, CheckConstraint
import glob
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

server_dir = sys.argv[1]
#server_dir = '../../SLED_api/'
sys.path.append(server_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from lenses.models import Imaging, Spectrum, Instrument, Band, Users, Lenses
from api.serializers import ImagingDataUploadSerializer

import panstarrs_utils
import legacysurvey_utils
import imaging_utils
import database_utils
import hst_utils


outpath='../../initialize_database_data/images_to_upload/'
jsonpath = outpath+'jsons/'
imagepath = outpath+'images/'
verbose = True

upload_again = True
attempt_download = True
direct_upload = True
username, password = 'admin', '123'

lenses = Lenses.objects.all()

surveys = ['HST', 'HST']
instruments = ['ACS', 'WFC3']

check_all = False

for kk in range(len(instruments)):
    uploads = []
    survey, instrument = surveys[kk], instruments[kk]
    uploads = []

    jsons = glob.glob(jsonpath+'*'+survey+'_'+instrument+'_*.json')
    allbands = []
    print(len(jsons), 'images to be uploaded for', instrument, survey)
    for js in jsons:
        f = open(js)
        uploadjson = json.load(f)
        f.close()
    
        allbands.append(uploadjson['band'])
        if uploadjson['exposure_time']<=0.0:
            print('no exposure time')
            continue
        uploads.append(uploadjson)
        if uploadjson['band']=='clear':
            print(js)

    print('Uploading to database for', survey, instrument)
    upload = database_utils.upload_imaging_to_db_direct(datalist=uploads, username=username)
