#!/usr/bin/bash
export container=`docker run --rm -d -v "$(pwd)"/argos-adf:/argos-adf argos`
docker exec -d $container start.sh $1
echo Container: $container
