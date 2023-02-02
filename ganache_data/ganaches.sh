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
	#add ganache parameters
	#add logging
	(node "/app/dist/node/cli.js" -p $(($base_port + $i)) --database.dbPath "/ganache_data/db_$i" -d -a 5 -e 1000 ) &
done

wait
