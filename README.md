Hari Sekhon Python / Jython Library
===================================
[![Build Status](https://travis-ci.org/HariSekhon/pylib.svg?branch=master)](https://travis-ci.org/HariSekhon/pylib)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cfc553fcdbc94491b3c8c56797dcd189)](https://www.codacy.com/app/harisekhon/pylib)
[![Coverage Status](https://coveralls.io/repos/HariSekhon/pylib/badge.svg?branch=master&service=github)](https://coveralls.io/github/HariSekhon/pylib?branch=master)
[![PyUp](https://pyup.io/repos/github/HariSekhon/pylib/shield.svg)](https://pyup.io/account/repos/github/HariSekhon/pylib/)
[![Python 3](https://pyup.io/repos/github/HariSekhon/pylib/python-3-shield.svg)](https://pyup.io/repos/github/HariSekhon/pylib/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20OS%20X-blue.svg)](https://github.com/harisekhon/pylib#hari-sekhon-python--jython-library)
[![DockerHub](https://img.shields.io/badge/docker-available-blue.svg)](https://hub.docker.com/r/harisekhon/centos-github/)

My personal Python library, full of lots of validation code and utility functions.

Only supports Python 2 for now.

#### Build + Unit Tests ####

```
make &&
make test
```

[Continuous Integration](https://travis-ci.org/HariSekhon/pylib) is run on this repo to build and test it (around 450 unit tests, plus custom tests).

#### Configuration ####

Strict validations include host/domain/FQDNs using TLDs which are populated from the official IANA list, a snapshot of which is shipped as part of this project.

To update the bundled official IANA TLD list with the latest valid TLDs do
```
make tld
```
##### Custom TLDs #####

If using bespoke internal domains such as `.local`, `.intranet`, `.vm`, `.cloud` etc. that aren't part of the official IANA TLD list then this is additionally supported via a custom configuration file ```resources/custom_tlds.txt``` containing one TLD per line, with support for # comment prefixes. Just add your bespoke internal TLD to the file and it will then pass the host/domain/fqdn validations.

#### See Also ####

* [Java version of this library](https://github.com/harisekhon/lib-java)
* [Perl version of this library](https://github.com/harisekhon/lib)

Repos using this library:

* [Advanced Nagios Plugins Collection](https://github.com/harisekhon/nagios-plugins) - 400+ programs - the largest repo of monitoring code for Hadoop & NoSQL technologies, every Hadoop vendor's management API and every major NoSQL technology (HBase, Cassandra, MongoDB, Elasticsearch, Solr, Riak, Redis etc.) as well as traditional Linux and infrastructure
* [DevOps Python Tools](https://github.com/harisekhon/devops-python-tools) - 75+ programs - Hadoop, Spark (PySpark), Pig => Solr / Elasticsearch indexers, Pig Jython UDFs, Ambari Blueprints, AWS CloudFormation templates, HBase, Linux, IPython Notebook, Data converters between different data formats and syntactic validators for Avro, Parquet, CSV, JSON, YAML...

See also:

* [DevOps Perl Tools](https://github.com/harisekhon/devops-perl-tools) - 25+ programs for Hadoop, NoSQL, Solr, Elasticsearch, Pig, Hive, Web URL + Nginx stats watchers, SQL and NoSQL syntax recasers, various Linux CLI tools
