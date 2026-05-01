#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

ARG FEDORA_VERSION=latest

## Stage 1: Setup build environment
FROM registry.fedoraproject.org/fedora:${FEDORA_VERSION} AS staging

# Install common build dependencies
RUN dnf install -y \
      autoconf \
      automake \
      gc \
      gcc \
      git \
      glibc-devel \
      glibc-headers \
      koji \
      libtool \
      make \
      ncompress \
      rpm-build \
      rpmspectool \
      rpmdevtools \
      kmodtool \
      which \
      @buildsys-build

# Add koji processing dir
RUN mkdir -p /app/koji

RUN cd /root && rpmdev-setuptree

COPY kernel-add /usr/local/sbin

# Minimize final image size
RUN dnf clean all -y

## Stage 2: Squash generated image layers
FROM scratch
COPY --from=staging / /

# Set default command for container image
CMD /usr/bin/bash
