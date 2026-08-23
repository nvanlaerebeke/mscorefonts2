FROM fedora:latest

RUN dnf -y install createrepo_c gnupg2 rpm-sign \
    && dnf clean all \
    && rm -rf /var/cache/dnf

WORKDIR /repo

ENTRYPOINT ["createrepo_c"]
CMD ["--update", "/repo/RPMS"]
