import sys
import os
from lenses.models import Users, SledQuery, Instrument

admin = Users.objects.get(username='admin')

names, descriptions, query_details = [], [], []

#LENSED QUASARS
name = 'Lensed quasars'
description = 'All confirmed lenses with quasar sources'
query_detail = {'lens-source_type':'QUASAR', 'lens-flag_confirmed':True}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)

#QUADS
name = 'Quadruply-imaged lensed quasars'
description = 'All confirmed lensed quasars with four or more images'
query_detail = {'lens-source_type':'QUASAR', 'lens-flag_confirmed':True, 'lens-n_img_min':4}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)


#DOUBLES
name = 'Doubly-imaged lensed quasars'
description = 'All confirmed lensed quasars with 2 images'
query_detail = {'lens-source_type':'QUASAR', 'lens-flag_confirmed':True, 'lens-lens-n_img_min':2, 'lens-n_img_max':2}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)

#TRIPLES
name = 'Triply-imaged lensed quasars'
description = 'All confirmed lensed quasars with 3 images'
query_detail = {'lens-source_type':'QUASAR', 'lens-flag_confirmed':True, 'lens-n_img_min':3, 'lens-n_img_max':3}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)



#z>4 lensed quasars
name = 'z>4 lensed quasars'
description = 'All confirmed lensed quasars with source redshifts above z=4'
query_detail = {'lens-source_type':'QUASAR', 'lens-flag_confirmed':True, 'lens-z_source_min':4}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)



#LENSED GALAXIES
name = 'Lensed galaxies'
description = 'All confirmed lenses with galaxy sources'
query_detail = {'lens-source_type':'GALAXY', 'lens-flag_confirmed':True}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)


#LENSED SUPERNOVAE
name = 'Lensed supernovae'
description = 'All confirmed lenses with supernovae sources'
query_detail = {'lens-source_type':'SN', 'lens-flag_confirmed':True}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)


#CONFIRMED LENSES WITH HST IMAGING
name = 'Lenses with HST imaging'
description = 'All confirmed lenses with ACS or WFC3 imaging'
query_detail = {'lens-flag_confirmed':True, 'imaging-instrument':[str(Instrument.objects.get(name='ACS').pk), str(Instrument.objects.get(name='WFC3').pk)]}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)


#CANDIDATE LENSES WITH HST IMAGING
name = 'Candidate lenses with HST imaging'
description = 'All candidate lenses with ACS or WFC3 imaging'
query_detail = {'lens-flag_unconfirmed':True, 'lens-flag_uncontaminant':True, 'imaging-instrument':[str(Instrument.objects.get(name='ACS').pk), str(Instrument.objects.get(name='WFC3').pk)]}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)


#Confirmed lenses with spectroscopy and Pan-STARRS imaging
name = 'Confirmed lenses with spectroscopy and Pan-STARRS imaging'
description = 'All confirmed lenses with both a spectrum in the database and Pan-STARRS imaging'
query_detail = {'lens-flag_confirmed':True, 'spectrum-instrument':[str(pk) for pk in list(Instrument.objects.filter(base_types__contains='Spectrum').values_list('pk', flat=True))],
                'imaging-instrument':[str(Instrument.objects.get(name='Pan-STARRS1').pk)]}
names.append(name)
descriptions.append(description)
query_details.append(query_detail)




for i in range(len(names)):
    name, description, query_detail = names[i], descriptions[i], query_details[i]    
    q = SledQuery(owner=admin, name=name, description=description, access_level='PUB')
    cargo = q.compress_to_cargo(query_detail)

    q.cargo = cargo
    q.save()
