# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- JSON functional test
# :Created:   mar 08 nov 2016 09:48:18 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019, 2021, 2022, 2023, 2024 Lele Gaifax
#

set -euo pipefail

THIS_SCRIPT=$(readlink -f $0)
TEST_DIR=$(dirname $THIS_SCRIPT)
TEST_NAME=$(basename $TEST_DIR)
WORK_DIR=${TMPDIR:-/tmp}/dbloady-test-$TEST_NAME

export PGHOST=localhost
export PGPORT=65432
export PGUSER=dbloady

export PYTHONPATH=$TEST_DIR${PYTHONPATH:+:}${PYTHONPATH:-}

DATABASE_NAME=dbloady-test-$TEST_NAME
SA_URI=postgresql+psycopg://localhost:$PGPORT/$DATABASE_NAME

rm -rf $WORK_DIR
mkdir -p $WORK_DIR
cd $TEST_DIR

../postgresql start
dropdb --if-exists $DATABASE_NAME
createdb $DATABASE_NAME
python model.py setup $SA_URI
dbloady -u $SA_URI data.yaml
python model.py test $SA_URI
