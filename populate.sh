#!/bin/bash

if [ $# != 1 ]
then
    echo "One command line argument is required: "
    echo "  1 - the full path to the SLED project directory, i.e. the directory containing SLED_api"
    exit 0
fi
spd=${1%/} # This has to be the SLED project dir, i.e. the directory containing SLED_api
echo $spd


# Activate SLED environment
if [ `hostname -s` = "django01" ]
then
    source /home/astro/gvernard/miniconda3/bin/activate sled
else
    eval "$(conda shell.bash hook)"
    conda activate sled
fi

dir=$(pwd)
echo $dir



python manage.py shell < ${dir}/add_users/populate_db.py

# Requires the server to be running for the API call
cd ${dir}/add_lenses
python upload_through_api.py

# Requires the server to be running for the API call
cd ${dir}/add_papers
python upload_papers_API.py

# Requires the server to be running for the API call
cd ${dir}/add_collections
python upload_collection.py

# Requires the server to be running for the API call (through the database_utils.py)
cd ${dir}/add_data
python ${spd}/SLED_api/manage.py shell < add_instruments_bands.py
python upload_initial_imaging.py ${spd}/SLED_api
python upload_initial_spectra.py ${spd}/SLED_api
python upload_initial_catalogues.py ${spd}/SLED_api

cd ${dir}/add_queries
python ${spd}/SLED_api/manage.py shell < create_queries.py
