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
	SUDO2 = sudo
endif

# EUID /  UID not exported in Make
# USER not populated in Docker
ifeq '$(shell id -u)' '0'
	SUDO =
	SUDO2 =
else
	SUDO = sudo
endif

.PHONY: build
build:
	if [ -x /usr/bin/apt-get ]; then make apt-packages; fi
	if [ -x /usr/bin/yum ];     then make yum-packages; fi
	
	git submodule init
	git submodule update --recursive

	git update-index --assume-unchanged resources/custom_tlds.txt
	
	#$(SUDO2) pip install mock
	$(SUDO2) pip install -r requirements.txt
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

.PHONY: yum-packages
yum-packages:
	rpm -q git || $(SUDO) yum install -y git
	rpm -q wget || $(SUDO) yum install -y wget
	rpm -q gcc  || $(SUDO) yum install -y gcc
	# needed to fetch the library submodule and CPAN modules
	# python-pip requires EPEL, so try to get the correct EPEL rpm
	rpm -q epel-release || yum install -y epel-release || { wget -O /tmp/epel.rpm "https://dl.fedoraproject.org/pub/epel/epel-release-latest-`grep -o '[[:digit:]]' /etc/*release | head -n1`.noarch.rpm" && $(SUDO) rpm -ivh /tmp/epel.rpm && rm -f /tmp/epel.rpm; }
	# for mysql_config to build MySQL-python
	rpm -q mysql-devel || $(SUDO) yum install -y mysql-devel
	rpm -q python-setuptools || $(SUDO) yum install -y python-setuptools
	rpm -q python-pip        || $(SUDO) yum install -y python-pip
	rpm -q python-devel      || $(SUDO) yum install -y python-devel
	#rpm -q ipython-notebook || $(SUDO) yum install -y ipython-notebook || :

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

.PHONY: tld
tld:
	wget -O resources/tlds-alpha-by-domain.txt http://data.iana.org/TLD/tlds-alpha-by-domain.txt

.PHONY: clean
clean:
	@# the xargs option to ignore blank input doesn't work on Mac
	@find . -maxdepth 3 -iname '*.py[co]' -o -iname '*.jy[co]' | xargs rm -f || :
