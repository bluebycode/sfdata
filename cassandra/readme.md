docker build -t sfcassandra .
id=`docker run -p 9042:9042 --rm --name sfcassandra -d sfcassandra`
docker logs -f $id
docker exec -i -t sfcassandra sh -c 'nodetool status'
docker exec -i -t sfcassandra sh -c 'exec cqlsh 172.17.0.3'

docker network create --subnet=172.30.0.0/16 sfnetwork
docker run -p 9042:9042 --rm --name sfcassandra --net sfnetwork --ip 172.30.0.3 -d sfcassandra
 docker build -t gcr.io/sfdatascience-216716/sfcassandra:v1 .
