FROM rockylinux:9 AS builder

RUN dnf -y install \
        cpio \
        rpm-build \
    && dnf clean all

WORKDIR /root/rpmbuild

COPY specs/msttcore-fonts-installer-2.7-1.spec SPECS/
COPY sources/msttcore-fonts-installer-2.7.tar.gz SOURCES/

RUN rpmbuild -ba SPECS/msttcore-fonts-installer-2.7-1.spec

FROM scratch

COPY --from=builder /root/rpmbuild/RPMS/noarch/msttcore-fonts-installer-2.7-1.noarch.rpm /rpms/
COPY --from=builder /root/rpmbuild/SRPMS/msttcore-fonts-installer-2.7-1.src.rpm /rpms/

CMD ["/bin/true"]
