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
ifneq (, $(shell docker images eldr/jaraf:latest 2> /dev/null | grep eldr 2> /dev/null))
	helper_image = eldr/jaraf:latest
endif

# Docker registry parameter defaults.
reg_namespace = eldr
reg_repo = jaraf

# URL of the git project. This is currently only used as a build-arg in docker
# build steps to create a label.
repo_url = https://github.com/edlabao/jaraf

# The branch to release from.
release_branch = master

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
	sphinx_cmd = docker run \
	    --rm \
		-v `pwd`:/opt/develop \
		-w /opt/develop \
		$(helper_image) sphinx-build
endif

# Set the twine upload command to use for publishing new versions to pypi.
twine_cmd = twine
ifeq (, $(shell which twine 2> /dev/null))
	twine_cmd = docker run \
	    --rm \
	    -it \
		-v `pwd`:/opt/develop \
		-w /opt/develop \
		$(helper_image) twine
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

# Increment the version number
bump-major: .bump-major
bump-minor: .bump-minor
bump-patch: .bump-patch

bump-major bump-minor bump-patch:
	@echo $(version) > VERSION \
	&& sed -e "s/^VERSION =.*/VERSION = \"$(version)\"/g" -i "" python/jaraf/version.py

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
		python/dist \
		python/jaraf.egg-info

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

# Build the container image.
package:
	@mkdir -p container/install/tmp \
		&& cp -r README.md python container/install/tmp \
		&& cd $(docker_dir) \
		&& docker build \
			--build-arg APP_NAME=jaraf \
			--build-arg APP_VERSION=$(version) \
			--build-arg GIT_REF= \
			--build-arg GIT_URL=$(repo_url) \
			-t $(reg_namespace)/$(reg_repo):$(version) . \
		&& docker tag $(reg_namespace)/$(reg_repo):$(version) \
			$(reg_namespace)/$(reg_repo):latest

# Release a new version.
release:
	$(eval branch_name = $(shell git rev-parse --abbrev-ref HEAD))
	@echo "Current branch is '$(branch_name)'."
	@cp LICENSE README.md python
	@if [ $(branch_name) = $(release_branch) ]; \
		then \
			cd python \
				&& python3 setup.py sdist bdist_wheel \
				&& $(twine_cmd) upload dist/* 2> /dev/null; \
		else \
			echo "You must be on the '$(release_branch)' branch to release a new version."; \
			/usr/bin/false; \
		fi

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


# Increment the major version.
.bump-major: .version
	$(eval new_major_vers = $(shell echo $$(($(major_vers)+1))))
	$(eval version = $(new_major_vers).0.0)

# Increment the minor version.
.bump-minor: .version
	$(eval new_minor_vers = $(shell echo $$(($(minor_vers)+1))))
	$(eval version = $(major_vers).$(new_minor_vers).0)

# Increment the patch version.
.bump-patch: .version
	$(eval new_patch_vers = $(shell echo $$(($(patch_vers)+1))))
	$(eval version = $(major_vers).$(minor_vers).$(new_patch_vers))

# Break the version number into its semantic parts.
.version:
	$(eval major_vers = $(shell cut -d. -f1 VERSION))
	$(eval minor_vers = $(shell cut -d. -f2 VERSION))
	$(eval patch_vers = $(shell cut -d. -f3 VERSION))

.PHONY: docs