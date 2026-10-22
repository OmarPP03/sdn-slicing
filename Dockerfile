# Dockerfile to build the kathara/ryu image. Taken from the courses sdn lab practice.

FROM kathara/pox
LABEL org.opencontainers.image.authors="Kathara Team <contact@kathara.org>"

ARG DEBIAN_FRONTEND="noninteractive"
RUN python3.9 -m pip --no-input install setuptools==67.6.1
RUN python3.9 -m pip --no-input install ryu
RUN python3.9 -m pip --no-input install eventlet==0.30.2

RUN apt clean && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*
