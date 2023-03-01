import json                    
import requests
from requests.auth import HTTPBasicAuth
import numpy as np
import cv2
import base64
import os
import sys
import django
import socket
import random
from operator import itemgetter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from lenses.models import Users, Lenses, Imaging, Spectrum



### This script should be ran on django01.


# Query the database for users
users = Users.objects.exclude(username__in=['AnonymousUser','admin']).filter(is_active=True)
print(users)

admin = Users.objects.get(username='admin')
admin_qset = Users.getAdmin()


Lenses.objects.all().update(owner=admin,access_level='PUB')
Imaging.objects.all().update(owner=admin,access_level='PUB')
Spectrum.objects.all().update(owner=admin)

justification = "Giving ownership of some objects to play with."
justification_pri = "Some private objects to play with."


for user in users:
    u = Users.objects.filter(username=user.username)
    
    # Assign lenses to user
    # --------------------------------------------
    N_lenses = random.randint(10,30)
    N_pri_lenses = random.randint(0,10)

    if N_lenses > 0:
        lenses = list(Lenses.objects.filter(owner=admin).order_by('?')[:N_lenses])

        pri_lenses = lenses[:N_pri_lenses]
        pub_lenses = lenses[N_pri_lenses:]
        
        qset = list( Lenses.objects.filter(pk__in=[lens.id for lens in pub_lenses]) )
        admin.cedeOwnership(qset,u,justification)
        
        if N_pri_lenses > 0:
            qset = Lenses.objects.filter(pk__in=[lens.id for lens in pri_lenses])
            admin.makePrivate(qset,justification_pri)
            admin.cedeOwnership(list(qset),u,justification)

    

    # Repeat the same procedure for a few Imagings
    # --------------------------------------------
    N_imaging = random.randint(0,10)
    N_pri_imaging = random.randint(0,N_imaging)

    if N_imaging > 0:
        imagings = list(Imaging.objects.filter(exists=True).filter(owner=admin).order_by('?')[:N_imaging])
        
        pri_imagings = imagings[:N_pri_imaging]
        pub_imagings = imagings[N_pri_imaging:]
        
        qset = list( Imaging.objects.filter(pk__in=[imaging.id for imaging in pub_imagings]) )
        admin.cedeOwnership(qset,u,justification)

        if N_pri_imaging > 0:
            qset = Imaging.objects.filter(pk__in=[imaging.id for imaging in pri_imagings])
            admin.makePrivate(qset,justification_pri)
            admin.cedeOwnership(list(qset),u,justification)


    
    # Repeat the same procedure for a few Spectra
    # --------------------------------------------
    N_spectra = random.randint(0,5)

    # Select N_lenses random spectra
    if N_spectra > 0:
        spectra = Spectrum.objects.filter(exists=True).filter(owner=admin).order_by('?')[:N_spectra]
        qset = list( Spectrum.objects.filter(pk__in=[spectrum.id for spectrum in spectra]) )
        admin.cedeOwnership(qset,u,justification)




    print(" User %s got: %d Lenses (%d private), %d Imaging data (%d private), %d Spectra" % (user,N_lenses,N_pri_lenses,N_imaging,N_pri_imaging,N_spectra) )
