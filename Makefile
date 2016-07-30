#
#  Author: Hari Sekhon
#  Date: 2013-01-06 15:45:00 +0000 (Sun, 06 Jan 2013)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying LICENSE file
#

ifdef TRAVIS
	SUDO2 =
else
	SUDO2 = sudo -H
endif

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
	if [ -x /usr/bin/apt-get ]; then make apt-packages; fi
	if [ -x /usr/bin/yum ];     then make yum-packages; fi
	
	git submodule init
	git submodule update --recursive
	
	git update-index --assume-unchanged resources/custom_tlds.txt
	
	#$(SUDO2) pip install mock
	# upgrade required to get install to work properly on Debian
	$(SUDO2) pip install --upgrade pip
	$(SUDO2) pip install -r requirements.txt
	# prevents https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
	# gets setuptools error, but works the second time, doesn't seem to prevent things from working
	$(SUDO2) pip install --upgrade ndg-httpsclient || :
	# Python 2.4 - 2.6 backports
	#$(SUDO2) pip install argparse
	#$(SUDO2) pip install unittest2
	# json module built-in to Python >= 2.6, backport not available via pypi
	#$(SUDO2) pip install json
	
	#yum install -y perl-DBD-MySQL
	# MySQL-python doesn't support Python 3 yet, breaks in Travis with "ImportError: No module named ConfigParser"
	#$(SUDO2) pip install MySQL-python || :
	@echo
	bash-tools/python_compile.sh
	@echo
	@echo 'BUILD SUCCESSFUL (pylib)'

.PHONY: apk-packages
apk-packages:
	$(SUDO) apk update
	$(SUDO) apk add alpine-sdk
	$(SUDO) apk add bash
	$(SUDO) apk add cyrus-sasl-dev
	$(SUDO) apk add gcc
	$(SUDO) apk add git
	$(SUDO) apk add krb5-dev
	$(SUDO) apk add libffi-dev
	$(SUDO) apk add linux-headers
	$(SUDO) apk add make
	$(SUDO) apk add openssl-dev
	$(SUDO) apk add py-pip
	$(SUDO) apk add python
	$(SUDO) apk add python-dev
	$(SUDO) apk add snappy-dev
	$(SUDO) apk add wget
	$(SUDO) apk add zip
	# Spark Java Py4J gets java linking error without this
	if [ -f /lib/libc.musl-x86_64.so.1 ]; then [ -e /lib/ld-linux-x86-64.so.2 ] || ln -sv /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2; fi

.PHONY: apk-packages-remove
apk-packages-remove:
	$(SUDO) apk del alpine-sdk
	$(SUDO) apk del bash
	$(SUDO) apk del cyrus-sasl-dev
	$(SUDO) apk del gcc
	$(SUDO) apk del krb5-dev
	$(SUDO) apk del libffi-dev
	$(SUDO) apk del linux-headers
	$(SUDO) apk del openssl-dev
	$(SUDO) apk del py-pip
	$(SUDO) apk del python-dev
	$(SUDO) apk del snappy-dev
	$(SUDO) apk del wget
	$(SUDO) apk del zip

.PHONY: apt-packages
apt-packages:
	$(SUDO) apt-get update
	$(SUDO) apt-get install -y build-essential
	$(SUDO) apt-get install -y git
	$(SUDO) apt-get install -y python-dev
	$(SUDO) apt-get install -y python-setuptools
	$(SUDO) apt-get install -y python-pip
	# IPython Notebook fails and leave apt broken
	# The following packages have unmet dependencies:
	#  python-zmq : Depends: libzmq1 but it is not going to be installed
	#  E: Unmet dependencies. Try 'apt-get -f install' with no packages (or specify a solution).
	#$(SUDO) apt-get install -y ipython-notebook || :
	# for mysql_config to build MySQL-python
	#$(SUDO) apt-get install -y libmysqlclient-dev || :
	# needed for ndg-httpsclient upgrade
	$(SUDO) apt-get install -y libffi-dev

.PHONY: apt-packages-remove
apt-packages-remove:
	$(SUDO) apt-get purge -y build-essential
	$(SUDO) apt-get purge -y python-dev
	$(SUDO) apt-get purge -y python-setuptools
	$(SUDO) apt-get purge -y python-pip
	$(SUDO) apt-get purge -y libffi-dev

.PHONY: yum-packages
yum-packages:
	rpm -q git || $(SUDO) yum install -y git
	rpm -q wget || $(SUDO) yum install -y wget
	rpm -q gcc  || $(SUDO) yum install -y gcc
	# needed to fetch the library submodule and CPAN modules
	# python-pip requires EPEL, so try to get the correct EPEL rpm
	rpm -q epel-release || yum install -y epel-release || { wget -t 100 --retry-connrefused -O /tmp/epel.rpm "https://dl.fedoraproject.org/pub/epel/epel-release-latest-`grep -o '[[:digit:]]' /etc/*release | head -n1`.noarch.rpm" && $(SUDO) rpm -ivh /tmp/epel.rpm && rm -f /tmp/epel.rpm; }
	# for mysql_config to build MySQL-python
	rpm -q mysql-devel || $(SUDO) yum install -y mysql-devel
	rpm -q python-setuptools || $(SUDO) yum install -y python-setuptools
	rpm -q python-pip        || $(SUDO) yum install -y python-pip
	rpm -q python-devel      || $(SUDO) yum install -y python-devel
	#rpm -q ipython-notebook || $(SUDO) yum install -y ipython-notebook || :
	# needed for ndg-httpsclient upgrade
	rpm -q libffi-devel      || $(SUDO) yum install -y libffi-devel

.PHONY: yum-packages-remove
yum-packages-remove:
	rpm -q wget && $(SUDO) yum remove -y wget
	rpm -q gcc  && $(SUDO) yum remove -y gcc
	rpm -q mysql-devel && $(SUDO) yum remove -y mysql-devel
	rpm -q python-setuptools && $(SUDO) yum remove -y python-setuptools
	rpm -q python-pip        && $(SUDO) yum remove -y python-pip
	rpm -q python-devel      && $(SUDO) yum remove -y python-devel
	#rpm -q ipython-notebook && $(SUDO) yum remove -y ipython-notebook || :
	rpm -q libffi-devel      && $(SUDO) yum remove -y libffi-devel

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
