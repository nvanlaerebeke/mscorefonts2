# mscorefonts RPM repository

This branch is a static RPM repository intended to be published with GitHub
Pages. The packages are in [`RPMS/`](RPMS/) and the repository metadata is in
`RPMS/repodata/`.

## Regenerate repository metadata

Docker is the only local dependency needed to generate the metadata:

```sh
make repo
```

The command builds the `createrepo_c` image and runs it with `RPMS/` mounted
into the container. Commit the resulting `RPMS/repodata/` changes together
with any added or removed RPMs.

To use a different Docker-compatible runtime or image name:

```sh
make repo DOCKER=podman IMAGE=my-createrepo
```

## Configure a client

After enabling GitHub Pages for this branch, use the repository URL as the
base URL in a `.repo` file:

```ini
[mscorefonts]
name=mscorefonts
baseurl=https://OWNER.github.io/REPOSITORY/RPMS/
enabled=1
gpgcheck=0
```

Replace `OWNER` and `REPOSITORY` with the GitHub account and repository name.
