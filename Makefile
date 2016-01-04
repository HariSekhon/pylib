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

.PHONY: make
make:
	if [ -x /usr/bin/apt-get ]; then make apt-packages; fi
	if [ -x /usr/bin/yum ];     then make yum-packages; fi
	
	git update-index --assume-unchanged resources/custom_tlds.txt
	
	#$(SUDO2) pip install mock
	pip install -r requirements.txt
	# Python 2.4 - 2.6 backports
	#$(SUDO2) pip install argparse
	#$(SUDO2) pip install unittest2
	# json module built-in to Python >= 2.6, backport not available via pypi
	#$(SUDO2) pip install json
	
	#yum install -y perl-DBD-MySQL
	# MySQL-python doesn't support Python 3 yet, breaks in Travis with "ImportError: No module named ConfigParser"
	pip install MySQL-python || :
	
	@echo
	@echo PyLib BUILD SUCCESSFUL


.PHONY: apt-packages
apt-packages:
	$(SUDO) apt-get install -y gcc || :
	#$(SUDO) apt-get install -y ipython-notebook || :
	# for mysql_config to build MySQL-python
	$(SUDO) apt-get install -y libmysqlclient-dev || :
	dpkg -l python-setuptools python-dev &>/dev/null || $(SUDO) apt-get install -y python-setuptools python-dev || :


.PHONY: yum-packages
yum-packages:
	rpm -q gcc wget || $(SUDO) yum install -y gcc wget
	# needed to fetch the library submodule and CPAN modules
	# python-pip requires EPEL, so try to get the correct EPEL rpm - for Make must escape the $3
	rpm -q epel-release || rpm -ivh "https://dl.fedoraproject.org/pub/epel/epel-release-latest-`awk '{print substr($$3, 0, 1); exit}' /etc/*release`.noarch.rpm"
	# for mysql_config to build MySQL-python
	rpm -q mysql-devel || $(SUDO) yum install -y mysql-devel
	rpm -q python-setuptools python-pip python-devel || $(SUDO) yum install -y python-setuptools python-pip python-devel
	#rpm -q ipython-notebook || $(SUDO) yum install -y ipython-notebook || :


.PHONY: test
test:
	test/find_dup_defs.sh
	#python test/test_HariSekhonUtils.py
	# find all unit tests under test/
	# Python -m >= 2.7
	#python -m unittest discover -v
	#unit2 discover -v
	nosetests
	tests/all.sh

.PHONY: test2
test2:
	test/find_dup_defs.sh
	python -m unittest discover -v
	tests/all.sh

.PHONY: install
install:
	@echo "No installation needed, just add '$(PWD)' to your \$$PATH"


.PHONY: update
update:
	git pull
	make


tld:
	wget -O resources/tlds-alpha-by-domain.txt http://data.iana.org/TLD/tlds-alpha-by-domain.txt
