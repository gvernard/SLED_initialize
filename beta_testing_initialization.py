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


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from lenses.models import Catalogue, Instrument, Band, Users, Lenses



### This script should be ran on django01.


# Query the database for users
users = Users.objects.exclude(username__in=['AnonymousUser','admin','Cameron','Giorgos'])
print(users)

