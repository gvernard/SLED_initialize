from astropy.table import Table
import os
import sys
import json
import glob
import django
from django.conf import settings
from django.db.models import Q, F, Func, FloatField, CheckConstraint
import numpy as np

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

sys.path.append('../../SLED_api/')

server_dir = sys.argv[1]
sys.path.append(server_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()


from lenses.models import Imaging, Spectrum, Instrument, Band, Users, Lenses
from api.serializers import ImagingDataUploadSerializer

#import spectrum_utils
import database_utils


#name, ra, dec = 'SDSSJ0246-0825', 41.6420, -8.4267
outpath = '../../initialize_database_data/images_to_upload/'
jsonpath = outpath+'jsons/'
imagepath = outpath+'images/'
verbose = True

upload_again = True
attempt_download = True
direct_upload = True
username, password = 'admin', '123'

survey = 'SDSS DR16'
offline = False

uploads = []
spectra = glob.glob(jsonpath+'*_SDSSDR1*.json')
m = len(spectra)
for i, jsonfile in enumerate(spectra):
    #print(i, m)
    if i in np.arange(0, 100000, 1000):
        print(i, m)
    f = open(jsonfile)
    uploadjson = json.load(f)
    f.close()
    
    if uploadjson['exists']:
        uploadjson['image'] = imagepath + os.path.basename(uploadjson['image'])
        uploadjson['lambda_min'] = uploadjson['lambda_min']/10.
        uploadjson['lambda_max'] = uploadjson['lambda_max']/10.

    uploads.append(uploadjson)

upload = database_utils.upload_spectrum_to_db_direct(datalist=uploads, username=username)
