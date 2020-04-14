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

#python test/test_utils.py

# find all unit tests under test/
# Python -m >= 2.7
#python -m unittest discover -v

#unit2 discover -v

# more concise output but pip version problems between verions that support Python 2 and Python 3
#pytest

potential_nose_commands="
nose2
nose
nosetests
nosetests-3
nosetests-2
"

if is_CI; then
    echo "Available Python nose commands:"
    for cmd in $potential_nose_commands; do
        find / -type f -name "$cmd" 2>/dev/null || :
    done
fi

nose="$(bash-tools/python_find_library_executable.sh $potential_nose_commands)"
echo "running nose tests using: $nose"
echo
$nose
