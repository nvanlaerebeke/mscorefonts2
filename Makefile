VERSION := $(strip $(shell cat VERSION))
RELEASE := $(strip $(shell git rev-list --count HEAD))

RPM_DIR := rpms
SPEC_FILE := specs/msttcore-fonts-installer.spec
BINARY_RPM := $(RPM_DIR)/msttcore-fonts-installer-$(VERSION)-$(RELEASE).noarch.rpm
SOURCE_RPM := $(RPM_DIR)/msttcore-fonts-installer-$(VERSION)-$(RELEASE).src.rpm

.DEFAULT_GOAL := rpm

.PHONY: clean rpm

rpm: clean
	test -f "$(SPEC_FILE)"
	mkdir -p "$(RPM_DIR)"
	docker build \
		--build-arg PKG_VERSION="$(VERSION)" \
		--build-arg PKG_RELEASE="$(RELEASE)" \
		--target artifacts \
		--output type=local,dest=. \
		--file builder .
	printf 'Built %s\nBuilt %s\n' "$(BINARY_RPM)" "$(SOURCE_RPM)"

clean:
	@set -eu; \
	if [ -z "$(RPM_DIR)" ] || [ "$(RPM_DIR)" = "/" ]; then \
		echo "Refusing to clean an empty or root RPM directory" >&2; \
		exit 1; \
	fi; \
	rm -rf "$(RPM_DIR)"/*
