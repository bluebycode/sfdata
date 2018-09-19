./clean && docker build -t sfapp . &&  docker run -p 80:80 -t  sfapp

# San Francisco (flask node)

## Working with docker

```
docker build -t sfapp .
id=`docker run -p 80:80 --rm --name sfapp -d sfapp`
docker logs -f $id
```

```
docker network create --subnet=172.30.0.0/16 sfnetwork
docker run -p 80:80 --rm --name sfapp --net sfnetwork --ip 172.30.0.1 -d sfapp
```

## Working with google cloud and kubernetes

References: https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app

Requirements:
* Install kubectl ```gcloud components install kubectl```

```
export PROJECT_ID="$(gcloud config get-value project -q)"
docker build -t gcr.io/$PROJECT_ID/sfapp:v1 .
gcloud docker -- push gcr.io/$PROJECT_ID/sfapp:v1
gcloud container clusters create sfcappcluster --num-nodes=1
```

* Remote deployment
References: https://cloud.google.com/kubernetes-engine/docs/tutorials/http-balancer
```
kubectl run sfapp --image=gcr.io/$PROJECT_ID/sfapp:v1 --port 80
```

# Configure loadbalancing
```
kubectl expose deployment sfapp --target-port=80 --type=NodePort
kubectl apply -f basic-ingress.yaml
```

* Accesses

```
kubectl get pods
kubectl exec -it sfapp-7b774d78db-67hzt -- /bin/bash
```

