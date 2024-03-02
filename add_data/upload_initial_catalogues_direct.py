import os
import json
import glob
from astropy.table import Table
import django
from django.conf import settings
from django.db.models import Q, F, Func, FloatField, CheckConstraint
import sys

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

server_dir = sys.argv[1]
sys.path.append(server_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from lenses.models import Catalogue, Instrument, Band, Users, Lenses
from api.serializers import ImagingDataUploadSerializer

import panstarrs_utils
import legacysurvey_utils
import imaging_utils
import database_utils
import gaia_utils 

import time
import numpy as np

outpath='../../initialize_database_data/images_to_upload/jsons/'

verbose = False

username, password = 'admin', '123'

#data = Table.read('../trial_sample/lensed_quasars_uploadtable.fits')]
lenses = Lenses.objects.all()

surveys = ['PanSTARRS', 'Gaia-DR1', 'Gaia-DR2']
bandss = ['grizY', 'G', ['G', 'BP', 'RP']]
instruments = ['Pan-STARRS1', 'Gaia-DR1', 'Gaia-DR2']

#df
#for kk in range(len(surveys)):
kk = 0
survey, bands, instrument = surveys[kk], bandss[kk], instruments[kk]
files = glob.glob(outpath+'*_'+survey+'*_photometry*')
files = list(np.sort(files))
'''for i, file in enumerate(files):
    if (i>1000) or (i<0):
        continue
    print(i)
    if ' ' in file:
        os.system('rm '+file.replace(' ', '*'))
    else:
        os.system('rm '+file)
df'''

#upload in batches of 1000
uploads = []
for i, file in enumerate(files):
    #print(i, len(files))
    f = open(file)
    uploadjson = json.load(f)
    f.close()
    uploads.append(uploadjson)
    if i in np.arange(1000, len(files)+5000, 1000):
        print(i, 'have been uploaded of', len(files))
        upload = database_utils.upload_catalogue_to_db_direct(datalist=uploads, username=username)
        uploads = []
#for the final list
upload = database_utils.upload_catalogue_to_db_direct(datalist=uploads, username=username)

#Catalogue.objects.bulk_create(all_uploads)