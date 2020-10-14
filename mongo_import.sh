#!/bin/bash
for collection in 'Resource' 'ResourceVersion' 'SubjectVersion'
do
    gunzip -c data/${collection}.json.gz | docker-compose exec -T mongo bash -c "mongoimport --username=\${MONGODB_USERNAME} --password=\${MONGODB_PASSWORD} --db=\${MONGODB_DATABASE} --collection=${collection}" 
done
