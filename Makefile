#
#  Author: Hari Sekhon
#  Date: 2013-01-06 15:45:00 +0000 (Sun, 06 Jan 2013)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying LICENSE file
#
#  https://www.linkedin.com/in/harisekhon
#

# Travis has custom python install earlier in $PATH even in Perl builds so need to install PyPI modules to non-system python otherwise they're not found by programs.
# Better than modifying $PATH to put /usr/bin first which is likely to affect many other things including potentially not finding the perlbrew installation first
#ifneq '$(VIRTUAL_ENV)$(CONDA_DEFAULT_ENV)$(TRAVIS)' ''
# Looks like Perl travis builds are now using system Python - do not use TRAVIS env var

# ===================
# bootstrap commands:

# setup/bootstrap.sh
#
# OR
#
# Alpine:
#
#   apk add --no-cache git make && git clone https://github.com/harisekhon/pylib && cd pylib && make
#
# Debian / Ubuntu:
#
#   apt-get update && apt-get install -y make git && git clone https://github.com/harisekhon/pylib && cd pylib && make
#
# RHEL / CentOS:
#
#   yum install -y make git && git clone https://github.com/harisekhon/pylib && cd pylib && make

# ===================

# would fail bootstrapping on Alpine
#SHELL := /usr/bin/env bash

ifneq ("$(wildcard bash-tools/Makefile.in)", "")
	include bash-tools/Makefile.in
endif

REPO := HariSekhon/pylib

CODE_FILES := $(shell find . -type f -name '*.py' -o -type f -name '*.sh' | grep -v -e bash-tools)

.PHONY: build
build: init
	@echo ================
	@echo Python Lib Build
	@echo ================
	@$(MAKE) git-summary
	@echo

	@# executing in sh where type is not available
	@#type -P python
	which python && python -V || :
	which python2 && python2 -V || :
	which python3 && python3 -V || :
	which pip && pip -V || :
	which pip2 && pip2 -V || :
	which pip3 && pip3 -V || :

	@# doesn't work, only exits the line not the script and don't wanna use oneshell
	@#if [ -z "$(CPANM)" ]; then make; exit $$?; fi
	$(MAKE) system-packages-python

	bash-tools/setup/alternatives_set_python.sh

	git update-index --assume-unchanged resources/custom_tlds.txt

	# fixes bug in cffi version detection when installing requests-kerberos
	@#$(SUDO_PIP) pip install --quiet --upgrade pip || :
	PIP_OPTS="--quiet --upgrade" bash-tools/python_pip_install.sh pip || :

	# impyla needs newer setuptools than OS packaged with Python 2
	@#$(SUDO_PIP) pip install --quiet --upgrade setuptools || :
	PIP_OPTS="--quiet --upgrade" bash-tools/python_pip_install.sh setuptools || :

	# only install pip packages not installed via system packages
	#$(SUDO_PIP) pip install --quiet --upgrade -r requirements.txt
	#$(SUDO_PIP) pip install --quiet -r requirements.txt
	PIP_OPTS="--ignore-installed urllib3" bash-tools/python_pip_install_if_absent.sh requirements.txt

	# prevents https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
	@#$(SUDO_PIP) pip install --quiet --upgrade ndg-httpsclient || \
	@#$(SUDO_PIP) pip install --quiet --upgrade ndg-httpsclient
	PIP_OPTS="--quiet --upgrade" bash-tools/python_pip_install.sh ndg-httpsclient ||
	PIP_OPTS="--quiet --upgrade" bash-tools/python_pip_install.sh ndg-httpsclient

	# Python 2.4 - 2.6 backports
	#$(SUDO_PIP) pip install argparse
	#$(SUDO_PIP) pip install unittest2

	# PyLint breaks in Python 2.6
	#if [ "$$(python -c 'import sys; sys.path.append("pylib"); import harisekhon; print(harisekhon.utils.getPythonVersion())')" = "2.6" ]; then $(SUDO_PIP) pip uninstall -y pylint; fi

	# Spark Java Py4J gets java linking error without this
	if [ -f /lib/libc.musl-x86_64.so.1 ]; then [ -e /lib/ld-linux-x86-64.so.2 ] || ln -sv /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2; fi

	@echo
	bash-tools/python_compile.sh
	@echo
	@echo 'BUILD SUCCESSFUL (pylib)'
	@echo
	@echo

.PHONY: init
init:
	git submodule update --init --recursive

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
test: test-common unittest

.PHONY: unittest
unittest:
	tests/unittest.sh

.PHONY: test2
test2: test-common unittest2

.PHONY: install
install:
	@echo "No installation needed, just add '$(PWD)' to your \$$PATH"

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

.PHONY: coverage
coverage:
	@# doesn't catch a lot of tests, use nose instead
	@#coverage run --source=harisekhon -m test
	coverage run --source=harisekhon -m nose
	@#coverage run --source=harisekhon -m pytest
	coverage report

.PHONY: coveralls
coveralls: coverage
	coveralls
