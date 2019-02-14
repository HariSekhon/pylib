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
#   apk add --no-cache git $(MAKE) && git clone https://github.com/harisekhon/pylib && cd pylib && $(MAKE)

# Debian / Ubuntu:
#
#   apt-get update && apt-get install -y $(MAKE) git && git clone https://github.com/harisekhon/pylib && cd pylib && $(MAKE)

# RHEL / CentOS:
#
#   yum install -y $(MAKE) git && git clone https://github.com/harisekhon/pylib && cd pylib && $(MAKE)

# ===================

.PHONY: build
build:
	@echo ================
	@echo Python Lib Build
	@echo ================

	make system-packages

	python -V

	which pip || $(SUDO) easy_install pip || :

	pip -V

	git submodule init
	git submodule update --recursive
	
	git update-index --assume-unchanged resources/custom_tlds.txt
	
	#$(SUDO_PIP) pip install mock
	# upgrade required to get install to work properly on Debian
	#$(SUDO_PIP) pip install --upgrade pip

	# only install pip packages not installed via system packages
	#$(SUDO_PIP) pip install --upgrade -r requirements.txt
	for pip_module in `sed 's/#.*//; s/[>=].*//; s/-/_/g; /^[[:space:]]*$$/d' requirements.txt`; do \
		python -c "import $$pip_module" || $(SUDO_PIP) pip install "$$pip_module" || exit 1; \
	done

	# prevents https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
	# gets setuptools error, but works the second time, doesn't seem to prevent things from working
	# XXX: Breaks alpine docker builds since it pulls in cryptography which fails to find cffi
	# Collecting cryptography>=2.3 (from PyOpenSSL->ndg-httpsclient)
	#   Could not find a version that satisfies the requirement cffi!=1.11.3,>=1.8 (from versions: )
	#$(SUDO_PIP) pip install --upgrade ndg-httpsclient || $(SUDO_PIP) pip install --upgrade ndg-httpsclient

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
	$(SUDO) apk update
	$(SUDO) apk add `sed 's/#.*//; /^[[:space:]]*$$/d' setup/apk-packages.txt setup/apk-packages-dev.txt`
	for package in `sed 's/#.*//; /^[[:space:]]*$$/d' setup/apk-packages-pip.txt`; do $(SUDO) apk add "$$package" || : ; done
	# Spark Java Py4J gets java linking error without this
	if [ -f /lib/libc.musl-x86_64.so.1 ]; then [ -e /lib/ld-linux-x86-64.so.2 ] || ln -sv /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2; fi

.PHONY: apk-packages-remove
apk-packages-remove:
	$(SUDO) apk del `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/apk-packages-dev.txt` || :
	$(SUDO) rm -fr /var/cache/apk/*

.PHONY: apt-packages
apt-packages:
	$(SUDO) apt-get update
	$(SUDO) apt-get install -y `sed 's/#.*//; /^[[:space:]]*$$/d' setup/deb-packages.txt setup/deb-packages-dev.txt`
	for package in `sed 's/#.*//; /^[[:space:]]*$$/d' setup/deb-packages-pip.txt`; do $(SUDO) apt-get install -y "$$package" || : ; done

.PHONY: apt-packages-remove
apt-packages-remove:
	$(SUDO) apt-get purge -y `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/deb-packages-dev.txt`

.PHONY: yum-packages
yum-packages:
	# needed to fetch the library submodule and CPAN modules
	rpm -q git  || $(SUDO) yum install -y git
	rpm -q wget || $(SUDO) yum install -y wget
	# python-pip requires EPEL, so try to get the correct EPEL rpm
	rpm -q epel-release || yum install -y epel-release || { wget -t 100 --retry-connrefused -O /tmp/epel.rpm "https://dl.fedoraproject.org/pub/epel/epel-release-latest-`grep -o '[[:digit:]]' /etc/*release | head -n1`.noarch.rpm" && $(SUDO) rpm -ivh /tmp/epel.rpm && rm -f /tmp/epel.rpm; }

	for x in `sed 's/#.*//; /^[[:space:]]*$$/d' setup/rpm-packages.txt setup/rpm-packages-dev.txt`; do rpm -q $$x || $(SUDO) yum install -y $$x; done
	yum install -y `sed 's/#.*//; /^[[:space:]]*$$/d' setup/rpm-packages-pip.txt` || :

.PHONY: yum-packages-remove
yum-packages-remove:
	for x in `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/rpm-packages-dev.txt`; do rpm -q $$x && $(SUDO) yum remove -y $$x; done

.PHONY: sonar
sonar:
	sonar-scanner

.PHONY: test-common
test-common:
	tests/all.sh

.PHONY: test
test: test-common
	#python test/test_HariSekhonUtils.py
	# find all unit tests under test/
	# Python -m >= 2.7
	#python -m unittest discover -v
	#unit2 discover -v
	nosetests

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
