#!/usr/bin/env bash
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-07-31 12:18:38 +0100 (Sun, 31 Jul 2016)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

set -euo pipefail
[ -n "${DEBUG:-}" ] && set -x
srcdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$srcdir/.."

# shellcheck disable=SC1091
. bash-tools/lib/utils.sh

section "Running PyLib Unit Tests"

# shellcheck disable=SC1091
. bash-tools/lib/python.sh

#python test/test_utils.py

# find all unit tests under test/
# Python -m >= 2.7
#python -m unittest discover -v

#unit2 discover -v

# more concise output but pip version problems between verions that support Python 2 and Python 3
#pytest

# in Semaphore CI /usr/bin/nosetests should come before /usr/local/bin/nose2 which will use Python 3.8 instead of /usr/bin/python -> python2.7
potential_nose_commands="
nose
nosetests
nose3
nose2
nosetests-3
nosetests-2
"

# causes timeouts on some builds (eg, Mac on GitHub Actions)
#if is_CI; then
#    echo "Available Python nose commands:"
#    for cmd in $potential_nose_commands; do
#        find / -type f -name "$cmd" 2>/dev/null || :
#    done
#fi

nose_commands="$(
    for nose in $potential_nose_commands; do
        # $python_major_version defined in bash-tools/lib/python.sh
        # shellcheck disable=SC2154
        if [[ "$nose" =~ [[:digit:]]$ ]] &&
           ! [[ "$nose" =~ $python_major_version$ ]]; then
            continue
        fi
        echo "$nose"
    done
)"

# want splitting
# shellcheck disable=SC2086
nose="$(bash-tools/python_find_library_executable.sh $nose_commands)"
echo
echo "Unsetting environment variables that may interfere with unit tests"
unset HOST
unset PORT
echo

# $python defined in bash-tools/lib/python.sh
# shellcheck disable=SC2154
echo "Running nose tests using: $python $nose"
echo
"$python" "$nose"
