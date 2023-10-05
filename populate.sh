#!/bin/bash

if [ $# != 2 ]
then
    echo "Two command line arguments are required: "
    echo "  1 - the database to reset: 'test' or 'production' or 'sqlite'"
    echo "  2 - the full path to the SLED project directory, i.e. the directory containing SLED_api"
    exit 0
fi
database=$1
spd=${2%/} # This has to be the SLED project dir, i.e. the directory containing SLED_api
dir=$(pwd)
launch=${spd}/SLED_opetations/launch_server


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


export DJANGO_SECRET_KEY=`cat ${launch}/secret_key.txt`
export DJANGO_EMAIL_PASSWORD=`cat ${launch}/email_password.txt`   
export DJANGO_STATIC_ROOT=/projects/astro/sled/STATIC
export DJANGO_DOMAIN_NAME=sled.astro.unige.ch
if [ $database = "test" ]
then
    export DJANGO_MEDIA_ROOT=/projects/astro/sled/FILES_TEST
    export DJANGO_DB_FILE=${launch}/test_server.cnf
    cp ${launch}/settings_debug.py ${spd}/SLED_api/mysite/settings.py
else
    export DJANGO_MEDIA_ROOT=/projects/astro/sled/FILES
    export DJANGO_DB_FILE=${launch}/test_localhost.cnf
    export DJANGO_NO_LAST_LOGIN=false
    cp ${launch}/settings_server_root.py ${spd}/SLED_api/mysite/settings.py
fi


if [ $database = "sqlite" ]
then
    cp ${launch}/settings_localhost_sqlite.py ${spd}/SLED_api/mysite/settings.py
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
