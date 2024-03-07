#!/bin/bash

if [ $# != 2 ]
then
    echo "Two command line arguments are required: "
    echo "  1 - the mode of the django server: 'production' or 'debug' or 'production_ro'"
    echo "  2 - the full path to the SLED project directory, i.e. the directory containing SLED_api"
    exit 0
fi
mode=$1
spd=${2%/}
dir=$(pwd)

sudo ${root_path}/SLED_operations/launch/set_server.sh $mode $root_path

# Check host name - needed for calls to the API by the upload scripts
host_ip=`python3 -c 'import socket; print(socket.gethostbyname(socket.gethostname()))'`
echo "Host IP is: " $host_ip



echo "Adding users..."
sudo python3 ${spd}/SLED_api/manage.py shell < ${dir}/add_users/populate_db.py
echo "Adding users...OK"
exit

echo "Adding lenses..."
cd ${dir}/add_lenses
python ${spd}/SLED_api/manage.py shell < upload_directly.py > ../report_add_lenses.txt
echo "Adding lenses...OK"

echo "Adding instruments and bands..."
cd ${dir}/add_data
python ${spd}/SLED_api/manage.py shell < add_instruments_bands.py
echo "Adding instruments and bands...OK"

echo "Adding spectra..."
cd ${dir}/add_data
python upload_initial_spectra.py ${spd}/SLED_api > ../report_add_spectra.txt
echo "Adding spectra...OK"

echo "Adding queries..."
cd ${dir}/add_queries
python ${spd}/SLED_api/manage.py shell < create_queries.py
echo "Adding queries...OK"

echo "Adding collections..."
cd ${dir}/add_collections
python ${spd}/SLED_api/manage.py shell < upload_collection.py > ../report_add_collections.txt
echo "Adding collections...OK"

echo "Adding papers..."
cd ${dir}/add_papers
python ${spd}/SLED_api/manage.py shell < upload_papers_API.py > ../report_add_papers.txt
echo "Adding papers...OK"

echo "Adding redshifts..."
cd ${dir}/add_data
python upload_initial_redshifts.py > ../report_add_redshifts.txt
echo "Adding redshifts...OK"

echo "Adding HST imaging data..."
cd ${dir}/add_data
python upload_initial_HST_imaging.py ${spd}/SLED_api > ../report_add_HST_imaging.txt
echo "Adding HST imaging data...OK"

echo "Adding imaging data..."
cd ${dir}/add_data
python upload_initial_imaging.py ${spd}/SLED_api > ../report_add_imaging.txt
echo "Adding imaging data...OK"


echo "Adding catalogue data..."
cd ${dir}/add_data
python upload_initial_catalogues_direct.py ${spd}/SLED_api > ../report_add_catalogues.txt
echo "Adding catalogue data...OK"


echo "Adding deleting notifications..."
cd ${dir}/
python ${spd}/SLED_api/manage.py shell < delete_notifications.py
echo "Adding deleting notifications...OK"
