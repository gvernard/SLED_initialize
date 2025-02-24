from astropy.table import Table
import os
import sys
import json
import glob
import django
from django.conf import settings
from django.db.models import Q, F, Func, FloatField, CheckConstraint
import fnmatch 

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

server_dir = sys.argv[1]
sys.path.append(server_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()


from lenses.models import Imaging, Spectrum, Instrument, Band, Users, Lenses
from api.serializers import ImagingDataUploadSerializer

import spectrum_utils
import database_utils

Nstart = int(sys.argv[2])
Nend = int(sys.argv[3])

#name, ra, dec = 'SDSSJ0246-0825', 41.6420, -8.4267
outpath = '../../initialize_database_data/images_to_upload/'
jsonpath = outpath+'jsons/'
imagepath = outpath+'images/'
verbose = True

username, password = 'admin', '123'

survey = 'SDSS DR16'
offline = False

#data = Table.read('../trial_sample/lensed_quasars_uploadtable.fits')
lenses = Lenses.objects.all()

allspectra = glob.glob(jsonpath+'*_SDSSDR1*.json')

#for i in range(0, 50):
for kk, lens in enumerate(lenses): 
    if (kk<Nstart) or (kk>Nend):
        continue
    print(kk, len(lenses))
    name, ra, dec = lens.name, float(lens.ra), float(lens.dec)

    spectra = fnmatch.filter(allspectra, jsonpath+name+'_SDSSDR1*.json')
    print(spectra)
    if len(spectra)>1:
        print('MAYBE A PROBLEM')
        specids = [spec.split('_')[-1][:-5] for spec in spectra]
    elif len(spectra)==1:
        specids = [spec.split('_')[-1][:-5] for spec in spectra]
        #df
        if specids == ['SDSSDR16']:
            spectra = None
    else:
        spectra = spectrum_utils.query_vizier_sdss_dr16(ra, dec, radius=5.)
        if spectra is not None:
            specids = spectra['Sp-ID']
    has_valid_spectrum = False

    if spectra is not None:
        for specnum, spec in enumerate(spectra):
            jsonfile = jsonpath+name+'_SDSSDR16_'+specids[specnum]+'.json'
            if os.path.exists(jsonfile):
                has_valid_spectrum = True
            else:
                #check flag to see if spectrum was unplugged
                flag = spec['f_zsp']
                if "{:08d}".format(int(format(flag, 'b')))[-8]=='1':
                    if verbose:
                        print('There was a spectrum but the fiber was unplugged')
                    continue

                spid = spec['Sp-ID']
                title_string = spec['spCl']+'-'+spec['subCl']+'; z='+'{0:.3f}'.format(spec['zsp'])
                fits_outname = name+'_SDSSDR16_'+spid+'.fits'
                jpg_outname = name+'_SDSSDR16_'+spid+'.jpg'
                spectrum_utils.download_spectrum(spid, fits_outname=jsonpath+fits_outname)
                spectrum_utils.make_cutout(fits_outname=jsonpath+fits_outname, jpg_outname=imagepath+jpg_outname, title_string=title_string)
                upload_json = spectrum_utils.get_upload_json(ra='{0:.4f}'.format(ra), dec='{0:.4f}'.format(dec), jpg_outname=imagepath+jpg_outname, json_outname=jsonfile, fits_outname=jsonpath+fits_outname, spec_table=spec)
                has_valid_spectrum = True



    if not has_valid_spectrum:
        jsonfile = jsonpath+name+'_SDSSDR16.json'
        if not os.path.exists(jsonfile):
            if verbose:
                print('No SDSS spectrum found for', name)
                print('Creating JSON to store as a negative result')        
            upload_json = spectrum_utils.checked_and_nodata_json(json_outname=jsonfile, ra=ra, dec=dec, instrument='SDSS-spec')
