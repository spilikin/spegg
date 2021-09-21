# build and deploy to Kubernetes

STAGE := dev
# include a file providing your (private) settings as variables per stage
#
include Make-settings.$(STAGE).private
include Make-settings.$(STAGE)
DATA_DIR := "../data"
BUILD_DIR := $(shell pwd)

default deploy: .helm-deploy.$(STAGE).make

docker-build: .docker-build.$(STAGE).make

docker-push: .docker-push.$(STAGE).make

.ONESHELL:
.docker-build.$(STAGE).make: ../.globex/*.yaml
	$(info "building docker images")
	cd ../.globex/
	docker-compose build
	docker tag globex_spegg-vue:latest $(DOCKER_REGISTRY)/globex_spegg-vue:$(IMAGE_TAG)
	docker tag globex_spegg-api:latest $(DOCKER_REGISTRY)/globex_spegg-api:$(IMAGE_TAG)
	cd $(BUILD_DIR)
	touch .docker-build.$(STAGE).make

.docker-push.$(STAGE).make: .docker-build.$(STAGE).make
	$(info doing docker push to $(DOCKER_REGISTRY))
	docker push $(DOCKER_REGISTRY)/globex_spegg-vue:$(IMAGE_TAG)
	docker push $(DOCKER_REGISTRY)/globex_spegg-api:$(IMAGE_TAG)
	touch .docker-push.$(STAGE).make

.helm-deploy.$(STAGE).make: .docker-push.$(STAGE).make
	$(info deploying to k8s)
	kubectl config use-context $(K8S_CONTEXT)
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
			--set api.env.mongodbHost=$(MONGODB_HOST)  \
			--set vue.image.repository=$(DOCKER_REGISTRY)/globex_spegg-vue \
			--set vue.image.tag=$(IMAGE_TAG) \
			--set mongodb.auth.rootPassword=$(MONGODB_ROOT_PASSWORD) \
			--set mongodb.auth.username=$(MONGODB_USER) \
			--set mongodb.auth.password=$(MONGODB_PASSWORD) \
			--set mongodb.auth.database=$(MONGODB_DB) \
			--set ingress.domain=$(INGRESS_DOMAIN)  \
			--set ingress.publicIpName=$(PUBLIC_IP_NAME)   			               	          # --debug

:ONESHELL:
db-import:
	$(info loading data)
	MONGODB_POD=$$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=mongodb,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}")
	for collection in 'Resource' 'ResourceVersion' 'Subject' 'SubjectVersion'
	do
	echo
		gunzip -c $(DATA_DIR)/$${collection}.json.gz | \
		kubectl exec -i $${MONGODB_POD} -- bash -c "mongoimport -u \$${MONGODB_USERNAME} -p \$${MONGODB_PASSWORD} --authenticationDatabase \$${MONGODB_DATABASE} --db=\$${MONGODB_DATABASE} --collection=$${collection}"
	done

uninstall:
	$(info uninstalling using helm)
	kubectl config use-context $(K8S_CONTEXT)
	kubectl config set-context --current --namespace=${K8S_NAMESPACE}
	helm uninstall $(STAGE)

api-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=api,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 8080:80

vue-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=vue,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 8088:80

db-proxy:
	kubectl -n $(K8S_NAMESPACE) port-forward $$(kubectl get pod -n $(K8S_NAMESPACE) -l "app.kubernetes.io/name=mongodb,app.kubernetes.io/instance=dev" -o jsonpath="{.items[0].metadata.name}") 27017:27017

clean:
	rm -f .*.$(STAGE).make

unclean:
	touch .docker-build.$(STAGE).make .docker-push.$(STAGE).make

.gcloud:
	$(GCLOUD_K8S)
