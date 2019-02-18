#
#  Author: Hari Sekhon
#  Date: 2013-01-06 15:45:00 +0000 (Sun, 06 Jan 2013)
#
#  https://github.com/harisekhon/devops-python-tools
#
#  License: see accompanying LICENSE file
#
#  https://www.linkedin.com/in/harisekhon
#

# Travis has custom python install earlier in $PATH even in Perl builds so need to install PyPI modules to non-system python otherwise they're not found by programs.
# Better than modifying $PATH to put /usr/bin first which is likely to affect many other things including potentially not finding the perlbrew installation first
#ifneq '$(VIRTUAL_ENV)$(CONDA_DEFAULT_ENV)$(TRAVIS)' ''
# Looks like Perl travis builds are now using system Python - do not use TRAVIS env var

SUDO     := sudo -H
SUDO_PIP := sudo -H

ifdef VIRTUAL_ENV
	# breaks as command before first target
	#$(info VIRTUAL_ENV environment variable detected, not using sudo)
	SUDO_PIP :=
endif
ifdef CONDA_DEFAULT_ENV
	#$(info CONDA_DEFAULT_ENV environment variable detected, not using sudo)
	SUDO_PIP :=
endif

# must come after to reset SUDO_PIP to blank if root
# EUID /  UID not exported in Make
# USER not populated in Docker
ifeq '$(shell id -u)' '0'
	SUDO =
	SUDO_PIP =
endif

# ===================
# bootstrap commands:

# Alpine:
#
#   apk add --no-cache git make && git clone https://github.com/harisekhon/pylib && cd pylib && make

# Debian / Ubuntu:
#
#   apt-get update && apt-get install -y make git && git clone https://github.com/harisekhon/pylib && cd pylib && make

# RHEL / CentOS:
#
#   yum install -y make git && git clone https://github.com/harisekhon/pylib && cd pylib && make

# ===================

.PHONY: build
build:
	@echo ================
	@echo Python Lib Build
	@echo ================

	git submodule init
	git submodule update --recursive

	make system-packages

	python -V

	which pip || $(SUDO) easy_install pip || :

	pip -V

	git update-index --assume-unchanged resources/custom_tlds.txt
	
	# fixes bug in cffi version detection when installing requests-kerberos
	$(SUDO_PIP) pip install --upgrade pip

	# only install pip packages not installed via system packages
	#$(SUDO_PIP) pip install --upgrade -r requirements.txt
	#$(SUDO_PIP) pip install -r requirements.txt
	@bash-tools/python_pip_install_if_absent.sh requirements.txt

	# prevents https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
	$(SUDO_PIP) pip install --upgrade ndg-httpsclient || $(SUDO_PIP) pip install --upgrade ndg-httpsclient

	# Python 2.4 - 2.6 backports
	#$(SUDO_PIP) pip install argparse
	#$(SUDO_PIP) pip install unittest2

	# PyLint breaks in Python 2.6
	#if [ "$$(python -c 'import sys; sys.path.append("pylib"); import harisekhon; print(harisekhon.utils.getPythonVersion())')" = "2.6" ]; then $(SUDO_PIP) pip uninstall -y pylint; fi

	@echo
	bash-tools/python_compile.sh
	@echo
	@echo 'BUILD SUCCESSFUL (pylib)'
	@echo
	@echo

.PHONY: quick
quick:
	QUICK=1 $(MAKE)

.PHONY: system-packages
system-packages:
	if [ -x /sbin/apk ];        then $(MAKE) apk-packages; fi
	if [ -x /usr/bin/apt-get -a "$$CI_NAME" != "codeship" ]; then $(MAKE) apt-packages; fi
	if [ -x /usr/bin/yum ];     then $(MAKE) yum-packages; fi

.PHONY: apk-packages
apk-packages:
	bash-tools/apk-install-packages.sh setup/apk-packages.txt setup/apk-packages-dev.txt
	NO_FAIL=1 NO_UPDATE=1 bash-tools/apk-install-packages.sh setup/apk-packages-pip.txt
	# Spark Java Py4J gets java linking error without this
	if [ -f /lib/libc.musl-x86_64.so.1 ]; then [ -e /lib/ld-linux-x86-64.so.2 ] || ln -sv /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2; fi

.PHONY: apk-packages-remove
apk-packages-remove:
	$(SUDO) apk del `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/apk-packages-dev.txt` || :
	$(SUDO) rm -fr /var/cache/apk/*

.PHONY: apt-packages
apt-packages:
	bash-tools/apt-install-packages.sh setup/deb-packages.txt setup/deb-packages-dev.txt
	NO_FAIL=1 NO_UPDATE=1 bash-tools/apt-install-packages.sh setup/deb-packages-pip.txt

.PHONY: apt-packages-remove
apt-packages-remove:
	$(SUDO) apt-get purge -y `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/deb-packages-dev.txt`

.PHONY: yum-packages
yum-packages:
	bash-tools/install_epel_repo.sh
	bash-tools/yum-install-packages.sh setup/rpm-packages.txt setup/rpm-packages-dev.txt
	NO_FAIL=1 bash-tools/yum-install-packages.sh setup/rpm-packages-pip.txt

.PHONY: yum-packages-remove
yum-packages-remove:
	for x in `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/rpm-packages-dev.txt`; do rpm -q $$x && $(SUDO) yum remove -y $$x; done

.PHONY: sonar
sonar:
	sonar-scanner

.PHONY: test-common
test-common:
	tests/all.sh
	# temporary workaround for pytest finding these files and breaking with error:
	# import file mismatch:
	# imported module 'test.test_utils' has this __file__ attribute:
	#   /home/travis/build/HariSekhon/pylib/bash-tools/pytools_checks/pylib/test/test_utils.py
	# which is not the same as the test file we want to collect:
	#   /home/travis/build/HariSekhon/pylib/test/test_utils.py
	# HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
	#rm -fr bash-tools/pytools_checks

.PHONY: test
test: test-common
	#python test/test_HariSekhonUtils.py
	# find all unit tests under test/
	# Python -m >= 2.7
	#python -m unittest discover -v
	#unit2 discover -v
	# Alpine fails to find 'blessings' module because now defaults to Python 3 but modules are installed to Python 2
	if type nosetests-2.7 2>/dev/null; then \
		nosetests-2.7; \
	else \
		nosetests; \
	fi
	# try pytest-2 first for Alpine, otherwise normal pytest which defaults to Python 3
	# On CentOS it's called py.test
	#if type pytest-2 2>/dev/null; then \
	#	pytest-2; \
	#elif type py.test-2 2>/dev/null; then \
	#	py.test-2; \
	#elif type py.test 2>/dev/null; then \
	#	py.test; \
	#else \
	#	pytest; \
	#fi

.PHONY: test2
test2: test-common
	python -m unittest discover -v

.PHONY: install
install:
	@echo "No installation needed, just add '$(PWD)' to your \$$PATH"

.PHONY: update
update:
	git pull
	git submodule update --init --recursive
	$(MAKE)

.PHONY: update2
update2:
	$(MAKE) update-no-recompile

.PHONY: update-no-recompile
update-no-recompile:
	git pull
	git submodule update --init --recursive

.PHONY: update-submodules
update-submodules:
	git submodule update --init --remote
.PHONY: updatem
updatem: update-submodules
	:

.PHONY: tld
tld:
	wget -t 100 --retry-connrefused -O resources/tlds-alpha-by-domain.txt http://data.iana.org/TLD/tlds-alpha-by-domain.txt

.PHONY: clean
clean:
	@# the xargs option to ignore blank input doesn't work on Mac
	@find . -maxdepth 3 -iname '*.py[co]' -o -iname '*.jy[co]' | xargs rm -f || :

.PHONY: deep-clean
deep-clean: clean
	$(SUDO) rm -fr /root/.cache ~/.cache 2>/dev/null

.PHONY: push
push:
	git push

# For quick testing only - for actual Dockerfile builds see https://hub.docker.com/r/harisekhon/alpine-github
.PHONY: docker-alpine
docker-alpine:
	bash-tools/docker_mount_build_exec.sh alpine

# For quick testing only - for actual Dockerfile builds see https://hub.docker.com/r/harisekhon/debian-github
.PHONY: docker-debian
docker-debian:
	bash-tools/docker_mount_build_exec.sh debian

# For quick testing only - for actual Dockerfile builds see https://hub.docker.com/r/harisekhon/centos-github
.PHONY: docker-centos
docker-centos:
	bash-tools/docker_mount_build_exec.sh centos

# For quick testing only - for actual Dockerfile builds see https://hub.docker.com/r/harisekhon/ubuntu-github
.PHONY: docker-ubuntu
docker-ubuntu:
	bash-tools/docker_mount_build_exec.sh ubuntu
