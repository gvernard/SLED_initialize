import sys
import os
import django
from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np

dirname = os.path.dirname(__file__)
sys.path.append(dirname)

#Database init
os.environ['DJANGO_SETTINGS_MODULE'] = "mysite.settings"
django.setup()

from lenses.models import Users, SledGroup, Lenses, SingleObject
from django.forms.models import model_to_dict
from guardian.shortcuts import assign_perm



# Create users
user_array = [
    {
        'username':'Cameron',
        'first_name':'Cameron',
        'last_name':'Lemon',
        'email':'cameron.lemon@epfl.ch'
    },
    {
        'username':'Giorgos',
        'first_name':'Giorgos',
        'last_name':'Vernardos',
        'email':'georgios.vernardos@epfl.ch'
    },
]
for user_details in user_array:
    user = Users.objects.create_user(user_details**, password='123',affiliation='EPFL')
    if user.username in ['Cameron','Giorgos']:
        user.is_staff = True
        user.save()
        
# Create superuser
Users.objects.create_superuser(username='admin',password=password,email='admin@example.com')

print('Populating the database with the following users:',Users.objects.all().values_list('username',flat=True))






group_array = [
    {
        'name': 'EPFL',
        'description': 'The lensing group based at EPFL.'
    },
    {
        'name': 'TDCOSMO',
        'description': 'Time delay cosmography with lensed quasars'
    }
]

group_owner = Users.objects.get(username='Cameron')
for group_details in group_array:
    sledgroup = SledGroup.objects.create(group_details**,owner=group_owner)

print('Populating the database with the following groups:',SledGroup.objects.all().values_list('name',flat=True))



# Adding users to group, need to have set the group ID
my_group = SledGroup.objects.get(name='EPFL') 
user1 = Users.objects.get(username='Cameron')
user2 = Users.objects.get(username='Giorgos')
user1.groups.add(my_group)
user2.groups.add(my_group)

my_group = SledGroup.objects.get(name='TDCOSMO') 
user1.groups.add(my_group)
user2.groups.add(my_group)

#my_group.user_set.add(user1)
#my_group.user_set.add(user2)



