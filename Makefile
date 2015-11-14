#
#  Author: Hari Sekhon
#  Date: 2013-01-06 15:45:00 +0000 (Sun, 06 Jan 2013)
#

# Library dependencies are handled in one place in calling project

ifdef TRAVIS
    SUDO2 =
else
    SUDO2 = sudo
endif

# EUID /  UID not exported in Make
ifeq '$(USER)' 'root'
    SUDO =
    SUDO2 =
else
    SUDO = sudo
endif

.PHONY: make
make:
	[ -x /usr/bin/apt-get ] && make apt-packages || :
	[ -x /usr/bin/yum ]     && make yum-packages || :

	git update-index --assume-unchanged resources/custom_tlds.txt

	#yum install -y perl-DBD-MySQL
	# this breaks in Python 3 in Travis with "ImportError: No module named ConfigParser"
	pip install MySQL-python

	# json module built-in to Python >= 2.6, backport not available via pypi
	#$(SUDO2) pip install json

	$(SUDO2) pip install coveralls
	$(SUDO2) pip install mock

.PHONY: apt-packages
apt-packages:
	$(SUDO) apt-get install -y gcc || :
	# needed to fetch the library submodule at end of build
	$(SUDO) apt-get install -y git || :
	$(SUDO) apt-get install -y ipython-notebook || :
	# for mysql_config to build MySQL-python
	$(SUDO) apt-get install -y libmysqlclient-dev || :
	dpkg -l python-setuptools python-dev &>/dev/null || $(SUDO) apt-get install -y python-setuptools python-dev || :

.PHONY: yum-packages
yum-packages:
	rpm -q gcc || $(SUDO) yum install -y gcc || :
	# needed to fetch the library submodule and CPAN modules
	# python-pip requires EPEL, so try to get the correct EPEL rpm - for Make must escape the $3
	rpm -ivh "https://dl.fedoraproject.org/pub/epel/epel-release-latest-`awk '{print substr($$3, 0, 1); exit}' /etc/*release`.noarch.rpm" || :
	# for mysql_config to build MySQL-python
	rpm -q mysql-devel || $(SUDO) yum install -y mysql-devel || :
	rpm -q python-setuptools python-pip python-devel || $(SUDO) yum install -y python-setuptools python-pip python-devel || :
	rpm -q ipython-notebook || $(SUDO) yum install -y ipython-notebook || :

.PHONY: test
test:
	#python -m unittest discover
	python test_HariSekhonUtils.py

.PHONY: install
install:
	@echo "No installation needed, just add '$(PWD)' to your \$$PATH"

.PHONY: update
update:
	git pull
	make

tld:
	wget -O resources/tlds-alpha-by-domain.txt http://data.iana.org/TLD/tlds-alpha-by-domain.txt
