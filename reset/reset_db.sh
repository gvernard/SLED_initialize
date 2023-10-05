#!/bin/bash

database=$1
spd=$2
launch=${spd}/SLED_operations/launch_server
echo "Working on database: "$database


if [ $database == "sqlite" ]
then
    echo "Using local sqlite DB server..."
    cd ${spd}/SLED_api/
    rm db.sqlite3
elif [ $database == "test" ]
then
    echo "Using TEST Mysql DB server..."
    echo "Dropping all tables"
    bash drop_all_tables.sh ${launch}/test_localhost.cnf
elif [ $database == "production" ]
then
    read -p "DANGER: deleting PRODUCTION database tables - are you sure? (Y/y=yes)" -n 1 -r reply
    if [[ $reply =~ ^[Yy]$ ]]
    then
	echo -e "\n"
	echo "Using PRODUCTION Mysql DB server..."
	echo "Dropping all tables"
	bash drop_all_tables.sh ${launch}/production_root.cnf
    else
	exit 0
    fi    
fi

rm ${spd}/SLED_api/*/migrations/0*.py
