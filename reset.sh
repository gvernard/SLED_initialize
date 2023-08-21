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



# Resetting the server can occur only on django01
if [ $host = "server" ] && [ `hostname -s` != "django01" ]
then
    echo "The host option is server but the actual host is not django01!"
    exit 0    
fi



# Resetting the sqlite database can occur only on the localhost
if [ $database = "sqlite" ] && [ $host = "server" ]
then
    echo "The sqlite database can be used only locally, i.e. not on django01"
    exit 0
fi



# Resetting any of the MySQL databases can occur only on the django server
if ([ $database = "test" ] || [ $database = "production" ]) && [ `hostname -s` != "django01" ]
then
    echo "The test or production database has to be used on django01!"
    exit 0
fi



# Check that spd is consistent with 'sled' and 'sled_test' directories on django01
if [ `hostname -s` == "django01" ]
then
   spd_name=$(basename $spd)
   if [ $database = "test" ] && [ $spd_name != "sled_test" ]
   then
       echo "You are using the 'test' database and the production path!"
       exit 0    
   fi
   if [ $database = "production" ] && [ $spd_name != "sled" ]
   then
       echo "You are using the 'production' database and the test path!"
       exit 0    
   fi
fi




cwd=$(pwd)
cd ${cwd}/reset

# Delete database tables
echo "Reseting database..."
./reset_db.sh $database $spd
echo "Reseting database...OK"

# Delete files
echo "Deleting files..."
./reset_FILES.sh $database $host $spd
echo "Deleting files...OK"

# Server settings
if [ $host = "localhost" ]
then
    cp ${spd}/launch_server/settings_localhost_sqlite.py ${spd}/SLED_api/mysite/settings.py
else
    if [ $database = "test" ]
    then
	export DJANGO_SECRET_KEY='django-insecure-3#$_(o_0g=w68gw@y5anq4$yb2$b!&1_@+bk%jse$*mboql#!t'
	export DJANGO_EMAIL_PASSWORD='ixzdsavcwdgohgrj'
	export DJANGO_MEDIA_ROOT=`pwd`/../FILES_TEST
	export DJANGO_STATIC_ROOT=`pwd`/../SLED_api/staticfiles
	export DJANGO_DB_FILE=`pwd`/../launch_server/test_server.cnf
	cp ${spd}/launch_server/settings_debug.py ${spd}/SLED_api/mysite/settings.py
    else
	export DJANGO_SECRET_KEY=`cat ${spd}/launch_server/secret_key.txt`
	export DJANGO_EMAIL_PASSWORD=`cat ${spd}/launch_server/email_password.txt`
	export DJANGO_MEDIA_ROOT=`pwd`/../FILES_TEST
	export DJANGO_STATIC_ROOT=`pwd`/../SLED_api/staticfiles
	export DJANGO_DB_FILE=`pwd`/../launch_server/test_localhost.cnf
	export DJANGO_NO_LAST_LOGIN=false
	cp ${spd}/launch_server/settings_server_root.py ${spd}/SLED_api/mysite/settings.py
    fi
fi

# Activate SLED environment
eval "$(conda shell.bash hook)"
if [ `hostname -s` = "django01" ]
then
    conda activate /projects/astro/sled/SLED_environment
else
    conda activate SLED_environment
fi

# Migrate the database with the django server
cd ${spd}/SLED_api

which python
echo "Running 'makemigrations': ..."
python manage.py makemigrations
echo "Running 'makemigrations': OK"

echo "Running 'migrate': ..."
python manage.py migrate
echo "Running 'migrate': OK"

