#------------------------------------------------------------------------------
#
# python2-develop
#
# This builds a docker suitable for python 2.7 development. We can install
# third-party packages into this image rather than modifying the local system's
# python installation directly.
#
# To build:
#   docker build -t python2-develop .
#
# To run:
#   docker run -it --rm -v `pwd`:/opt/develop python2-develop
# This starts a python2-develop container that mounts the current directory to
# its /opt/develop path.
#
# To run the sphinx auto-generator inside the container, cd to the directory
# containing the sphinx .rst files and run:
#   sphinx-autobuild . ../html
#
#------------------------------------------------------------------------------

##
## Define the base image to use.
##
FROM centos:7

##
## Define variables used throughout.
##
ARG _GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py
ARG _GET_PIP_SCRIPT=./get-pip.py

##
## Install the pip installer and then install the following python packages:
##   coverage
##   flask
##   flask-migrate
##   flask-restplus
##   flask-sqlalchemy
##   flask-wtf
##   sphinx
##   sphinx-autobuild
##   sphinx_rtd_theme
##
RUN mkdir /opt/develop \
    && cd /opt/develop \
    && curl -O ${_GET_PIP_URL} \
    && python ${_GET_PIP_SCRIPT} \
    && pip install coverage \
    && pip install flask \
    && pip install flask-login \
    && pip install flask-migrate \
    && pip install flask-restplus \
    && pip install flask-sqlalchemy \
    && pip install flask-wtf \
    && pip install sphinx \
    && pip install sphinx-autobuild \
    && pip install sphinx_rtd_theme \
    && rm -f ${_GET_PIP_SCRIPT}


##
## The default directory should be /opt/develop. Under here, we can mount
## externa directories containing source code.
##
WORKDIR /opt/develop
