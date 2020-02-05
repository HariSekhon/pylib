Hari Sekhon Python / Jython Library
===================================
[![Build Status](https://travis-ci.org/HariSekhon/pylib.svg?branch=master)](https://travis-ci.org/HariSekhon/pylib)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cfc553fcdbc94491b3c8c56797dcd189)](https://www.codacy.com/app/harisekhon/pylib)
[![GitHub stars](https://img.shields.io/github/stars/harisekhon/pylib.svg)](https://github.com/harisekhon/pylib/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/harisekhon/pylib.svg)](https://github.com/harisekhon/pylib/network)
[![Coverage Status](https://coveralls.io/repos/HariSekhon/pylib/badge.svg?branch=master&service=github)](https://coveralls.io/github/HariSekhon/pylib?branch=master)
[![PyUp](https://pyup.io/repos/github/HariSekhon/pylib/shield.svg)](https://pyup.io/account/repos/github/HariSekhon/pylib/)
[![Python 3](https://pyup.io/repos/github/HariSekhon/pylib/python-3-shield.svg)](https://pyup.io/repos/github/HariSekhon/pylib/)

[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20OS%20X-blue.svg)](https://github.com/harisekhon/pylib#hari-sekhon-python--jython-library)
[![DockerHub](https://img.shields.io/badge/docker-available-blue.svg)](https://hub.docker.com/r/harisekhon/centos-github/)

[![CI Mac](https://github.com/HariSekhon/pylib/workflows/CI%20Mac/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+Mac%22)
[![CI Ubuntu](https://github.com/HariSekhon/pylib/workflows/CI%20Ubuntu/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+Ubuntu%22)
[![CI CentOS](https://github.com/HariSekhon/pylib/workflows/CI%20CentOS/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+CentOS%22)
[![CI Alpine](https://github.com/HariSekhon/pylib/workflows/CI%20Alpine/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+Alpine%22)
[![CI Python 2.7](https://github.com/HariSekhon/pylib/workflows/CI%20Python%202.7/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+Python+2.7%22)
[![CI Python 3.6](https://github.com/HariSekhon/pylib/workflows/CI%20Python%203.6/badge.svg)](https://github.com/HariSekhon/pylib/actions?query=workflow%3A%22CI+Python+3.6%22)

My personal Python library, full of lots of validation code and utility functions.

Only supports Python 2 for now.

Hari Sekhon

Cloud & Big Data Contractor, United Kingdom

[https://www.linkedin.com/in/harisekhon](https://www.linkedin.com/in/harisekhon)
###### (you're welcome to connect with me on LinkedIn)

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

* [DevOps Python Tools](https://github.com/harisekhon/devops-python-tools) - 80+ DevOps CLI tools for AWS, Hadoop, HBase, Spark, Log Anonymizer, Ambari Blueprints, AWS CloudFormation, Linux, Docker, Spark Data Converters & Validators (Avro / Parquet / JSON / CSV / INI / XML / YAML), Elasticsearch, Solr, Travis CI, Pig, IPython

* [The Advanced Nagios Plugins Collection](https://github.com/harisekhon/nagios-plugins) - 450+ programs for Nagios monitoring your Hadoop & NoSQL clusters. Covers every Hadoop vendor's management API and every major NoSQL technology (HBase, Cassandra, MongoDB, Elasticsearch, Solr, Riak, Redis etc.) as well as message queues (Kafka, RabbitMQ), continuous integration (Jenkins, Travis CI) and traditional infrastructure (SSL, Whois, DNS, Linux)

* [DevOps Bash Tools](https://github.com/harisekhon/devops-bash-tools) - 100+ DevOps Bash scripts, advanced `.bashrc`, `.vimrc`, `.screenrc`, `.tmux.conf`, `.toprc`, Utility Code Library used by CI and all my GitHub repos - includes code for AWS, Kubernetes, Kafka, Docker, Git, Code & build linting, package management for Linux / Mac / Perl / Python / Ruby / Golang, and lots more random goodies

* [DevOps Perl Tools](https://github.com/harisekhon/perl-tools) - 25+ DevOps CLI tools for Hadoop, HDFS, Hive, Solr/SolrCloud CLI, Log Anonymizer, Nginx stats & HTTP(S) URL watchers for load balanced web farms, Dockerfiles & SQL ReCaser (MySQL, PostgreSQL, AWS Redshift, Snowflake, Apache Drill, Hive, Impala, Cassandra CQL, Microsoft SQL Server, Oracle, Couchbase N1QL, Dockerfiles, Pig Latin, Neo4j, InfluxDB), Ambari FreeIPA Kerberos, Datameer, Linux...

* [HAProxy-configs](https://github.com/harisekhon/haproxy-configs) - 80+ HAProxy Configs for Hadoop, Big Data, NoSQL, Docker, Elasticsearch, SolrCloud, HBase, Cloudera, Hortonworks, MapR, MySQL, PostgreSQL, Apache Drill, Hive, Presto, Impala, ZooKeeper, OpenTSDB, InfluxDB, Prometheus, Kibana, Graphite, SSH, RabbitMQ, Redis, Riak, Rancher etc.

* [Dockerfiles](https://github.com/HariSekhon/Dockerfiles) - 50+ DockerHub public images for Docker & Kubernetes - Hadoop, Kafka, ZooKeeper, HBase, Cassandra, Solr, SolrCloud, Presto, Apache Drill, Nifi, Spark, Mesos, Consul, Riak, OpenTSDB, Jython, Advanced Nagios Plugins & DevOps Tools repos on Alpine, CentOS, Debian, Fedora, Ubuntu, Superset, H2O, Serf, Alluxio / Tachyon, FakeS3
