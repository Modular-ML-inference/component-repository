# FL Repository

Before running, place the `db.dump` folder inside the mongodb folder: 
https://drive.google.com/file/d/1s2TRJ_MQ_tNZI3j03A_O9eCwYe_nVxQz/view?usp=sharing
Run `docker-compose up --force-recreate --build -d` to run the server.

Interactive API docs: http://127.0.0.1:9013/docs

New additions:

# Kubernetes configuration

In order to properly set up the enabler with the use of Helm charts, first you have to set up the appropriate configuration. For this purposes, the `repository-config-map.yaml` is included in this repository. This is a ConfigMap containing information that may be specific to this deployment that the application must be able to access.

After performing appropriate modifications, run `kubectl apply -f repository-config-map.yaml` to create the ConfigMap. Finally, run `helm install flrepositorylocaldb flrepositorydb` in order to properly install the release using Helm charts.

You can later use `kubectl port-forward <podname> <hostport>:9012` to forward port to your localhost and easily set up local configuration on `127.0.0.1:9012/docs`.



