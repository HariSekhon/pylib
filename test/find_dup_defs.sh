#!/usr/bin/env bash
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-11-07 17:47:21 +0000 (Sat, 07 Nov 2015)
#
#  https://github.com/harisekhon
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon/pylib
#

set -euo pipefail
srcdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$srcdir/.."

# sed + and \+ don't work on Mac, must use *
# .*? also doesn't work, must use .*
#dups="$(grep -hR '^[^#]*def ' test/ | sed 's/^[[:space:]]*def[[:space:]]*//; s/(.*$//;' | sort | uniq -d)"
dups="$(grep '^[^#]*def ' test/*.py | sed 's/^[[:space:]]*def[[:space:]]*//; s/(.*$//;' | sort | uniq -d)"

if [ -n "$dups" ]; then
    echo "WARNING: duplicate defs found (may be masking other tests via overriding):"
    echo
    echo "$dups"
    echo
    exit 1
else
    echo "no duplicate defs found"
    exit 0
fi
