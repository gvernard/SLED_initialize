#!/bin/bash

database=$1
spd=$2
echo "Working on database: "$database


if [ $database == "sqlite" ]
then
    echo "Using local sqlite DB server..."
    cd ${spd}/SLED_api/
    rm db.sqlite3
    rm */migrations/0*.py
elif [ $database == "test" ]
then
    echo "Using TEST Mysql DB server..."
    echo "Dropping all tables"
    bash drop_all_tables.sh ../SENSITIVE/localhost_test.cnf
elif [ $database == "production" ]
then
    echo "Using PRODUCTION Mysql DB server..."
    echo "Dropping all tables"
    bash drop_all_tables.sh ../SENSITIVE/server_root.cnf
fi



