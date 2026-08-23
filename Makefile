DOCKER ?= docker
IMAGE ?= mscorefonts-createrepo
RPM_DIR := $(CURDIR)/RPMS
GPG_KEY ?=
GPG_HOME ?= $(shell gpgconf --list-dirs homedir 2>/dev/null)
GPG_AGENT_SOCKET ?= $(shell gpgconf --list-dirs agent-socket 2>/dev/null)

.PHONY: help image repo sign export-key sign-repomd

help:
	@echo "make image  Build the createrepo container"
	@echo "make repo   Generate or update RPMS/repodata"
	@echo "make sign   Sign all RPMs, then regenerate metadata"
	@echo "make export-key  Export the public signing key"
	@echo "make sign-repomd  Sign metadata and export the public key"

image:
	$(DOCKER) build --tag $(IMAGE) .

repo: image
	$(DOCKER) run --rm \
		--user "$$(id -u):$$(id -g)" \
		--volume "$(RPM_DIR):/repo/RPMS" \
		$(IMAGE)

sign:
	@test -n "$(GPG_KEY)" || (echo "GPG_KEY is required, e.g. make sign GPG_KEY=ABCDEF1234567890" >&2; exit 1)
	test -d "$(GPG_HOME)" || (echo "GPG_HOME does not exist: $(GPG_HOME)" >&2; exit 1)
	test -S "$(GPG_AGENT_SOCKET)" || (echo "GPG agent socket does not exist: $(GPG_AGENT_SOCKET)" >&2; exit 1)
	$(MAKE) image
	$(DOCKER) run --rm \
		--interactive --tty \
		--user "$$(id -u):$$(id -g)" \
		--env GNUPGHOME=/gnupg \
		--volume "$(GPG_HOME):/gnupg" \
		--volume "$(GPG_AGENT_SOCKET):/gnupg/S.gpg-agent" \
		--volume "$(RPM_DIR):/repo/RPMS" \
		--entrypoint /bin/sh \
		$(IMAGE) -c 'exec rpmsign --addsign --key-id "$(GPG_KEY)" /repo/RPMS/*.rpm'
	$(MAKE) repo

export-key:
	@test -n "$(GPG_KEY)" || (echo "GPG_KEY is required, e.g. make export-key GPG_KEY=ABCDEF1234567890" >&2; exit 1)
	gpg --armor --export "$(GPG_KEY)" > RPM-GPG-KEY-mscorefonts.asc

sign-repomd: sign
	$(MAKE) export-key GPG_KEY="$(GPG_KEY)"
	gpg --armor --batch --yes --local-user "$(GPG_KEY)" --detach-sign RPMS/repodata/repomd.xml
