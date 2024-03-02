import os
import sys
import json
import glob
import numpy as np
import database_utils

json_dir = '../../initialize_database_data/add_redshifts_csvs/'

#image_files = []
jsons = np.sort(glob.glob(json_dir+'*.json'))

uploads = []
badjsons = []
for i, jsonfile in enumerate(jsons):
    f = open(jsonfile)
    uploadjson = json.load(f)
    f.close()
    #print(jsonfile, len(uploadjson[0]['redshifts']))
    for zdict in uploadjson[0]['redshifts']:
        if zdict['tag']=='SPECTROSCOPIC':
            zdict['tag'] = 'SPECTRO'

        for key in zdict.keys():
            if zdict[key]=='':
                zdict[key]=None
        if zdict['method']==None:
            print(zdict, jsonfile)
            badjsons.append(jsonfile)
        zdict['access_level'] = 'PUB'
        uploads.append(zdict)

uploads = [dict(t) for t in {tuple(sorted(d.items())) for d in uploads}]

upload = database_utils.upload_redshifts_to_db_direct(datalist=uploads, username='admin')
