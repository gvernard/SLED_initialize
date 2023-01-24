#!/bin/bash

database=$1
host=$2
spd=$3

if [ $host = "localhost" ]
then
    cd ../../
    rm -r FILES_TEST
    mkdir FILES_TEST
    mkdir FILES_TEST/lenses
    mkdir FILES_TEST/imaging
    mkdir FILES_TEST/spectrum
    mkdir FILES_TEST/temporary
elif [ $host = "server" ]
then
    file_source=""
    if [ $database = "test" ]
    then
	file_source="FILES_TEST"
    else
	read -p "DANGER: deleting production database files - are you sure? " -n 1 -r reply
	echo "\n"
	if [[ $reply =~ ^[Yy]$ ]]
	then
	    file_source="FILES"
	else
	    exit 0
	fi
    fi

    unlink ${spd}/${file_source}

    cd ../../
    rm -r ${file_source}
    mkdir ${file_source}
    mkdir ${file_source}/lenses
    mkdir ${file_source}/imaging
    mkdir ${file_source}/spectrum
    mkdir ${file_source}/temporary

    cd ${spd}
    ln -s /projects/astro/sled/${file_source}
fi


