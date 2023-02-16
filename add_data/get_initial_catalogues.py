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



outpath='../../initialize_database_data/images_to_upload/jsons/'

verbose = False

upload_again = True
attempt_download = True
direct_upload = True
username, password = 'admin', '123'

#data = Table.read('../trial_sample/lensed_quasars_uploadtable.fits')]
lenses = Lenses.objects.all()

surveys = ['PanSTARRS', 'Gaia-DR1', 'Gaia-DR2']
bandss = ['grizY', 'G', ['G', 'BP', 'RP']]
instruments = ['Pan-STARRS1', 'Gaia-DR1', 'Gaia-DR2']



for kk in range(len(surveys)):
    survey, bands, instrument = surveys[kk], bandss[kk], instruments[kk]
    
    for i in range(len(lenses)):

        lens = lenses[i]
        name, ra, dec = lens.name, float(lens.ra), float(lens.dec)
        for band in bands:
            jsonfile = outpath+name+'_'+survey+'_'+band+'_photometry1.json'
            if upload_again & os.path.exists(jsonfile):
                if verbose:
                    print('A json file and the associated photometry already exist for', jsonfile,  ', uploading to database')

                files = glob.glob(outpath+name+'_'+survey+'_'+band+'_photometry*')
                if verbose:
                    print(len(files), ' separate files were found')
                for file in files:
                    f = open(file)
                    uploadjson = json.load(f)
                    f.close()

            if (not os.path.exists(jsonfile)) & attempt_download:
                if verbose:
                    print('checking for ', survey,' data in', band)
                #download the PanSTARRS data
                if survey=='PanSTARRS':
                    datafile = panstarrs_utils.query_vizier_panstarrs(ra, dec, radius=5.)
                if survey=='Gaia-DR1':
                    datafile = gaia_utils.query_vizier_gaiadr1(ra, dec, radius=5.)
                    #print(survey, datafile)
                if survey=='Gaia-DR2':
                    datafile = gaia_utils.query_vizier_gaiadr2(ra, dec, radius=5.)
                    #print(survey, datafile)

                #if the data exists, create the json and image for upload
                if datafile is not None:
                    for k, phot in enumerate(datafile):
                        print(name, ra, dec, k)
                        jsonname = outpath+name+'_'+survey+'_'+band+'_photometry'+str(k+1)+'.json'
                        if survey=='PanSTARRS':
                            uploadjson = panstarrs_utils.return_photometry_json(json_outname=jsonname, ra=ra, dec=dec, band=band, phot=phot)
                        if survey in ['Gaia-DR1', 'Gaia-DR2']:
                            print(survey)
                            uploadjson = gaia_utils.return_photometry_json(json_outname=jsonname, ra=ra, dec=dec, band=band, phot=phot, instrument=instrument)


                #if the data does not exist, then upload an exists=False json so we know not to try again (DIRECT ONLY)
                if (datafile is None) & direct_upload:
                    if survey=='PanSTARRS':
                        uploadjson = panstarrs_utils.return_empty_photometry_json(json_outname=jsonfile, ra=ra, dec=dec, band=band)
                    if survey=='Gaia-DR1':
                        uploadjson = gaia_utils.return_empty_photometry_json(json_outname=jsonfile, ra=ra, dec=dec, band=band, instrument='Gaia-DR1')
                    if survey=='Gaia-DR2':
                        uploadjson = gaia_utils.return_empty_photometry_json(json_outname=jsonfile, ra=ra, dec=dec, band=band, instrument='Gaia-DR2')
