# Cassandra nodes with Kubernetes

## References:

* Cassandra docker project. https://github.com/bitnami/bitnami-docker-cassandra
* IBM Steps. https://github.com/IBM/Scalable-Cassandra-deployment-on-Kubernetes
* Stateful references from kubernetes. https://kubernetes.io/docs/tutorials/stateful-application/cassandra/
* Deploy a HA Cassandra AWS. https://medium.com/merapar/deploy-a-high-available-cassandra-cluster-in-aws-using-kubernetes-bd8ba07bfcdd


* [Requirements](#Requirements)
* [Deployment layout steps](#Deployment-layout-steps)
* [Deployment manual procedures](#Deployment-manual-procedures)
* [Troubleshooting](#troubleshooting)

## Requirements:

* Docker context ```eval $(docker-machine env default)```
* Install Kubernetes cmd *kubectl* ```gcloud components install kubectl```
* Kubernetes context (project)
```
kb()  { kubectl $@ ;}
export PROJECT_ID="$(gcloud config get-value project -q)"
```


## Deployment layout steps

* Creating the (stateless) service

```
$ kb create -f cassandra-service.yaml
service "cassandra" created
$ kb get svc cassandra
NAME        TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
cassandra   ClusterIP   None         <none>        9042/TCP   14s
```

* Creating volumes

```
$ kb create -f cassandra-volumes.yaml
persistentvolume "cassandra-volume1" created
persistentvolume "cassandra-volume2" created
$ kubectl get pv
NAME                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM     STORAGECLASS   REASON    AGE
cassandra-volume1   10Gi       RWO            Recycle          Available                                      7s
cassandra-volume2   10Gi       RWO            Recycle          Available                                      7s
```

* Node templates (statefulset)

```
$ kb create -f cassandra-statefulset.yaml
statefulset "cassandra" created
$ kubectl get statefulsets
NAME        DESIRED   CURRENT   AGE
cassandra   1         1         12s
```

```
$kb get pods -o wide
NAME                           READY     STATUS    RESTARTS   AGE       IP           NODE
cassandra-0                    1/1       Running   0          1m        10.32.0.15   gke-sfcassandracluster-default-pool-670a8326-ltvm
```

To check if the Cassandra node is up, perform a nodetool status:
$ kb exec -ti cassandra-0 -- nodetool status

* Scaling up to 2 nodes

```
$ kb scale --replicas=2 statefulset/cassandra
statefulset "cassandra" scaled
$ kb get statefulsets
NAME        DESIRED   CURRENT   AGE
cassandra   2         2         4m
$ kb get pods -o wide
NAME                           READY     STATUS    RESTARTS   AGE       IP           NODE
cassandra-0                    1/1       Running   0          4m        10.32.0.15   gke-sfcassandracluster-default-pool-670a8326-ltvm
cassandra-1                    1/1       Running   0          44s       10.32.0.16   gke-sfcassandracluster-default-pool-670a8326-ltvm
```

```
$ kb exec -ti cassandra-0 -- nodetool status
Datacenter: SFDataCenter1
=========================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address     Load       Tokens       Owns (effective)  Host ID                               Rack
UN  10.32.0.16  94 KiB     256          100.0%            868db7e3-f332-4013-8d37-c2f6d0c07df6  SFRack1
UN  10.32.0.15  108.62 KiB  256          100.0%            9295309b-8004-4ed5-a26b-4d1cb6de82c6  SFRack1
```

```
$ kb exec -ti cassandra-0 -- cqlsh
Connected to SFCassandraCluster at 127.0.0.1:9042.
[cqlsh 5.0.1 | Cassandra 3.11.3 | CQL spec 3.4.4 | Native protocol v4]
Use HELP for help.
cqlsh>
```

* Import the dataset

```
$ kb exec -ti cassandra-0 -- /bin/bash

$ apt-get update \
	&& apt-get install -y wget \
	&& wget -O mega.py https://gist.githubusercontent.com/vrandkode/7a31d261f26c1f6db4ddbb8ea7fbb0cc/raw/2460dee8e50cd148a59277b829eed22f336b1e78/mega.py \
	&& mkdir /datasets && python mega.py 'https://mega.nz/#!GqRlAaRC!r5zOJxSZwXe40ov_7zhqiLqThOij804K9g73y_Q_DaA'
	&& mv mega_GqRlAaRC_incidents.all.csv /datasets/incidents.all.csv
```


## Deployment manual procedures

* Building and publishing cassandra new images

```
$ export PROJECT_ID="$(gcloud config get-value project -q)"
$ docker build -t gcr.io/$PROJECT_ID/sfcassandra:v1 .
$ gcloud docker -- push gcr.io/$PROJECT_ID/sfcassandra:v1
```

* Creating cassandra cluster with machine profiles

```
$ gcloud container clusters create sfcassandracluster \
    --machine-type=n1-highmem-2 \
    --num-nodes=1
```

* Running a new pod

```
kubectl run sfcassandra --image=gcr.io/$PROJECT_ID/sfcassandra:v1 --port 9042
```

* Controlling the nodes

```
kubectl get pods
id=`kubectl get pods|grep cassandra|awk '{print $1}'`
kubectl exec -it $id -- bin/bash
kubectl exec -it $id -- sh -c 'nodetool status'
kubectl exec -it $id  -- sh -c 'exec cqlsh 10.32.0.12'
10.16.0.27

