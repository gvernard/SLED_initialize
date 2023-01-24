#!/bin/bash

if [ $# != 3 ]
then
    echo "Three command line arguments are required: "
    echo "  1 - the database to reset: 'test' or 'production' or 'sqlite'"
    echo "  2 - the machine where the files are at and where the django server will run : 'server' or 'localhost'"
    echo "  3 - the full path to the SLED project directory, i.e. the directory containing SLED_api"
    exit 0
fi
database=$1
host=$2
spd=${3%/} # This has to be the SLED project dir, i.e. the directory containing SLED_api


if [ $host = "server" ] && [ `hostname -s` != "django01" ]
then
    echo "The host option is server but the actual host is not django01!"
    exit 0    
fi
    

if [ $database = "sqlite" ] && [ $host = "server" ]
then
    echo "The sqlite database can be used only locally, i.e. not on django01"
    exit 0
fi
if ([ $database = "test" ] || [ $database = "production" ]) && [ `hostname -s` != "django01" ]
then
    echo "These test or production database has to be used on django01!"
    exit 0
fi


# Check that spd is consistent with 'sled' and 'sled_test' directories on django01



cwd=$(pwd)
cd ${cwd}/reset

# Delete database tables
./reset_db.sh $database $host

# Delete files
./reset_FILES.sh $database $host $spd

# Server settings
if [ $host = "localhost" ]
then
    cp ${spd}/launch_server/settings_localhost_sqlite.py ${spd}/SLED_api/mysite/settings.py
else
    if [ $database = "test" ]
    then
	cp ${spd}/launch_server/settings_server_test.py ${spd}/SLED_api/mysite/settings.py
    else
	cp settings_server_root.py ${spd}/SLED_api/mysite/settings.py
    fi
fi

# Activate SLED environment
if [ `hostname -s` = "django01" ]
then
    source /home/astro/gvernard/miniconda3/bin/activate sled
else
    eval "$(conda shell.bash hook)"
    conda activate sled
fi

# Migrate the database with the django server
cd ${spd}/SLED_api

python manage.py makemigrations
python manage.py migrate

echo ""
echo ""
echo " --- ATTENTION --- "
echo ""
echo "The django server is running in this terminal."
echo "If you want to populate the database run the respective script in a new terminal."
echo "After the database is populated you can quit the server and close this terminal."
echo ""
echo ""

python manage.py runserver
