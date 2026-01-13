# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- File functional test
# :Created:   dom 08 apr 2018 13:57:32 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2019, 2021, 2022, 2023 Lele Gaifax
#

set -euo pipefail

THIS_SCRIPT=$(readlink -f $0)
TEST_DIR=$(dirname $THIS_SCRIPT)
TEST_NAME=$(basename $TEST_DIR)
WORK_DIR=${TMPDIR:-/tmp}/dbloady-test-$TEST_NAME
DATABASE_NAME=$WORK_DIR/db.sqlite

export PYTHONPATH=$TEST_DIR${PYTHONPATH:+:}${PYTHONPATH:-}

rm -rf $WORK_DIR
mkdir -p $WORK_DIR
cd $TEST_DIR

python test.py
