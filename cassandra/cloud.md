# San Francisco (cassandra node)

## Working with docker

```
docker build -t sfcassandra .
id=`docker run -p 9042:9042 --rm --name sfcassandra -d sfcassandra`
docker logs -f $id
docker exec -i -t sfcassandra sh -c 'nodetool status'
docker exec -i -t sfcassandra sh -c 'exec cqlsh 172.30.0.3'
```

```
docker network create --subnet=172.30.0.0/16 sfnetwork
docker run -p 9042:9042 --rm --name sfcassandra --net sfnetwork --ip 172.30.0.3 -d sfcassandra
```

## Working with google cloud and kubernetes

References: https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app

Requirements:
* Install kubectl ```gcloud components install kubectl```

```
export PROJECT_ID="$(gcloud config get-value project -q)"
docker build -t gcr.io/$PROJECT_ID/sfcassandra:v1 .
gcloud docker -- push gcr.io/$PROJECT_ID/sfcassandra:v1


# creating cluster https://cloud.google.com/sdk/gcloud/reference/container/clusters/create
gcloud container clusters create sfcassandracluster --num-nodes=1
or
gcloud container clusters create sfcassandracluster --machine-type=n1-highmem-2 --num-nodes=1
```

* Remote deployment

```
kubectl run sfcassandra --image=gcr.io/$PROJECT_ID/sfcassandra:v1 --port 9042
```

* Accesses

```
kubectl get pods
id=`kubectl get pods|grep cassandra|awk '{print $1}'`
kubectl exec -it $id -- bin/bash
kubectl exec -it $id -- sh -c 'nodetool status'
kubectl exec -it $id  -- sh -c 'exec cqlsh 10.32.0.12'
10.16.0.27
```

