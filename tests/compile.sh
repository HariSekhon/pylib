#!/usr/bin/env bash
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

. ./tests/utils.sh

section "Python Compile"

start_time="$(start_timer)"

for x in $(find . -type f -iname '*.py' -o -iname '*.jy'); do
    isExcluded "$x" && continue
    echo "compiling $x"
    python -m py_compile $x
done

time_taken "$start_time"
section2 "Completed Python Compile"
