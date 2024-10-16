# Pasos deployment

Crear proyecto con nombre abcall para no cambiar nada en los ejemplos de los pasos ni en el archivo de k8s.


Todos los pasos es para hacerlos desde la raiz del proyecto

## Subir imagenes de los contenedores

### 1. Habilitar API de container registry en GCP

Ir a GCP y en artifact registry habilitar la API y crear el repoistorio donde se colocaran las imagenes de los contenedores

Autenticarse en gcp 
```
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Crear repositorio **abcall**

### 2. Configurar CLI para apuntar a la region seleccionada
```
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 3. Construir imagenes de los servicios
Recordar la construccion de la URI <REGION>-docker.pkg.dev/<ID-PROYECTO>/<NOMBRE-REPOSITORIO>/<IMAGEN>:<TAG>


```shell
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/api-gateway:latest -f ./api-gateway/Dockerfile ./api-gateway
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/gestor-clientes:latest -f ./gestor-clientes/Dockerfile ./gestor-clientes
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/generacion-reportes:latest -f ./generacion-reportes/Dockerfile ./generacion-reportes
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/gestor-incidentes:latest -f ./gestor-incidentes/Dockerfile ./gestor-incidentes
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/gestor-fidelizacion:latest -f ./gestor-fidelizacion/Dockerfile ./gestor-fidelizacion
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/vista-360:latest -f ./vista-360/Dockerfile ./vista-360
```

experimento
```shell
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/api-gateway:latest -f ./api-gateway/Dockerfile ./api-gateway
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/gestor-incidentes:latest -f ./gestor-incidentes/Dockerfile ./gestor-incidentes
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/abcall/abcall/gestor-agentes:latest -f ./gestor-agentes/Dockerfile ./gestor-agentes
```


### 4. Publicar las imagenes en container registry

```shell
docker push us-central1-docker.pkg.dev/abcall/abcall/api-gateway:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/gestor-clientes:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/generacion-reportes:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/gestor-incidentes:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/gestor-fidelizacion:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/vista-360:latest
```

experimento
```shell
docker push us-central1-docker.pkg.dev/abcall/abcall/api-gateway:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/gestor-incidentes:latest
docker push us-central1-docker.pkg.dev/abcall/abcall/gestor-agentes:latest
```

## Creacion de base de datos y red virtual

### 1. Creacion red virtual

```shell
gcloud compute networks create vpn-abcall --project=abcall --subnet-mode=custom --mtu=1460 --bgp-routing-mode=regional
```

### 2. crear subred base de datos
```shell
gcloud compute addresses create red-dbs-abcall --global --purpose=VPC_PEERING --addresses=192.168.0.0 --prefix-length=24 --network=vpn-abcall --project=abcall
```

### 3. Dar permisos 
```shell
gcloud services vpc-peerings connect --service=servicenetworking.googleapis.com --ranges=red-dbs-abcall --network=vpn-abcall --project=abcall
```

### 4. Crear firewall
```shell
gcloud compute firewall-rules create allow-db-ingress --direction=INGRESS --priority=1000 --network=vpn-abcall --action=ALLOW --rules=tcp:5432 --source-ranges=192.168.1.0/24 --target-tags=basesdedatos --project=abcall
```

### 5. Crear base de datos
https://www.coursera.org/learn/desarrollo-de-aplicaciones-nativas-en-la-nube/ungradedWidget/RTHZ1/tutorial-bases-de-datos-en-kubernetes

	Instancia:
		Nombre: abcall-db
		Contraseña: 1234
		Versión: PostgreSQL 14
		Región: us-central1
		Disponibilidad zonal: Única
	
	Maquina y Almacenamiento:
		Tipo de máquina: De núcleo compartido, 1 core y 1.7 GB de RAM
		Almacenamiento 10 GB de HDD
		No habilitar los aumentos automáticos de almacenamiento.
	
	Conexiones:
		Asignación de IP de la instancia: privada (publica si se quiere conectar desde local)
		Red: vpn-abcall
		Rango de IP asignado: red-dbs-abcall
		
	Etiquetas:
		basesdedatos

URI base de atos: "postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@<POSTGRES_HOST>/<POSTGRES_DB>"

Ejemplo: "postgresql+psycopg2://postgres:1234@192.168.0.3/postgres"



## Creacion cluster Kubernetes

### 1. Creacion subred
```shell
gcloud compute networks subnets create red-k8s-abcall --range=192.168.32.0/19 --network=vpn-abcall --region=us-central1 --project=abcall
```

### 2. Creacion cluster
https://www.coursera.org/learn/desarrollo-de-aplicaciones-nativas-en-la-nube/ungradedWidget/jy8Dt/tutorial-hello-kubernetes

	Nombre Kubernetes: abcall-k8s
	Red: vpn-abcall
	Subred del nodo: red-k8s-abcall
	Rango de direcciones del pod: 192.168.64.0/21
	Rango de direcciones del servicio: 192.168.72.0/21

### 3. Conectarse al cluster
```shell
gcloud container clusters get-credentials abcall-k8s --region us-central1 --project abcall
```

- Borrar todo antes por si algo
```shell
kubectl delete all --all -n default
```

- Aplicar secretos si se tiene
```shell
kubectl apply -f deployment/k8s-secrets.yaml
```

- Aplicar deployment servicios (experimento)
```shell
kubectl apply -f deployment/k8s-experimento.yaml
```

- Aplicar Ingress
```shell
kubectl apply -f deployment/k8s-ingress.yaml
```