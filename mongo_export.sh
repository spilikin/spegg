#!/bin/bash
for collection in 'Resource' 'ResourceVersion' 'SubjectVersion'
do
    docker-compose exec -T mongo bash -c "mongoexport --username=\${MONGODB_USERNAME} --password=\${MONGODB_PASSWORD} --db=\${MONGODB_DATABASE} --collection=${collection}" | gzip -c > data/${collection}.json.gz
done

