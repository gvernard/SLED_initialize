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


# Activate SLED environment
if [ `hostname -s` = "django01" ]
then
    source /home/astro/gvernard/miniconda3/bin/activate sled
else
    eval "$(conda shell.bash hook)"
    conda activate SLED_environment
fi




echo "Adding users..."
python ${spd}/SLED_api/manage.py shell < ${dir}/add_users/populate_db.py
echo "Adding users...OK"

echo "Adding lenses..."
cd ${dir}/add_lenses
python ${spd}/SLED_api/manage.py shell < upload_directly.py > ../report_add_lenses.txt
echo "Adding lenses...OK"

echo "Adding papers..."
cd ${dir}/add_papers
python ${spd}/SLED_api/manage.py shell < upload_papers_API.py > ../report_add_papers.txt
echo "Adding papers...OK"

echo "Adding collections..."
cd ${dir}/add_collections
python ${spd}/SLED_api/manage.py shell < upload_collection.py > ../report_add_collections.txt
echo "Adding collections...OK"

echo "Adding instruments and bands..."
cd ${dir}/add_data
python ${spd}/SLED_api/manage.py shell < add_instruments_bands.py
echo "Adding instruments and bands...OK"

echo "Adding imaging data..."
cd ${dir}/add_data
python upload_initial_imaging.py ${spd}/SLED_api > ../report_add_imaging.txt
echo "Adding imaging data...OK"

echo "Adding spectra..."
cd ${dir}/add_data
python upload_initial_spectra.py ${spd}/SLED_api > ../report_add_spectra.txt
echo "Adding spectra...OK"

echo "Adding catalogue data..."
cd ${dir}/add_data
python upload_initial_catalogues_direct.py ${spd}/SLED_api > ../report_add_catalogues.txt
echo "Adding catalogue data...OK"

echo "Adding queries..."
cd ${dir}/add_queries
python ${spd}/SLED_api/manage.py shell < create_queries.py
echo "Adding queries...OK"
