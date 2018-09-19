# How to run the stack into the Google Cloud using Kubernetes

kb()  { kubectl $@ ;}
eval $(docker-machine env default)

export PROJECT_ID="$(gcloud config get-value project -q)"

# application cluster (first time)
gcloud container clusters create 	sfcappcluster --num-nodes=1

# application build instance
docker build -t gcr.io/$PROJECT_ID/sfcassandra:v2.5 .

gcloud docker -- push gcr.io/$PROJECT_ID/sfcassandra:v2.5

kb delete deployment sfapp

kb run sfapp --image=gcr.io/$PROJECT_ID/sfapp: --env="CASSANDRA_HOST=10.16.0.13"

