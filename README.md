Hari Sekhon Python / Jython Library
===================================
[![Build Status](https://travis-ci.org/HariSekhon/pylib.svg?branch=master)](https://travis-ci.org/HariSekhon/pylib)
[![Coverage Status](https://coveralls.io/repos/HariSekhon/pylib/badge.svg?branch=master&service=github)](https://coveralls.io/github/HariSekhon/pylib?branch=master)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20OS%20X-lightgrey.svg)
[![DockerHub](https://img.shields.io/badge/docker-available-blue.svg)](https://hub.docker.com/r/harisekhon/centos-github/)

My personal Python library, full of lots of validation code and utility functions.

Only supports Python 2 for now.

#### Build + Unit Tests ####

```
make &&
make test
```

Continuous Integration is run on this repo to build and unit test it.

#### Configuration ####

Strict validations include host/domain/FQDNs using TLDs which are populated from the official IANA list, a snapshot of which is shipped as part of this project.

To update the bundled official IANA TLD list with the latest valid TLDs do
```
make tld
```
##### Custom TLDs #####

If using bespoke internal domains such as ```.local``` or ```.intranet``` that aren't part of the official IANA TLD list then this is additionally supported via a custom configuration file ```resources/custom_tlds.txt``` containing one TLD per line, with support for # comment prefixes. Just add your bespoke internal TLD to the file and it will then pass the host/domain/fqdn validations.

#### See Also ####

* [Java version of this library](https://github.com/harisekhon/lib-java)
* [Perl version of this library](https://github.com/harisekhon/lib)

Repos using this library:

* [PyTools](https://github.com/harisekhon/pytools) - Hadoop, Spark, IPython, Pig => Solr / Elasticsearch, Pig Jython UDFs, Ambari, Linux
* [Advanced Nagios Plugins Collection](https://github.com/harisekhon/nagios-plugins) - 220+ programs - the largest repo of monitoring code for Hadoop & NoSQL technologies, every Hadoop vendor's management API and every major NoSQL technology (HBase, Cassandra, MongoDB, Elasticsearch, Solr, Riak, Redis etc.) as well as traditional Linux and infrastructure

See also:

* [Tools](https://github.com/harisekhon/tools) - Hadoop, NoSQL, Hive, Solr, Ambari, Web, Linux
