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

## Sign the repository

The repository uses GPG signatures for both RPM packages and repository
metadata. Keep the private key outside this repository.

### Without a YubiKey

If you are not using a hardware key, create a local signing key and record its
long key ID:

```sh
gpg --quick-generate-key "mscorefonts RPM Repository" rsa4096 sign 2y
gpg --list-secret-keys --keyid-format=long
```

### Set up a YubiKey for GPG signing on Ubuntu 26.04

Use the YubiKey's **OpenPGP** application for GPG signing, not its PIV application.

A YubiKey can use multiple applications independently, so using the PIV application for other purposes does not prevent using OpenPGP for GPG signing.

Reference:

https://docs.yubico.com/hardware/yubikey/yk-tech-manual/yk5-apps-openpgp.html

#### Install the required packages

Install GnuPG, smart-card support, PC/SC, and the YubiKey management tools:

```sh
sudo apt install gnupg pcscd scdaemon pcsc-tools yubikey-manager
```

Enable and start `pcscd`:

```sh
sudo systemctl enable --now pcscd
```

#### Configure GnuPG smart-card access

On Ubuntu 26.04, GnuPG may fail to detect the YubiKey with an error such as:

```text
gpg: selecting card failed: No such device
gpg: OpenPGP card not available: No such device
```

Configure `scdaemon` to use PC/SC instead of directly accessing the YubiKey through its internal CCID driver.

Create the GnuPG configuration directory if it does not already exist:

```sh
mkdir -p ~/.gnupg
chmod 700 ~/.gnupg
```

Create:

```text
~/.gnupg/scdaemon.conf
```

with the following contents:

```text
disable-ccid
```

The options have the following purpose:

* `disable-ccid` makes `scdaemon` access the YubiKey through `pcscd` instead of attempting to use its own CCID driver.

Do not add `pcsc-shared` here with the current Ubuntu/GnuPG setup. It can
prevent PIN retention in GnuPG 2.4.x, causing a PIN prompt for every
signature. If another application needs simultaneous access to the card, this
is a trade-off that must be evaluated separately.

Restart GnuPG's smart-card components:

```sh
gpgconf --kill scdaemon
gpgconf --kill gpg-agent
sudo systemctl restart pcscd
```

Unplug and reconnect the YubiKey if necessary.

#### Verify that the YubiKey is detected

First verify that the YubiKey itself is visible:

```sh
ykman list
```

Check that the OpenPGP application is enabled:

```sh
ykman info
```

The output should show:

```text
OpenPGP          Enabled
```

If OpenPGP is disabled, enable it:

```sh
ykman config usb --enable OPENPGP
```

Then unplug and reconnect the YubiKey.

Optionally verify that PC/SC can see the smart card:

```sh
pcsc_scan
```

Press `Ctrl+C` to exit after the YubiKey has been detected.

Finally, verify that GnuPG sees the OpenPGP card:

```sh
gpg --card-status
```

You should now see the YubiKey's OpenPGP card information.

#### Generate the signing key

From the administrative `gpg --card-edit` prompt, to enter admin mode, type:

```text
admin
```

Now generate the signing key

```text
generate
```

Follow the prompts to generate the OpenPGP key directly on the YubiKey.

The private key operations are performed by the YubiKey.  
The private key itself is not copied into the Git repository, build environment, or Docker image.

After generation, leave the card editor:

```text
quit
```

## Find the signing key ID

List the available secret keys:

```sh
gpg --list-secret-keys --keyid-format=long
```

Identify the long key ID for the key associated with the YubiKey.

For example:

```sh
KEY_ID=0123456789ABCDEF
```

## Test signing

Create a temporary test file and sign it:

```sh
tmpdir=$(mktemp -d)

printf 'mscorefonts signing test\n' > "$tmpdir/test"

gpg \
    --local-user "$KEY_ID" \
    --detach-sign \
    --armor \
    "$tmpdir/test"
```

Verify the signature:

```sh
gpg --verify "$tmpdir/test.asc" "$tmpdir/test"
```

Then remove the temporary files:

```sh
rm -rf "$tmpdir"
```

During signing, GnuPG may ask for the OpenPGP user PIN.

If a touch policy is configured for the signing key, touch the YubiKey when it starts blinking.

## Export the public key

Only the public key needs to be distributed to systems that verify the RPM packages.

Export it with:

```sh
gpg --armor --export "$KEY_ID" > RPM-GPG-KEY-mscorefonts.asc
```

The private key must never be exported or committed.

## Sign the RPM repository

RPM packages must be signed with `rpmsign`, which adds the package signature to
the RPM header. The Makefile runs `rpmsign` in the same Docker image used for
repository generation, while forwarding the host GPG home directory and agent
socket. It then runs `createrepo_c` in Docker to regenerate the repository
metadata from the signed packages, and finally signs `repomd.xml` with `gpg` on
the host.

Run:

```sh
make sign-repomd GPG_KEY="$KEY_ID"
```

The steps run in this order:

1. Sign all RPM packages in the signing container with `rpmsign`.
2. Regenerate `RPMS/repodata/` with Docker.
3. Export the public key and create the detached signature for `repomd.xml`.

When requested during RPM or metadata signing:

1. Enter the YubiKey OpenPGP PIN.
2. Touch the YubiKey if its signing touch policy requires it.

The signing process creates or updates:

```text
RPM-GPG-KEY-mscorefonts.asc
RPMS/repodata/repomd.xml.asc
```

It also signs the RPM packages and regenerates the repository metadata.

Commit:

* The signed RPM packages
* `RPM-GPG-KEY-mscorefonts.asc`
* `RPMS/repodata/repomd.xml.asc`
* The updated `RPMS/repodata/` directory

Do **not** commit:

* Private GPG keys
* The contents of `~/.gnupg`
* YubiKey PINs
* GPG agent sockets

For additional information about the GnuPG smart-card commands, see:

https://gnupg.org/documentation/manuals/gnupg/gpg_002dcard.html


## Publish with GitHub Pages

Push this branch to GitHub, then open the repository's **Settings → Pages**:

1. Under **Build and deployment**, choose **Deploy from a branch**.
2. Select the `pages` branch and the `/ (root)` folder.
3. Click **Save**.

For this repository, the expected Pages URL is:

<https://nvanlaerebeke.github.io/mscorefonts2/>

The RPM repository itself is published below `RPMS/`:

<https://nvanlaerebeke.github.io/mscorefonts2/RPMS/>

GitHub may take a short time to publish the branch. A custom domain, if one
is configured later, will replace these URLs.

## Configure a client

On a Fedora, RHEL, CentOS, Rocky, or AlmaLinux system, create
`/etc/yum.repos.d/mscorefonts.repo` as root:

```ini
[mscorefonts]
name=mscorefonts
baseurl=https://nvanlaerebeke.github.io/mscorefonts2/RPMS/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://nvanlaerebeke.github.io/mscorefonts2/RPM-GPG-KEY-mscorefonts.asc
```

Then refresh the metadata and install the package:

```sh
sudo dnf clean metadata
sudo dnf makecache
sudo dnf install msttcore-fonts-installer
```

Older systems using `yum` can use the same `.repo` file and replace `dnf`
with `yum`.

The `gpgkey` URL is the public key used to verify both package and repository
metadata signatures. The repository must be published with the signing
artifacts from `make sign-repomd` before clients can use this configuration.
