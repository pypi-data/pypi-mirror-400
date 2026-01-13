# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Dump functional test
# :Created:   gio 10 mar 2016 18:43:53 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019, 2021, 2022, 2023 Lele Gaifax
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

python model.py setup $DATABASE_NAME
dbloady -u sqlite:///$DATABASE_NAME data.yaml
echo ".dump" | sqlite3 $DATABASE_NAME > $WORK_DIR/first.dump
dbdumpy -u sqlite:///$DATABASE_NAME spec.yaml $WORK_DIR/output.yaml

rm -f $DATABASE_NAME
python model.py setup $DATABASE_NAME
dbloady -u sqlite:///$DATABASE_NAME $WORK_DIR/output.yaml
echo ".dump" | sqlite3 $DATABASE_NAME > $WORK_DIR/second.dump

cmp $WORK_DIR/first.dump $WORK_DIR/second.dump
