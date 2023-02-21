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

Nstart = int(sys.argv[2])
Nend = int(sys.argv[3])

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

    for ii in range(len(lenses)):
        if (ii<Nstart) or (ii>Nend):
            continue
        lens = lenses[ii]
        print(ii, '/',len(lenses), ':', lens.name)
        
        name, ra, dec = lens.name, float(lens.ra), float(lens.dec)
    
        filtered_results = hst_utils.best_hst(ra, dec, datemin='1988-01-01T00:00:00.000', datemax='2023-02-14T00:00:00.000', one_instrument=instrument)
        if filtered_results:
            for j in range(len(filtered_results)):
                instr, filt = filtered_results['instrument_name'][j], filtered_results['energy_bandpassName'][j]
                filename = name+'_'+survey+'_'+instrument+'_'+filt
                if not os.path.exists(filename+'.json'):
                    image, pixscale, url = hst_utils.download_cutouts_HLA(observation=filtered_results[[j]], savedir=imagepath, savename=filename+'.jpg', ra=ra, dec=dec, size=10)
                    print(name, instr, filt)
                    if image:
                        uploadjson = hst_utils.construct_json(observation=filtered_results[[j]], pixscale=pixscale, imagename=imagepath+filename+'.jpg', ra=ra, dec=dec, url=url)
                        outfile = open(jsonpath+filename+'.json', 'w')
                        json.dump(uploadjson, outfile)
                        outfile.close()
