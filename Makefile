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
helper_image = eldr/jaraf:0.1.0

# Docker registry parameter defaults.
reg_namespace = eldr
reg_repo = jaraf

# URL of the git project. This is currently only used as a build-arg in docker
# build steps to create a label.
repo_url = https://github.com/edlabao/jaraf

# Get the current version tag.
version = $(shell git describe >& /dev/null || echo $(default_version))


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

# Clean up generated files. This includes files we copied into the docker
# install directory and python bytecode.
clean:
	@find python -depth -name "*__pycache__" -exec rm -rf {} \;
	@find python -name "*.pyc" -exec rm -f {} \;

# Run an interactive docker session for development and testing.
# For macs, we need to pass in extra dns options to resolve the coda mongodb
# servers.
exec:
	@docker run -it --rm \
		--name codaml-dev \
		-v `pwd`:/opt/develop \
		-w /opt/develop \
		$(helper_image) bash

#
# Package the application into a docker image.
#
package:
	cd $(docker_dir) \
	&& docker build \
		--build-arg APP_NAME=jaraf \
		--build-arg APP_VERSION=$(version) \
		--build-arg GIT_REF= \
		--build-arg GIT_URL=$(repo_url) \
		-t $(reg_namespace)/$(reg_repo):$(version) .
