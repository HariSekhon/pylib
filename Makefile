#
#  Author: Hari Sekhon
#  Date: 2013-01-06 15:45:00 +0000 (Sun, 06 Jan 2013)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying LICENSE file
#
#  https://www.linkedin.com/in/harisekhon
#

# Travis has custom python install earlier in $PATH even in Perl builds so need to install PyPI modules to non-system python otherwise they're not found by programs.
# Better than modifying $PATH to put /usr/bin first which is likely to affect many other things including potentially not finding the perlbrew installation first
#ifneq '$(VIRTUAL_ENV)$(CONDA_DEFAULT_ENV)$(TRAVIS)' ''
# Looks like Perl travis builds are now using system Python
ifndef VIRTUAL_ENV
	VIRTUAL_ENV = ''
endif
ifndef CONDA_DEFAULT_ENV
	CONDA_DEFAULT_ENV = ''
endif
ifneq '$(VIRTUAL_ENV)$(CONDA_DEFAULT_ENV)' ''
	SUDO2 =
else
	SUDO2 = sudo -H
endif

# must come after to reset SUDO2 to blank if root
# EUID /  UID not exported in Make
# USER not populated in Docker
ifeq '$(shell id -u)' '0'
	SUDO =
	SUDO2 =
else
	SUDO = sudo -H
endif

.PHONY: build
build:
	if [ -x /sbin/apk ];        then make apk-packages; fi
	if [ -x /usr/bin/apt-get -a "$$CI_NAME" != "codeship" ]; then make apt-packages; fi
	if [ -x /usr/bin/yum ];     then make yum-packages; fi
	
	git submodule init
	git submodule update --recursive
	
	git update-index --assume-unchanged resources/custom_tlds.txt
	
	#$(SUDO2) pip install mock
	# upgrade required to get install to work properly on Debian
	$(SUDO2) pip install --upgrade pip
	$(SUDO2) pip install --upgrade -r requirements.txt
	# prevents https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
	# gets setuptools error, but works the second time, doesn't seem to prevent things from working
	$(SUDO2) pip install --upgrade ndg-httpsclient || $(SUDO2) pip install --upgrade ndg-httpsclient
	# Python 2.4 - 2.6 backports
	#$(SUDO2) pip install argparse
	#$(SUDO2) pip install unittest2
	# json module built-in to Python >= 2.6, backport not available via pypi
	#$(SUDO2) pip install json
	
	#yum install -y perl-DBD-MySQL
	# MySQL-python doesn't support Python 3 yet, breaks in Travis with "ImportError: No module named ConfigParser"
	#$(SUDO2) pip install MySQL-python || :

	# PyLint breaks in Python 2.6
	#if [ "$$(python -c 'import sys; sys.path.append("pylib"); import harisekhon; print(harisekhon.utils.getPythonVersion())')" = "2.6" ]; then $(SUDO2) pip uninstall -y pylint; fi

	@echo
	bash-tools/python_compile.sh
	@echo
	@echo 'BUILD SUCCESSFUL (pylib)'

.PHONY: quick
quick:
	QUICK=1 make

.PHONY: apk-packages
apk-packages:
	$(SUDO) apk update
	$(SUDO) apk add `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/apk-packages.txt`
	# Spark Java Py4J gets java linking error without this
	if [ -f /lib/libc.musl-x86_64.so.1 ]; then [ -e /lib/ld-linux-x86-64.so.2 ] || ln -sv /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2; fi

.PHONY: apk-packages-remove
apk-packages-remove:
	$(SUDO) apk del `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/apk-packages-dev.txt` || :
	$(SUDO) rm -fr /var/cache/apk/*

.PHONY: apt-packages
apt-packages:
	$(SUDO) apt-get update
	$(SUDO) apt-get install -y `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/deb-packages.txt`

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

	for x in `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/rpm-packages.txt`; do rpm -q $$x || $(SUDO) yum install -y $$x; done

.PHONY: yum-packages-remove
yum-packages-remove:
	for x in `sed 's/#.*//; /^[[:space:]]*$$/d' < setup/rpm-packages-dev.txt`; do rpm -q $$x && $(SUDO) yum remove -y $$x; done

.PHONY: sonar
sonar:
	sonar-scanner

.PHONY: test-common
test-common:
	test/find_dup_defs.sh
	tests/all.sh

.PHONY: test
test:
	#python test/test_HariSekhonUtils.py
	# find all unit tests under test/
	# Python -m >= 2.7
	#python -m unittest discover -v
	#unit2 discover -v
	nosetests
	make test-common

.PHONY: test2
test2:
	python -m unittest discover -v
	make test-common

.PHONY: install
install:
	@echo "No installation needed, just add '$(PWD)' to your \$$PATH"

.PHONY: update
update:
	git pull
	git submodule update --init --recursive
	make

.PHONY: update2
update2:
	make update-no-recompile

.PHONY: update-no-recompile
update-no-recompile:
	git pull
	git submodule update --init --recursive

.PHONY: update-submodules
update-submodules:
	git submodule update --init --remote
.PHONY: updatem
updatem:
	make update-submodules

.PHONY: tld
tld:
	wget -t 100 --retry-connrefused -O resources/tlds-alpha-by-domain.txt http://data.iana.org/TLD/tlds-alpha-by-domain.txt

.PHONY: clean
clean:
	@# the xargs option to ignore blank input doesn't work on Mac
	@find . -maxdepth 3 -iname '*.py[co]' -o -iname '*.jy[co]' | xargs rm -f || :

.PHONY: push
push:
	git push
