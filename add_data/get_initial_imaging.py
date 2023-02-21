import os
import json
from astropy.table import Table
import sys
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

import panstarrs_utils
import legacysurvey_utils
import imaging_utils
import database_utils

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
    #for i in range(0, 50):
    for kk, lens in enumerate(lenses): 
        if (kk<Nstart) or (kk>Nend):
            continue
        print(kk, '/',len(lenses), ':', lens.name)
        uploads = []
        name, ra, dec = lens.name, float(lens.ra), float(lens.dec)
        for band in bands:
            jsonfile = jsonpath+name+'_'+survey+'_'+band+'.json'

            if (not os.path.exists(jsonfile)) & attempt_download:
                if verbose:
                    print('checking for ', survey,' data in', band)
                #download the PanSTARRS data
                if survey=='PanSTARRS':
                    datafile = panstarrs_utils.panstarrs_data(name, ra, dec, band, outpath=jsonpath, size=10, verbose=verbose)
                elif survey=='LegacySurveySouth':
                    datafile = legacysurvey_utils.legacysurvey_data(name, ra, dec, band, layer='ls-dr9-south', outpath=jsonpath, size=10, verbose=verbose)
                elif survey=='LegacySurveyNorth':
                    datafile = legacysurvey_utils.legacysurvey_data(name, ra, dec, band, layer='ls-dr9-north', outpath=jsonpath, size=10, verbose=verbose)
                
                if datafile==0:
                    continue
                    
                #if the data exists, create the json and image for upload
                if datafile is not None:
                    if survey=='PanSTARRS':
                        jsonfile = panstarrs_utils.panstarrs_band_image_and_json(name=name, ra=ra, dec=dec, band=band, jsonpath=jsonpath, imagepath=imagepath)
                    elif survey=='LegacySurveySouth':
                        jsonfile = legacysurvey_utils.legacy_survey_layer_band_image_and_json(name, ra, dec, band, layer='ls-dr9-south', jsonpath=jsonpath, imagepath=imagepath, size=10)
                    elif survey=='LegacySurveyNorth':
                        jsonfile = legacysurvey_utils.legacy_survey_layer_band_image_and_json(name, ra, dec, band, layer='ls-dr9-north', jsonpath=jsonpath, imagepath=imagepath, size=10)
                    

                    #f = open(jsonfile)
                    #uploadjson = json.load(f)
                    #f.close()

                else:
                    uploadjson = imaging_utils.checked_and_nodata_json(jsonfile, name, ra, dec, band, instrument=instrument)