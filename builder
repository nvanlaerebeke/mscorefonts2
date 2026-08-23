#Build the RPM
FROM fedora:43 AS rpm-builder

ARG PKG_VERSION
ARG PKG_RELEASE

RUN dnf -y install \
        cpio \
        rpm-build \
    && dnf clean all

WORKDIR /root/rpmbuild

COPY specs/msttcore-fonts-installer.spec SPECS/
COPY sources/ /tmp/sources/

RUN test -n "$PKG_VERSION" \
    && test -n "$PKG_RELEASE" \
    && mkdir -p SOURCES \
    && mkdir -p /tmp/source-tree/msttcore-fonts-installer \
    && cp -a /tmp/sources/. /tmp/source-tree/msttcore-fonts-installer/ \
    && tar -cf SOURCES/msttcore-fonts-installer.tar \
        -C /tmp/source-tree msttcore-fonts-installer \
    && rpmbuild -ba \
        --define "pkg_version ${PKG_VERSION}" \
        --define "pkg_release ${PKG_RELEASE}" \
        SPECS/msttcore-fonts-installer.spec

# Test the freshly built RPM. This stage is an ancestor of artifacts, so the
# test runs whenever the artifact target is built.
FROM fedora:43 AS rpm-test
COPY --from=rpm-builder /root/rpmbuild/RPMS/noarch/ /rpms/
COPY tests/test-rpm.sh /usr/local/bin/test-rpm

RUN rpm_path="$(find /rpms -maxdepth 1 -type f -name '*.rpm' -print -quit)" \
    && test -n "$rpm_path" \
    && /usr/local/bin/test-rpm "$rpm_path"

# Copy ARTIFACTS back to the host
FROM scratch AS artifacts
COPY --from=rpm-test /rpms/ /rpms/
COPY --from=rpm-builder /root/rpmbuild/SRPMS/ /rpms/

CMD ["/bin/true"]
