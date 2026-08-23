CONTAINER_ENGINE ?= docker
IMAGE ?= msttcore-fonts-builder:2.6-1

RPM_DIR := rpms
BINARY_RPM := $(RPM_DIR)/msttcore-fonts-installer-2.7-1.noarch.rpm
SOURCE_RPM := $(RPM_DIR)/msttcore-fonts-installer-2.7-1.src.rpm

.DEFAULT_GOAL := fonts-installer

.PHONY: clean image fonts-installer

image:
	$(CONTAINER_ENGINE) build --tag $(IMAGE) --file builder .

fonts-installer: image
	@set -eu; \
	mkdir -p "$(RPM_DIR)"; \
	container_id="$$( $(CONTAINER_ENGINE) create "$(IMAGE)" )"; \
	trap '$(CONTAINER_ENGINE) rm -f "$$container_id" >/dev/null 2>&1 || true' EXIT INT TERM; \
	$(CONTAINER_ENGINE) cp "$$container_id:/rpms/." "$(RPM_DIR)/"; \
	printf 'Built %s\nBuilt %s\n' "$(BINARY_RPM)" "$(SOURCE_RPM)"

clean:
	rm -f "$(BINARY_RPM)" "$(SOURCE_RPM)"
