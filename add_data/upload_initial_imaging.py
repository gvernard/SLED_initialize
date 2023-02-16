import os
import json
from astropy.table import Table
import sys
import glob
import django
from django.conf import settings
from django.db.models import Q, F, Func, FloatField, CheckConstraint

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

server_dir = sys.argv[1]
sys.path.append(server_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from lenses.models import Imaging, Spectrum, Instrument, Band, Users, Lenses
from api.serializers import ImagingDataUploadSerializer

#import panstarrs_utils
#import legacysurvey_utils
#import imaging_utils
import database_utils



outpath='../../initialize_database_data/images_to_upload/'
jsonpath = outpath+'jsons/'
imagepath = outpath+'images/'
verbose = True

upload_again = True
attempt_download = True
direct_upload = True
username, password = 'admin', '123'

#data = Table.read('../trial_sample/lensed_quasars_uploadtable.fits')]
lenses = Lenses.objects.all()

surveys = ['PanSTARRS', 'LegacySurveySouth', 'LegacySurveyNorth']
bandss = ['grizY', 'grz', 'grz']
instruments = ['Pan-STARRS1', 'Legacy Survey (South)', 'Legacy Survey (North)']

#surveys = ['LegacySurveySouth', 'LegacySurveyNorth']
#bandss = ['grz', 'grz']
#instruments = ['Legacy Survey (South)', 'Legacy Survey (North)']



for kk in range(len(surveys)):
    survey, bands, instrument = surveys[kk], bandss[kk], instruments[kk]
    uploads = []
    jsonfiles = list(set(glob.glob(jsonpath+'*_'+survey+'_*.json')) - set(glob.glob(jsonpath+'*_'+survey+'_*hotom*.json')))
    for jsonfile in jsonfiles:
        f = open(jsonfile)
        uploadjson = json.load(f)
        f.close()

        if uploadjson['exists']:
            uploadjson['image'] = imagepath + os.path.basename(uploadjson['image'])


        uploads.append(uploadjson)

    print('Uploading to database')
    upload = database_utils.upload_imaging_to_db_direct(datalist=uploads, username=username)
    #else:
    #    upload = database_utils.upload_data_to_db_API(datalist=uploads, datatype='Imaging', username=username, password=password)
