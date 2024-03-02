from django.db.backends.signals import connection_created
from django.dispatch import receiver

import math

def distance_on_sky(ra1,dec1,ra2,dec2):
    """
    Same implementation as in lenses.py and distance_on_sky.sql
    """
    dec1_rad = math.radians(dec1);
    dec2_rad = math.radians(dec2);
    Ddec = abs(dec1_rad - dec2_rad);
    Dra = abs(math.radians(ra1) - math.radians(ra2));
    a = math.pow(math.sin(Ddec/2.0),2) + math.cos(dec1_rad)*math.cos(dec2_rad)*math.pow(math.sin(Dra/2.0),2);
    d = math.degrees( 2.0*math.atan2(math.sqrt(a),math.sqrt(1.0-a)) )
    return d*3600.0


@receiver(connection_created)
def extend_sqlite(connection = None, ** kwargs):
    connection.connection.create_function("distance_on_sky",4,distance_on_sky)
