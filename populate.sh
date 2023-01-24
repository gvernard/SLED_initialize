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




echo "Adding users..."
python ${spd}/SLED_api/manage.py shell < ${dir}/add_users/populate_db.py
echo "Adding users...OK"

# Requires the server to be running for the API call
cd ${dir}/add_lenses
echo "Adding lenses..."
touch ../report_add_lenses.txt
python upload_through_api.py > ../report_add_lenses.txt
echo "Adding lenses...OK"

# Requires the server to be running for the API call
cd ${dir}/add_papers
echo "Adding papers..."
touch ../report_add_papers.txt
python upload_papers_API.py > ../report_add_papers.txt
echo "Adding papers...OK"

# Requires the server to be running for the API call
cd ${dir}/add_collections
echo "Adding collections..."
touch ../report_add_collections.txt
python upload_collection.py > ../report_add_collections.txt
echo "Adding collections...OK"

echo "Adding instruments and bands..."
cd ${dir}/add_data
python ${spd}/SLED_api/manage.py shell < add_instruments_bands.py
echo "Adding instruments and bands...OK"

# Requires the server to be running for the API call (through the database_utils.py)
echo "Adding imaging data..."
touch ../report_add_imaging.txt
python upload_initial_imaging.py ${spd}/SLED_api > ../report_add_imaging.txt
echo "Adding imaging data...OK"

# Requires the server to be running for the API call (through the database_utils.py)
echo "Adding spectra..."
touch ../report_add_spectra.txt
python upload_initial_spectra.py ${spd}/SLED_api > ../report_add_spectra.txt
echo "Adding spectra...OK"

# Requires the server to be running for the API call (through the database_utils.py)
echo "Adding catalogue data..."
touch ../report_add_catelogues.txt
python upload_initial_catalogues.py ${spd}/SLED_api > ../report_add_catalogues.txt
echo "Adding catalogue data...OK"

echo "Adding queries..."
cd ${dir}/add_queries
python ${spd}/SLED_api/manage.py shell < create_queries.py
echo "Adding queries...OK"
