import os
import json
import requests
import numpy as np 

from astropy.time import Time
from astropy.table import vstack
from astroquery.cadc import Cadc
import astropy.io.fits as fits

import matplotlib.cm
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import scipy.ndimage

import rotation_utils


def clip(data, nsigma):
    '''iteratively removes data until all is within nsigma of the median, then returns the median and std'''
    lennewdata = 0
    lenolddata = data.size
    while lenolddata>lennewdata:
        lenolddata = data.size
        data = data[np.where((data<np.nanmedian(data)+nsigma*np.nanstd(data))&(data>np.nanmedian(data)-nsigma*np.nanstd(data)))]
        lennewdata = data.size
    return np.median(data), np.std(data)


def best_hst(ra, dec, datemin='1981-01-01T00:00:00.000', datemax='2022-01-01T00:00:00.000', one_instrument=None):
    """This function queries the HST and HSTHLA collections at CADC. There is often no single best exposure of a system in a particular band,
    but multiple reductions in both collections.
    param: ra (float), right ascension in degrees
    param: dec (float), declination in degrees
    param: one_instrument (str), examples include 'WFC3', 'ACS', 'NICMOS'
    param: datemin (str), earliest release date for an exposure, format='isot', UTC
    param: datemax (str), latest release date for an exposure, format='isot', UTC
    """
    cadc = Cadc()
    #images = cadc.get_images('%f %f'%(ra, dec),'10 arcsec',collection='HST', show_progress=True)
    result1 = cadc.query_region('%f %f'%(ra, dec), collection='HST')
    result2 = cadc.query_region('%f %f'%(ra, dec), collection='HSTHLA')
    result = vstack([result1, result2])


    #only keep results with release dates within specified limits
    datarelease = Time(result['dataRelease'], format='isot', scale='utc').mjd
    datemin = Time(datemin, format='isot', scale='utc').mjd
    datemax = Time(datemax, format='isot', scale='utc').mjd

    keep = np.where((datarelease>datemin)&(datarelease<datemax))[0]
    if len(keep)>0:
        result = result[keep]
    else:
        return None


    #remove stack of two filters, e.g. F555W/F814W
    filters = result['energy_bandpassName']
    result = result[np.array(['/' not in filt for filt in filters])]

    #just keep the instrument name, not the channel
    result['instrument_name'] = [instr.split('/')[0] for instr in result['instrument_name']]

    #remove any instances of no proposal PI
    result = result[result['proposal_pi']!='']

    #only keep imaging data
    result = result[result['type']!='SPECTROSCOPIC']

    #remove the PR200L filters since that appears to be spectroscopic with ACS
    result = result[result['energy_bandpassName']!='PR200L']

    #only keep science intent data
    result = result[result['intent']=='science']

    #remove any planetary camera images for WPFC2, since WF contains them anyway and the object will always be in the wf frame
    removepc = np.array([obs[-3:]!='_pc' for obs in result['observationID']])
    #isnotwfpc2 = np.array([inst!='WFPC2' for inst in result['instrument_name']])
    result = result[removepc] #*isnotwfpc2]

    #remove any detection images
    removedets = np.array([obs[-6:]!='_total' for obs in result['observationID']])
    result = result[removedets]
    
    bad_instruments = ['FOS', 'HSP', 'FOC', 'STIS', 'FGS', 'WFPC', 'COS'] #sometimes WFPC fails... not included in HLA archive
    for inst in bad_instruments:

        instruments = result['instrument_name']
        keep = []
        for instrument in instruments:
            keep.append(instrument!=inst)
        keep = np.array(keep)

        result = result[keep]


    #remove certain calibration programmes
    remove_calib_prog = np.array(['calib' not in target_name.lower() for target_name in result['target_name']])
    result = result[remove_calib_prog]

    if one_instrument:
        keep_inst = np.array([one_instrument in instrument for instrument in result['instrument_name']])
        result = result[keep_inst]


    best_each_band = []
    #loop over filters

    filts = result['energy_bandpassName']

    #remove filts with ; in them
    final_filts = []
    for i, filt in enumerate(filts):
        if ';' in filt:
            filtoptions = filt.split(';')
            for filtoption in filtoptions:
                print(filtoption)
                if filtoption[0]=='F':
                    bestfilt = filtoption
            final_filts.append(bestfilt)
        else:
            final_filts.append(filt)

    result['energy_bandpassName'] = final_filts

    for filt in np.unique(filts):

        if (filt=='detection') or (filt==''):
            continue
        kappa = np.where(filts==filt)
        observations = result[kappa]
        #instruments = result[kappa]['instrument_name']

        #for instrument in np.unique(instruments):

        #for instrument in np.unique(instruments):
        #kappa = np.where(instruments==instrument)
        ###obs_instrument = result[kappa]
        #filts = obs_instrument['energy_bandpassName']

        #now loop over filters
        #for filt in np.unique(filts):
            #if filt=='detection':
            #    continue
            #observations = obs_instrument[np.where(filts==filt)]

            #we choose the most suitable exposure
            
            #keep highest calibration level only
        calib = observations['calibrationLevel']
        observations = observations[calib==calib.max()]

        #if HSTHLA observations exist, remove the HST ones for the NICMOS instrument
        #HLA cutout server only does NICMOS HLA cutouts it seems
        instruments = np.unique(observations['instrument_name'])
        if np.sum(['NICMOS' not in instrument for instrument in instruments])==0:
            #only use the HSTHLA observations:
            observations = observations[observations['collection']=='HSTHLA']

        #if more than one exposure, choose the deepest exposure
        if len(observations)>1:
            exptimes = observations['time_exposure']

            observations = observations[exptimes==exptimes.max()]
            if len(observations)>1:

                #choose the latest release:
                t = Time(observations['dataRelease'], format='isot', scale='utc')
                observations = observations[t.mjd==np.max(t.mjd)]
                
                print('more than one option...')
                print(observations)
                observations = observations[0]


        best_each_band.append(observations)
        print(filt)
    if len(best_each_band)>0:
        filtered_results = vstack(best_each_band)
        return filtered_results #, image_urls
    else:
        return None
        #image_urls = cadc.get_image_list(filtered_results, coordinates='%f %f'%(ra, dec), radius='10 arcsec')
    


def download_cutouts_HLA(observation, savedir, savename, ra, dec, size=10):
    """This function takes in a single line of a CADC table and uses the HLA cutout server to return cutouts
    Returns None if cutout could not be made; this happens rarely and an implementation to make the cutout from 
            CADC itself (cadc.get_image_list) should be implemented

    """

    #we need to process some variable names to be consistent with the HLA cutout server parameters
    if '-' in observation['productID'][0]:
        red = ''.join(observation['productID'][0].split('-')[:-1])
    else:
        red = observation['productID'][0]

    detector = observation['instrument_name'][0]
    if detector=='NICMOS/NIC2':
        red += '_mos'
    if '_drz' in red:
        red = red[:-4]
    if ('nic_nic3' in red)|('nic_nic2' in red)|('nic_nic1' in red):
        thirdred = red.split('_')[2]
        red = red.upper()
        if len(red.split('NIC')[0].split('_'))>2:
            components = red.split('_')
            components[2] = thirdred

            red = '_'.join(components)

    #for some crazy reason HLA does not store the HLA assocation for these exposures... even though they exist at CADC
    if red.split('_')[-1]=='fr423n':
        red += '_01'

    #first get pixel scale
    url = 'https://hla.stsci.edu/cgi-bin/fitscut.cgi?red='+red+'&RA='+str(ra)+'&Dec='+str(dec)+'&size=5&format=FITS'
    r = requests.get(url)
    if 'Some image dimensions are negative for all planes' in str(r.content):
        return None, None, None

    try:
        dat = fits.open(url)
    except Exception:
        print('url could not be opened; ERROR!')
        return None, None, None

    data, header = dat[0].data, dat[0].header
    if np.isnan(np.nanmax(data)):
        return None, None, None

    CD1_1, CD1_2 = header['CD1_1'], header['CD1_2']
    CD2_1, CD2_2 = header['CD2_1'], header['CD2_2']
    cd = np.array([[CD1_1, CD1_2], [CD2_1, CD2_2]])
    pixscale = 3600*(CD1_1**2. + CD1_2**2.)**0.5

    #now get correct size cutout
    npix = int(size*2**0.5/pixscale)
    url = 'https://hla.stsci.edu/cgi-bin/fitscut.cgi?red='+red+'&RA='+str(ra)+'&Dec='+str(dec)+'&size='+str(npix)+'&format=FITS'
    dat = fits.open(url)

    data, header = dat[0].data, dat[0].header
    #print(data, header)
    rotangle = rotation_utils.image_angle_from_cd(cd)

    #fill nans before rotation:
    mask = np.isnan(data)
    data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])

    bg, sigma = clip(data, 4.)
    data = scipy.ndimage.rotate(data, rotangle, order=3)
    rotmask = scipy.ndimage.rotate(mask, rotangle, order=0)
    data[rotmask] = np.nan

    #dat = fits.open(image_url)[1].data
    finalsize = int(size/pixscale)
    crop = int((data.shape[0]-finalsize)/2)
    data = data[crop:-crop, crop:-crop]

    cmap = matplotlib.cm.get_cmap("cubehelix").copy()
    cmap.set_bad('black')

    lenspixels = data[data>bg+3*sigma]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(data, origin='lower', cmap=cmap, norm=LogNorm(vmax=np.nanpercentile(lenspixels, 99.5), vmin=bg+sigma))
    #ax.set_title(observation['instrument_name'][0]+' '+observation['energy_bandpassName'][0])
    #ypos, xpos = data.shape[1]*0.1, data.shape[0]*0.1
    #ax.hlines(ypos, xpos, xpos + 1/pixscale, color='white', lw=2)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    ax.set_xticks([])
    ax.set_yticks([])
    plt.savefig(savedir+'/'+savename, bbox_inches='tight', pad_inches=0)
    plt.close()

    return savename, pixscale, url



def construct_json(observation, pixscale, imagename, ra, dec, url):

    upload_json = {}
    upload_json['instrument'] = observation['instrument_name'][0]
    upload_json['pixel_size'] = pixscale
    upload_json['band'] = observation['energy_bandpassName'][0]
    upload_json['access_level'] = 'PUB'
    upload_json['ra'] = ra
    upload_json['dec'] = dec
    upload_json['exists'] = True

    date = Time(np.median(observation['time_bounds'][0].data), format='mjd')
    formatted_date = date.fits.replace('T', ' ')

    upload_json['exposure_time'] = observation['time_exposure'][0]
    upload_json['date_taken'] = formatted_date
    upload_json['image'] = imagename
    upload_json['future'] = False
    upload_json['info'] = ''
    upload_json['url'] = url

    return upload_json


if __name__ == '__main__':

    ras = [2.83435, 3.34808, 7.09369, 7.56378, 7.674, 11.3665, 11.94659, 12.6158, 13.4353, 15.6965, 18.1412, 18.65991, 18.98883, 19.1635, 20.84084, 21.23943, 22.80585, 23.64858, 25.0125, 25.2042, 26.3194, 26.63699, 26.79231, 27.73692, 28.0796, 29.1039, 29.6724, 30.0872, 30.9977, 32.3047, 33.56813, 34.55142, 35.27285, 36.593, 37.04624, 38.06565, 38.13829, 38.86426, 39.574, 41.35651, 41.55083, 41.64204, 41.8664, 41.8764, 41.9561, 41.9782, 42.2031, 44.16983, 44.88965, 44.92858, 47.7029, 50.4885, 51.4511, 52.428, 54.78666, 55.0351, 55.7978, 56.5579, 56.769, 57.7146, 58.804, 60.45041, 61.2721, 61.49917, 61.79258, 61.9741, 62.0905, 63.65719, 64.1783, 64.1972, 64.49682, 67.3048, 69.5619, 69.94617, 70.0482, 71.71822, 72.09163, 74.3483, 75.1017, 75.4413, 76.1616, 78.54541, 81.54666, 82.65415, 85.73921, 86.1448, 90.1242, 90.56684, 91.79499, 92.1725, 97.2299, 97.5377, 98.80131, 98.9864, 100.9259, 104.76682, 109.0151, 113.6936, 114.2861, 115.0907, 115.71333, 115.9692, 116.721, 117.9212, 120.9906, 121.59867, 123.38033, 124.6179, 124.6269, 124.99909, 125.06706, 125.4121, 125.4944, 126.53489, 127.92379, 128.071, 128.3369, 128.4767, 128.6411, 130.13842, 133.22323, 135.89609, 136.01744, 136.1714, 136.7937, 136.966, 137.43957, 137.7845, 137.86471, 137.954, 138.25425, 139.6806, 140.208, 140.2685, 140.3144, 141.1243, 141.23246, 144.2494, 144.3832, 145.34355, 145.8625, 146.52017, 147.4783, 147.84404, 148.7079, 148.75038, 150.33665, 150.36876, 150.5063, 150.7886, 151.10379, 151.14294, 152.1932, 152.2041, 153.06622, 154.3498, 155.29588, 156.14392, 156.3567, 157.30765, 158.39177, 159.3665, 160.3081, 160.59213, 160.6553, 163.67036, 163.93938, 164.9802, 166.63938, 167.7773, 169.09805, 169.57035, 172.077, 172.50041, 172.75, 172.9644, 172.9908, 173.6688, 174.3128, 174.51554, 176.7198, 177.1381, 178.82195, 178.82639, 180.3288, 181.62361, 181.7448, 182.3615, 184.19165, 186.5334, 188.3261, 188.4219, 189.2537, 189.67778, 191.9855, 192.78154, 193.27792, 193.57917, 193.6682, 193.9324, 194.58017, 195.7765, 196.18166, 196.92947, 197.5835, 198.41675, 200.65152, 201.50006, 201.741, 202.4535, 202.5305, 202.57772, 203.09425, 203.50579, 203.89496, 204.77999, 206.204, 207.37472, 208.27642, 208.9308, 209.9332, 210.05341, 210.3982, 211.3142, 211.60303, 212.1406, 212.8317, 212.902, 213.0424, 213.94267, 214.3989, 216.15871, 218.345, 220.7282, 220.836, 223.0479, 223.75782, 224.6982, 227.18253, 228.9107, 228.91601, 229.51286, 230.43679, 231.12428, 231.1901, 231.6891, 231.8338, 232.41203, 234.35555, 234.3935, 237.1733, 237.3014, 237.7387, 238.4092, 238.7627, 239.2999, 240.41854, 240.70535, 241.50074, 242.3081, 243.05136, 244.1934, 244.4705, 245.10931, 245.82049, 246.9594, 248.24033, 248.45408, 250.07599, 250.19029, 252.681, 252.772, 253.43865, 257.36966, 257.74257, 260.45419, 274.37855, 277.8636, 278.41625, 279.61874, 293.62875, 294.60538, 296.3899, 297.40117, 301.02946, 303.8037, 304.45436, 305.4144, 306.54346, 308.4257, 309.5113, 311.83479, 315.06191, 316.507, 317.5016, 317.7253, 319.2116, 321.07029, 323.0079, 325.3179, 326.27159, 326.6918, 326.9957, 327.6196, 328.0311, 329.6554, 330.38667, 331.4161, 331.4343, 333.03355, 333.3363, 333.41012, 334.7075, 335.5354, 340.1258, 342.64396, 344.35586, 346.1054, 346.48273, 346.8287, 347.0777, 349.13353, 350.41995, 350.52985, 351.4217, 352.4912, 353.08034, 355.79975, 356.0708, 357.4924, 357.53143]
    decs = [-8.76407, 51.31822, 6.53195, -15.41752, -33.9767, -39.6262, 25.24085, -17.6693, -20.2092, 24.7543, -16.841, 7.37458, -52.73978, 40.8811, -4.93266, -0.5533, 43.97032, -9.51747, -11.8719, 41.13331, -9.75475, -11.5608, 46.5118, -40.69557, -24.8105, -27.8562, -43.4178, -15.1609, 16.20213, -38.6961, -21.09307, -73.59328, 35.93716, -4.423, 39.88536, -24.49433, -21.29046, -24.5537, -5.765, -5.95015, -18.7514, -8.42669, 77.1014, -26.7729, -8.015, -63.8231, 19.22514, 1.89147, -23.6338, -16.5953, -55.7534, -44.4703, -22.5409, -2.1379, -61.3624, -25.761, -28.4779, -64.2417, -21.9095, -46.1858, -56.4147, -25.2438, -37.5128, -33.14761, -50.10025, -19.5225, -53.8999, 5.57862, -56.1073, 74.4827, 33.417, 14.4779, -12.28745, 16.57103, -9.0911, -31.03795, 12.46539, -78.3466, -55.5796, -41.3003, -24.7752, -33.43958, -39.5629, -37.50307, -21.42615, 43.8386, -46.8168, -43.59433, -21.8713, 42.49361, -74.801, -12.0221, 51.9505, 64.8715, 27.4276, 16.48577, 47.14735, 19.2501, 48.43086, 6.5938, 36.57881, 24.96211, 44.06425, 27.2757, 39.1398, 20.10874, 25.75083, -26.2236, 6.02722, 53.94018, 8.20466, 12.29191, 45.71233, 70.04488, 52.75489, 4.06792, 3.5247, 26.2029, -29.5505, 35.83334, 5.25435, 50.47213, 15.21507, 33.7291, 0.0559, 62.4116, 44.83183, -9.8054, 5.84834, 4.315, 52.99133, -2.3354, 45.3661, 30.3421, 28.9123, 42.5947, 2.32358, -12.1836, 58.5906, 5.307, 35.5439, 18.59453, 42.13381, 26.58719, -14.3528, -1.50187, 55.89791, 50.46595, 2.0581, 6.8501, 12.48966, 41.2118, 0.7724, 9.4878, -3.1176, -20.7829, 49.22508, 47.15272, -22.769, 26.39171, 7.19, 0.3057, 17.1798, 16.68758, 0.3839, 27.5517, 46.4777, 42.8593, -18.35672, 38.0736, -6.9608, 7.76627, 24.03816, 38.20086, -44.3333, -12.5329, 19.25761, -21.05625, -12.7506, 3.24939, 32.903, 19.5009, 63.77265, 19.66146, 40.22169, 43.53856, -25.7254, -19.4879, 35.49478, -0.10061, -35.716, -2.4604, 33.682, 28.78297, -32.8919, 29.59458, -29.24167, 22.59334, 18.95333, 7.6296, 16.95489, 18.2781, 20.01805, 6.70376, -17.24939, 51.85801, 10.8778, 48.11208, 30.34, -28.1279, 38.01177, 18.17581, 3.79442, 33.25953, 1.30153, 13.1775, 62.0118, 12.4521, 11.63464, -22.9565, 1.47053, 31.58141, 15.22361, 9.99203, 61.44446, 4.3747, 52.19158, -1.038, 52.07313, 11.49539, 52.4462, 22.9335, 60.121, 40.92655, -1.427, 42.40822, 14.79301, -2.03497, 38.73934, 15.19327, 31.62784, 46.97113, 52.9135, 48.02056, 44.16377, -14.003, 1.69433, 10.63454, -30.17139, 30.24825, -29.2351, 30.7879, 2.3629, 31.82542, 31.3125, 37.35999, 43.27994, 45.43528, -23.55612, 65.5411, 39.34632, 14.26214, 38.4603, 12.0613, 75.55507, -2.40363, -0.55586, 31.56997, 10.7514, 19.54921, 42.86369, -4.29027, 51.91796, 38.467, 43.54287, 88.70621, 27.49447, 54.79965, -21.06111, -34.4616, 50.42312, 66.81471, -28.9548, 77.54416, -13.82519, 7.1171, 62.07877, -41.26587, -45.60753, -47.3956, -40.1371, 26.73367, -44.86851, -49.7482, -37.9183, 21.5164, 2.4297, 16.53841, 26.0517, -42.9529, 63.76145, -0.7957, -13.6772, -46.8809, -27.5304, -58.201, -32.02889, 10.3307, -37.4504, 31.73785, -59.4376, -26.8742, -33.3787, 27.7594, 3.35855, 21.28988, 23.8251, -22.2461, 37.23932, -30.6547, 32.0294, 6.18036, 5.46011, 19.7397, -52.4875, -12.983, -18.86853, -0.84286, -30.9405, -45.3147, 36.90959]

    instrument_use = 'WFC3' #'WFC3'

    for i in range(len(ras)):
        ra, dec = ras[i], decs[i]
        filtered_results = best_hst(ra, dec, datemin='1988-01-01T00:00:00.000', datemax='2023-02-14T00:00:00.000', one_instrument=instrument_use)
        if filtered_results:
            for j in range(len(filtered_results)):
                instr, filt = filtered_results['instrument_name'][j], filtered_results['energy_bandpassName'][j]
                savedir = '/Users/cameron/OBJECTS/HST_cutouts/'
                savename = str(ras[i])+'HST_'+instr+'_'+filt+'.png'
                image, pixscale, url = download_cutouts_HLA(observation=filtered_results[[j]], savedir=savedir, savename=savename, ra=ra, dec=dec, size=10)
                print(i, instr, filt)
                if image:
                    print(i, instr, filt)
                    datajson = construct_json(observation=filtered_results[[j]], pixscale=pixscale, imagename=savename, ra=ra, dec=dec, url=url)
                    print(datajson)
                    #outfile = open(json_outname, 'w')
                    #json.dump(datajson, outfile)
                    #outfile.close()