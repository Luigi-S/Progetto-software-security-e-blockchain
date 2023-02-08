#!/bin/bash
re='^[0-9]+$'
ports=$(printenv PORTS)
base_port=10000

if [ -z $ports ]; then
	echo "error: unspecified number of ports"
	exit 1
fi

if ! [[ $ports =~ $re ]];  then
	echo "error: number of ports must be a number"
	exit 1	
fi

if (( $ports < 2 )) || (( $ports > 10 )); then
	echo "error: number of ports must be between 2 and 10"
	exit 1
fi

for (( i = 0 ; i < $ports ; i += 1 )) ; do
	mkdir "db_$i"
	(node "/app/dist/node/cli.js" -p $(($base_port + $i)) --database.dbPath "db_$i" -d -a 1 -e 10000 --wallet.accountKeysPath "db_$i/keys.json") &
done

wait