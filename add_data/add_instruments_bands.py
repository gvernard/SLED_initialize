import sys
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = "mysite.settings"
django.setup()

from lenses.models import Instrument, Band
import json                    
from django.core.exceptions import ValidationError


f = open('../../initialize_database_data/instruments.json')
instruments = json.load(f)
f.close()
for instrument in instruments:
    instr = Instrument(name=instrument["name"],extended_name=instrument["extended_name"],info=instrument["info"])
    try:
        instr.full_clean()
    except ValidationError as e:
        print(instr.name,e)
    else:
        instr.save()



f = open('../../initialize_database_data/bands.json')
bands = json.load(f)
f.close()
for band in bands:
    b = Band(name=band["name"],info=band["info"],wavelength=band['wavelength'])
    try:
        b.full_clean()
    except ValidationError as e:
        print(b.name,e)
    else:
        b.save()
