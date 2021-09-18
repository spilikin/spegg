# build and deploy to Kubernetes

STAGE := dev
# include a file providing your (private) settings as variables
#
include Make-settings.private
IMAGE_TAG := "0.0.1"
DATA_DIR := "../data"
BUILD_DIR := $(shell pwd)
MONGODB_DB := "spegg"
MONGODB_USER := "speggu"

default: .helm-deploy.make

docker-build: .docker-build.make

docker-push: .docker-push.make

.ONESHELL:
.docker-build.make: ../.globex/*.yaml
	$(info "building docker images")
	cd ../.globex/
	docker-compose build
	docker tag globex_spegg-vue:latest $(DOCKER_REGISTRY)/globex_spegg-vue:$(IMAGE_TAG)
	docker tag globex_spegg-api:latest $(DOCKER_REGISTRY)/globex_spegg-api:$(IMAGE_TAG)
	cd $(BUILD_DIR)
	touch .docker-build.make

.docker-push.make: .docker-build.make
	$(info doing docker push to $(DOCKER_REGISTRY))
	docker push $(DOCKER_REGISTRY)/globex_spegg-vue:$(IMAGE_TAG)
	docker push $(DOCKER_REGISTRY)/globex_spegg-api:$(IMAGE_TAG)
	touch .docker-push.make

.helm-deploy.make: .docker-push.make
	$(info deploying to k8s)
	kubectl config use-context gke_gematik-all-k8s-db-$(STAGE)_europe-west3-a_shared-k8s-$(STAGE)
	kubectl config set-context --current --namespace=${K8S_NAMESPACE}
	helm dep up spegg
	helm upgrade $(STAGE) spegg \
			--install \
			--namespace=$(K8S_NAMESPACE) \
			--set stage=$(STAGE) \
			--set api.image.repository=$(DOCKER_REGISTRY)/globex_spegg-api \
			--set api.image.tag=$(IMAGE_TAG) \
			--set api.env.mongodbUsername=$(MONGODB_USER) \
			--set api.env.mongodbPassword=$(MONGODB_PASSWORD) \
			--set api.env.mongodbHost=$(STAGE)-mongodb \
			--set vue.image.repository=$(DOCKER_REGISTRY)/globex_spegg-vue \
			--set vue.image.tag=$(IMAGE_TAG) \
			--set mongodb.auth.rootPassword=$(MONGODB_ROOT_PASSWORD) \
			--set mongodb.auth.username=$(MONGODB_USER) \
			--set mongodb.auth.password=$(MONGODB_PASSWORD) \
			--set mongodb.auth.database=$(MONGODB_DB) \
			--set ingress.domain="thomasdonath.com" \
			--set ingress.publicIpName="spegg-dev"  			               	          # --debug

:ONESHELL:
db-import:
	MONGODB_POD=$$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=mongodb,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}")
	for collection in 'Resource' 'ResourceVersion' 'Subject' 'SubjectVersion'
	do
	echo
		gunzip -c $(DATA_DIR)/$${collection}.json.gz | \
		kubectl exec -i $${MONGODB_POD} -- bash -c "mongoimport -u \$${MONGODB_USERNAME} -p \$${MONGODB_PASSWORD} --authenticationDatabase \$${MONGODB_DATABASE} --db=\$${MONGODB_DATABASE} --collection=$${collection}"
	done

api-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=api,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 8080:80

vue-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=vue,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 8088:80

db-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=mongodb,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 27017:27017


.gcloud:
	$(GCLOUD_K8S)


