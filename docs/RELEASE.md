# Build and release

This repository builds an installer RPM for the Microsoft core fonts. The
font archives are still downloaded by the RPM's post-install script, so an
installation needs network access to the SourceForge mirrors.

## Build the RPM

Requirements:

- Docker with BuildKit support
- Git, for calculating the RPM release number

From the repository root, run:

    make rpm

The command:

1. reads the package version from `VERSION`;
2. calculates the RPM release from the number of commits reachable from
   `HEAD`;
3. builds the RPM and SRPM in a Fedora 43 container;
4. installs the RPM in a disposable Fedora 43 test stage; and
5. verifies the HTTPS mirrors, downloaded fonts, generated font indexes,
   download manifest, and fontconfig registration.

The artifacts are exported to `rpms/`:

    rpms/msttcore-fonts-installer-<version>-<release>.noarch.rpm
    rpms/msttcore-fonts-installer-<version>-<release>.src.rpm

The test downloads the font archives, so it requires network access. The
output directory is cleaned before each build.

## Inspect or install a build

Set the generated filenames with:

    version=$(tr -d '[:space:]' < VERSION)
    release=$(git rev-list --count HEAD)
    rpm_file="rpms/msttcore-fonts-installer-$version-$release.noarch.rpm"
    srpm_file="rpms/msttcore-fonts-installer-$version-$release.src.rpm"

Inspect the packages:

    rpm -qip "$rpm_file"
    rpm -qlp "$rpm_file"
    rpm -qip "$srpm_file"
    rpm -qp --scripts "$rpm_file"

Install the binary RPM only on a disposable or development system:
2.7-1
    sudo rpm -i "$rpm_file"

The post-install script downloads and installs the fonts outside the RPM's
payload tracking. Removing the package cleans up those downloaded font files.

## Prepare a release

1. Update `VERSION` when the package version changes.
2. Update the newest changelog entry in `README` and
   `specs/msttcore-fonts-installer.spec`.
3. Review the source tree under `sources/`, the spec, `builder`, `Makefile`,
   and `tests/test-rpm.sh`.
4. Run `git diff --check` and `make rpm`.
5. Commit the release changes.
6. Run `make rpm` again after committing so the commit count used as the RPM
   release is final.
7. Tag and publish the commit together with both files from `rpms/`.

For example:

    git diff --check
    make rpm
    git add VERSION README docs/RELEASE.md Makefile builder tests specs sources
    git commit -m "Release $(tr -d '[:space:]' < VERSION)"
    make rpm
    git tag -a "v$(tr -d '[:space:]' < VERSION)-$(git rev-list --count HEAD)" \
        -m "msttcore-fonts-installer $(tr -d '[:space:]' < VERSION)"

Do not commit generated files from `rpms/` unless the project policy changes.
