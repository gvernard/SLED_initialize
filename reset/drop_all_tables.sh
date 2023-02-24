#!/bin/bash

cnf_file=$1

# Detect paths
MYSQL=$(which mysql)
AWK=$(which awk)
GREP=$(which grep)

# Get database connection parameters
MHOST=$($AWK '/^host/{print $3}' $cnf_file)
MPORT=$($AWK '/^port/{print $3}' $cnf_file)
MDB=$($AWK '/^database/{print $3}' $cnf_file)
MUSER=$($AWK '/^user/{print $3}' $cnf_file)
MPASS=$($AWK '/^password/{print $3}' $cnf_file)
#echo $MHOST $MPORT $MDB $MUSER $MPASS
#exit 0


TABLES=$($MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e 'show tables' | $AWK '{ print $1}' | $GREP -v '^Tables' )

for t in $TABLES
do
    echo "Deleting table: $t"
    $MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e "SET FOREIGN_KEY_CHECKS=0; DROP TABLE $t;" # The FOREIGN_KEY_CHECKS applies per connection.
done
$MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e "DROP FUNCTION distance_on_sky;"


#$MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e "SET FOREIGN_KEY_CHECKS = 1;"
$MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e "ALTER DATABASE $MDB CHARACTER SET utf8 COLLATE utf8_bin;"
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
$MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB < $SCRIPTPATH/function_distance_on_sky.sql
$MYSQL -h $MHOST -P $MPORT -u $MUSER -p$MPASS $MDB -e "GRANT EXECUTE ON FUNCTION strong_lenses_database.distance_on_sky TO 'sled_rw'@'10.25.64.150';"
