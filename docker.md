eval $(docker-machine env default)

# cassandra
docker build -t sfcassandra .

# cassandra volumes
docker volume create sfcassandra-volume
docker run --name sfaccess -v cassandra-volume:/opt:r -ti ubuntu /bin/bash

# cassandra instances
docker run -p 9042:9042 --name sfcassandra \
	-v cassandra-volume:/var/lib/cassandra:rw \
	--ulimit nofile=100000:100000 \
	--ulimit nproc=32768 \
	--memory-swappiness -1 \
	sfcassandra

# cassandra get current ip
docker inspect sfcassandra --format '{{ .NetworkSettings.IPAddress }}'

# cassandra check nodes ring
docker exec -it sfcassandra sh -c 'nodetool status'

# cassandra run the cql bash
docker exec -it sfcassandra sh -c 'exec cqlsh -f /docker-entrypoint-initdb.d/init.cql'

# application creation
docker build -t sfapp .

# application instances
docker run -p 80:80 --name sfapp \
	-e CASSANDRA_HOST='172.17.0.2' \
        --ulimit nofile=100000:100000 \
        --ulimit nproc=32768 \
        --memory-swappiness -1 \
        sfapp

