#!/usr/bin/env make

#-------------------------------------------------------------------------------
#
# Makefile for managing the local project.
#
#-------------------------------------------------------------------------------

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
# Make variables
#
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Default version to use if no tags are found.
default_version = 0.1.0

# Directory containing the Dockerfile. This is used for build steps.
docker_dir = container

# Helper image to use for certain targets.
helper_image = eldr/jaraf:0.1.0-12-gcc3b837
ifneq (, $(shell docker images eldr/jaraf:latest | grep eldr 2> /dev/null))
	helper_image = eldr/jaraf:latest
endif

# Docker registry parameter defaults.
reg_namespace = eldr
reg_repo = jaraf

# URL of the git project. This is currently only used as a build-arg in docker
# build steps to create a label.
repo_url = https://github.com/edlabao/jaraf

# Get the current version tag.
version = $(shell git describe 2> /dev/null || echo $(default_version))

# Set the coverage test command to use for testing.
cov_cmd = coverage3
ifeq (, $(shell which coverage3 2> /dev/null))
	cov_cmd = docker run --rm \
		-v `pwd`/..:/opt/develop \
		-w /opt/develop/coverage \
		$(helper_image) coverage3
endif

# Set the sphinx doc build command to use for testing.
sphinx_cmd = sphinx-build
ifeq (, $(shell which sphinx-build 2> /dev/null))
	sphinx_cmd = docker run --rm \
		-v `pwd`:/opt/develop \
		-w /opt/develop \
		$(helper_image) sphinx-build
endif

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
# Targets
#
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Print out help text by parsing for targets in the current Makefile and also
# one in a cicd subdirectory (which will be this file if we are being called
# with an include).
#
# Discard targets that start with "." or "help".
#
help:
	@echo ""
	@echo "Make targets:"
	@grep -E "^[^\.]\S+:" Makefile \
		| cut -d: -f1 \
		| grep -Ev -e "^help" -e "^#" \
		| sort \
		| awk '{printf "    %s\n", $$1}'
	@test -f cicd/Makefile && grep -E "^[^\.]\S+:" cicd/Makefile \
		| cut -d: -f1 \
		| grep -Ev -e "^help" -e "^#" \
		| sort \
		| awk '{printf "    %s\n", $$1}' \
		|| /usr/bin/true
	@echo ""

# Build the container image.
package:
	@mkdir -p container/install/tmp \
		&& cp -r README.md python container/install/tmp \
		&& sed -ie "s/^VERSION =.*/VERSION = \"$(shell cat ./VERSION)\"/g" container/install/tmp/python/jaraf/version.py \
		&& cd $(docker_dir) \
		&& docker build \
			--build-arg APP_NAME=jaraf \
			--build-arg APP_VERSION=$(version) \
			--build-arg GIT_REF= \
			--build-arg GIT_URL=$(repo_url) \
			-t $(reg_namespace)/$(reg_repo):$(version) . \
		&& docker tag $(reg_namespace)/$(reg_repo):$(version) \
			$(reg_namespace)/$(reg_repo):latest

# Clean up generated files. This includes files we copied into the docker
# install directory and python bytecode.
clean:
	@find python -depth -name "*__pycache__" -exec rm -rf {} \;
	@find python -name "*.pyc" -exec rm -f {} \;
	@rm -rf container/install/tmp \
		coverage docs/html \
		python/LICENSE \
		python/README.md \
		python/build \
		python/dist

# Genereate the sphinx documentation.
docs:
	@mkdir -p docs/html
	$(sphinx_cmd) -E -j 4 docs/sphinx docs/html

# Run an interactive docker session for development and testing.
exec:
	@docker run -it --rm \
		--name codaml-dev \
		-v `pwd`:/opt/develop \
		-w /opt/develop \
		$(helper_image) bash

# Create and upload the jaraf package to pypi.
publish:
	cp LICENSE README.md python
	cd python \
		&& python3 setup.py sdist bdist_wheel \
		&& twine upload dist/*

# Run unittests and generate a coverage report.
test:
	@mkdir -p coverage html/coverage
	@cd coverage \
		&& $(cov_cmd) run -a \
			--branch \
			--omit "*/unittest/*" \
			../python/jaraf/unittest/TestAll.py \
		&& $(cov_cmd) run -a \
			--branch \
			--omit "*/unittest/*" \
			../python/jaraf/mixin/unittest/TestAll.py \
		&& $(cov_cmd) html -d ../docs/html/coverage \
		&& $(cov_cmd) report -m

.PHONY: docs