#-------------------------------------------------------------------------------
#
# Dockerfile for building a python3 development container.
#
#-------------------------------------------------------------------------------
FROM photon:3.0

# Variables used for generating the image tag.
ARG REGISTRY=
ARG ORGANIZATION=jaraf
ARG APP_NAME=python3-devel
ARG APP_VERSION=3.7.3
ARG APP_BUILD_NUMBER=1

# Other build variables.
ARG COMMIT_HASH=n/a
ARG MAINTAINER=n/a

# Install everything under the install/ directory to the root of the image.
ADD install /

# Install the application and dependencies and perform cleanup tasks in a
# single RUN step to keep our image footprint as small as possible.
RUN tdnf update -y \
    && tdnf install -y \
    gcc \
    gzip \
    python3-devel \
    python3-pip \
    && pip3 install --upgrade pip \
    && pip install coverage setuptools \
    && pip install sphinx \
    && tdnf clean all \
    && rm -rf /var/cache/tdnf/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# Add some hopefully useful labels.
#
# We use some standard Label Schema attributes defined at:
#     http://label-schema.org/rc1/
#
LABEL \
    maintainer="${MAINTAINER}" \
    org.label-schema.schema-version="1.0.0" \
    org.label-schema.name="${APP_NAME}" \
    org.label-schema.description="Python 3 development image" \
    org.label-schema.vcs-url="" \
    org.label-schema.vcs-ref="${COMMIT_HASH}" \
    org.label-schema.version="${APP_VERSION}"

# Set the default command to print the motd which contains some helpful
# information on how to use the container.
CMD [ "/usr/bin/cat", "/etc/motd" ]
