#!/usr/bin/env bash
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-11-05 23:29:15 +0000 (Thu, 05 Nov 2015)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

set -euo pipefail
[ -n "${DEBUG:-}" ] && set -x
srcdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export PROJECT=pylib

cd "$srcdir/..";

# shellcheck disable=SC1091
. bash-tools/lib/utils.sh

section "PyLib Tests ALL"

pylib_start_time="$(start_timer)"

tests/find_dup_defs.sh

#./help.sh

bash-tools/checks/check_all.sh

bash-tools/checks/run_tests.sh

time_taken "$pylib_start_time" "PyLib Tests Completed in"
section2 "PyLib Tests Successful"
