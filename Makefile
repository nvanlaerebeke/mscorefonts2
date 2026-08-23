DOCKER ?= docker
IMAGE ?= mscorefonts-createrepo
RPM_DIR := $(CURDIR)/RPMS

.PHONY: help image repo

help:
	@echo "make image  Build the createrepo container"
	@echo "make repo   Generate or update RPMS/repodata"

image:
	$(DOCKER) build --tag $(IMAGE) .

repo: image
	$(DOCKER) run --rm \
		--user "$$(id -u):$$(id -g)" \
		--volume "$(RPM_DIR):/repo/RPMS" \
		$(IMAGE)
