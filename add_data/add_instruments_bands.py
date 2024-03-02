import sys
import os
import django
import numpy as np

os.environ['DJANGO_SETTINGS_MODULE'] = "mysite.settings"
django.setup()

from lenses.models import Instrument, Band
import json                    
from django.core.exceptions import ValidationError


f = open('instruments.json')
instruments = json.load(f)
f.close()
for instrument in instruments:
    instr = Instrument(name=instrument["name"],extended_name=instrument["extended_name"],info=instrument["info"], base_types=instrument["base_types"])
    try:
        instr.full_clean()
    except ValidationError as e:
        print(instr.name,e)
    else:
        instr.save()

f = open('bands.json')
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

#ADD HST bands
#WFC3 bands
bands = ['F098M', 'G102', 'F105W', 'F110W', 'F125W', 'F126N', 'F127M', 'F128N', 'F130N', 'F132N', 'F139M', 'F140W', 'G141', 'F153M', 'F160W', 'F218W', 'FQ232N', 'F225W', 'FQ243N', 'F275W', 'F280N', 'F300X', 'F336W', 'F343N', 'F373N', 'FQ378N', 'FQ387N', 'F390M', 'F395N', 'F390W', 'F410M', 'FQ422M', 'F438W', 'FQ436N', 'FQ437N', 'F467M', 'F469N', 'G280', 'F475W', 'F487N', 'FQ492N', 'F502N', 'F475X', 'FQ508N', 'F555W', 'F547M', 'FQ575N', 'F606W', 'F200LP', 'FQ619N', 'F621M', 'F625W', 'F631N', 'FQ634N', 'F645N', 'F350LP', 'F656N', 'F657N', 'F658N', 'F665N', 'FQ672N', 'FQ674N', 'F673N', 'F680N', 'F689M', 'FQ727N', 'FQ750N', 'F763M', 'F600LP', 'F775W', 'F814W', 'F845M', 'FQ889N', 'FQ906N', 'F850LP', 'FQ924N', 'FQ937N', 'F953N', 'F164N', 'F167N']
wavelengths = [9862.72, 9989.86, 10550.25, 11534.46, 12486.07, 12585.43, 12741.07, 12836.65, 13010.38, 13193.46, 13841.81, 13923.21, 13886.72, 15332.75, 15370.34, 2225.17, 2327.04, 2371.15, 2420.51, 2709.29, 2796.88, 2819.96, 3354.43, 3435.16, 3730.09, 3792.39, 3873.56, 3897.22, 3955.17, 3923.67, 4108.81, 4219.19, 4326.24, 4367.35, 4371.27, 4682.2, 4688.21, 3749.25, 4773.1, 4871.43, 4933.48, 5009.81, 4940.7, 5091.13, 5308.42, 5447.5, 5756.91, 5889.16, 4972.03, 6198.39, 6218.87, 6242.56, 6304.19, 6349.26, 6453.41, 5873.9, 6561.53, 6566.61, 6585.63, 6655.89, 6717.12, 6730.58, 6765.99, 6877.61, 6876.76, 7275.75, 7502.44, 7614.39, 7468.12, 7651.37, 8039.03, 8439.08, 8892.27, 9057.9, 9176.14, 9247.72, 9372.66, 9530.87, 16449.96, 16676.0]
infos = ['WFC3' for band in bands]

#ACS bands
bands2 = ['FR388N', 'FR423N', 'F435W', 'FR459M', 'FR462N', 'F475W', 'F502N', 'FR505N', 'F555W', 'FR551N', 'F550M', 'FR601N', 'F606W', 'F625W', 'FR647M', 'FR656N', 'F658N', 'F660N', 'FR716N', 'POL_UV', 'POL_V', 'G800L', 'F775W', 'FR782N', 'F814W', 'FR853N', 'F892N', 'FR914M', 'F850LP', 'FR931N', 'FR1016N', 'F220W', 'F250W', 'F330W', 'F344N', 'FR388N', 'F435W', 'FR459M', 'F475W', 'F502N', 'FR505N', 'F555W', 'F550M', 'F606W', 'F625W', 'FR656N', 'F658N', 'F660N', 'PR200L', 'POL_UV', 'POL_V', 'F775W', 'G800L', 'F814W', 'F892N', 'FR914M', 'F850LP', 'F122M', 'F115LP', 'PR110L', 'F125LP', 'PR130L', 'F140LP', 'F150LP', 'F165LP', 'clear']
wavelengths2 = [3881.44, 4230.12, 4329.85, 4588.26, 4619.85, 4746.94, 5023.02, 5050.02, 5361.03, 5510, 5581.4, 6010.12, 5921.88, 6311.85, 6469.58, 6559.94, 6583.95, 6599.46, 7159.61, 6634.16, 6911.09, 7471.4, 7693.47, 7818.97, 8045.53, 8528.34, 8914.98, 9067.53, 9031.48, 9305.64, 10149.49, 2254.44, 2716.13, 3362.99, 3433.9, 3880.26, 4323.09, 4592.74, 4775.73, 5023.03, 5050.05, 5355.74, 5579.69, 5887.08, 6295.19, 6559.82, 6583.91, 6599.44, 5655.72, 6231.95, 6959.12, 7665.08, 7504.96, 8100.44, 8916.4, 9105.81, 9143.95, 1267.08, 1392.59, 1416.61, 1426.2, 1427.25, 1518.84, 1605.02, 1757.29, 0.0]
infos2 = ['ACS' for band in bands2]

bands += bands2
wavelengths += wavelengths2
infos += infos2

wavelengths = np.array(wavelengths)/10.

final_bands, _, _, N = np.unique(np.array(bands), True, True, True)
for i in range(len(final_bands)):
    k = np.where(np.array(bands)==final_bands[i])[0]
    bandinfo = 'HST filter for '+','.join(np.unique(np.array(infos)[k]))

    b = Band(name=final_bands[i],info=bandinfo,wavelength=wavelengths[k[0]])
    try:
        b.full_clean()
    except ValidationError as e:
        print(b.name,e)
    else:
        b.save()
