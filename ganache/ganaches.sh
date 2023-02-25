#!/bin/bash
re='^[0-9]+$'
ports=$(printenv PORTS)
base_port=$(printenv BASE_PORT)

if [ -z $ports ]; then
	echo "error: unspecified number of ports"
	exit 1
fi

if [ -z $base_port ]; then
	echo "error: unspecified base port"
	exit 1
fi

if ! [[ $ports =~ $re ]];  then
	echo "error: number of ports must be a number"
	exit 1	
fi

if ! [[ $base_port =~ $re ]];  then
	echo "error: base port must be a number"
	exit 1	
fi

if (( $ports < 2 )) || (( $ports > 10 )); then
	echo "error: number of ports must be between 2 and 10"
	exit 1
fi

if (( $base_port < 1025 )) || (( $base_port + $ports > 65535 )); then
	echo "error: ports to be used must be between 1025 and 65535"
	exit 1
fi

for (( i = 0 ; i < $ports ; i += 1 )) ; do
	mkdir "db_$i"
	(node "/app/dist/node/cli.js" -p $(($base_port + $i)) --database.dbPath "db_$i" -m "myth like bonus scare over problem client lizard pioneer submit female collect" -a 10 -e 10000 --wallet.accountKeysPath "db_$i/keys.json") &
done

wait