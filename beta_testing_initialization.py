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
users = Users.objects.exclude(username__in=['AnonymousUser','admin'])
print(users)

admin = Users.objects.get(username='admin')

Lenses.objects.all().update(owner=admin,access_level='PUB')
Imaging.objects.all().update(owner=admin,access_level='PUB')
Spectrum.objects.all().update(owner=admin)


                 

for u in users:

    # Assign lenses to user
    # --------------------------------------------
    N_lenses = random.randint(10,30)
    N_pri_lenses = random.randint(0,10)
    lenses = list(Lenses.objects.all().order_by('?')[:N_lenses])

    pri_lenses = lenses[:N_pri_lenses]
    pub_lenses = lenses[N_pri_lenses:]
    
    qset = Lenses.objects.filter(pk__in=[lens.id for lens in pub_lenses])
    qset.update(owner=u)

    qset = Lenses.objects.filter(pk__in=[lens.id for lens in pri_lenses])
    qset.update(owner=u,access_level='PRI')

    

    # Repeat the same procedure for a few Imagings
    # --------------------------------------------
    N_imaging = random.randint(0,10)
    N_pri_imaging = random.randint(0,N_imaging)
    imagings = list(Imaging.objects.filter(exists=True).order_by('?')[:N_imaging])

    pri_imagings = imagings[:N_pri_imaging]
    pub_imagings = imagings[N_pri_imaging:]
    
    qset = Imaging.objects.filter(pk__in=[imaging.id for imaging in pub_imagings])
    qset.update(owner=u)

    qset = Imaging.objects.filter(pk__in=[imaging.id for imaging in pri_imagings])
    qset.update(owner=u,access_level='PRI')


    
    # Repeat the same procedure for a few Spectra
    # --------------------------------------------
    N_spectra = random.randint(0,5)

    # Select N_lenses random spectra
    spectra = Spectrum.objects.filter(exists=True).order_by('?')[:N_spectra]
    qset = Spectrum.objects.filter(pk__in=[spectrum.id for spectrum in spectra])
    qset.update(owner=u)



    print(" User %s got: %d Lenses (%d private), %d Imaging data (%d private), %d Spectra" % (u,N_lenses,N_pri_lenses,N_imaging,N_pri_imaging,N_spectra) )
