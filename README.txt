The are two scripts and two corresponding directories here.

RESET:
Run the reset.sh script to:
    - Delete all the database tables.
      For the MySQL database, it leaves an empty database but it install the distance_on_the_sky custom function.
    - Delete all the files associated to the database.
    - Create all the new tables in the database by migrating it.

The script then launches the django server in the terminal and waits.


POPULATE:
Run the populate script to populate the database.






################ OLD README ################
First off, you’ll need the files (images/jsons/paper csvs etc.).
So I’ve put them on observatory filesystem and you can just copy them across, while in the base SLED directory:

scp USERNAME@login01.astro.unige.ch://home/astro/lemon/SLED_files/data_files.zip ./data/images_to_upload/
cd data/images_to_upload/
unzip -o -q data_files.zip
rm data_files.zip

cd ../..
scp USERNAME@login01.astro.unige.ch://home/astro/lemon/SLED_files/paper_files.zip ./data/add_papers/
cd ./data/add_papers/
unzip -o -q paper_files.zip
rm paper_files.zip

Now you can initialise the database. Go into initialise_database and run the reset_and_populate.sh script.
The database should not be running when starting this script.
You will be prompted to start the database after a few seconds, when data ingestion is about to start.

