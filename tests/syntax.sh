#!/usr/bin/env bash
# shellcheck disable=SC2230
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-05-25 01:38:24 +0100 (Mon, 25 May 2015)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon
#

set -eu
srcdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$srcdir/..";

# shellcheck disable=SC1091
. ./tests/utils.sh

section "Python Syntax Checks"

start_time="$(start_timer)"

for x in $(echo ./*.py ./*.jy 2>/dev/null); do
    isExcluded "$x" && continue
    if which flake8 &> /dev/null; then
        echo "flake8 $x"
        flake8 --max-line-length=120 --statistics "$x"
        echo; hr; echo
    fi
    for y in pyflakes pychecker; do
        if which "$y" &>/dev/null; then
            echo "$y $x"
            "$y" "$x"
            echo; hr; echo
        fi
   done
done

time_taken "$start_time"
section2 "Python Syntax Checks Passed"
