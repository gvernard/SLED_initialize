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

scp USERNAME@login01.astro.unige.ch://home/astro/lemon/SLED_files/initialize_database_data.zip ./
unzip -o -q initialize_database_data.zip
rm initialize_database_data.zip

Now you can initialise the database. Go into SLED_initialize and run the reset_and_populate.sh script.
