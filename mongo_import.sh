#!/bin/bash
DATA_DIR="$( dirname ${BASH_SOURCE[0]} )/data"
for collection in 'Resource' 'ResourceVersion' 'SubjectVersion'
do
echo
    gunzip -c ${DATA_DIR}/${collection}.json.gz | docker-compose exec -T mongo bash -c "mongoimport --username=\${MONGODB_USERNAME} --password=\${MONGODB_PASSWORD} --db=\${MONGODB_DATABASE} --collection=${collection}" 
done
