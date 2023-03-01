#!/bin/bash

if [ $# != 1 ]
then
    echo "One command line argument is required: "
    echo "  1 - the full path to the SLED project directory, i.e. the directory containing SLED_api"
    exit 0
fi
spd=${1%/} # This has to be the SLED project dir, i.e. the directory containing SLED_api
dir=$(pwd)

echo $spd
echo $dir


# Check host name - needed for calls to the API by the upload scripts
host_ip=`python -c 'import socket; print(socket.gethostbyname(socket.gethostname()))'`
echo "Host IP is: " $host_ip


# Activate SLED environment
eval "$(conda shell.bash hook)"
if [ `hostname -s` = "django01" ]
then
    conda activate /projects/astro/sled/SLED_environment
else
    conda activate SLED_environment
fi


if [ `hostname -s` == "django01" ]
then
    export DJANGO_SECRET_KEY=`cat ${spd}/launch_server/secret_key.txt`
    export DJANGO_EMAIL_PASSWORD=`cat ${spd}/launch_server/email_password.txt`   
fi


echo "Adding users..."
python ${spd}/SLED_api/manage.py shell < ${dir}/add_users/populate_db.py
echo "Adding users...OK"

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


echo "Adding catalogue data..."
cd ${dir}/add_data
python upload_initial_catalogues_direct.py ${spd}/SLED_api > ../report_add_catalogues.txt
echo "Adding catalogue data...OK"


echo "Adding HST imaging data..."
cd ${dir}/add_data
python upload_initial_HST_imaging.py ${spd}/SLED_api > ../report_add_HST_imaging.txt
echo "Adding HST imaging data...OK"

echo "Adding imaging data..."
cd ${dir}/add_data
python upload_initial_imaging.py ${spd}/SLED_api > ../report_add_imaging.txt
echo "Adding imaging data...OK"

<<comment
comment