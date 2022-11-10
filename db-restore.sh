#!/bin/bash
date=$1
path='/mnt/nosql-backup/'${date}'/data/rankworksDB'


echo "### Fetching backup from google storage ..."
docker cp $path rankworks-nosql:/db-resotore
echo "### Fetched and then copied to docker container: ${path}  ..."


echo "### Restore APIs database ..."
docker exec -i rankworks-nosql /usr/bin/mongorestore db-resotore/