# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- HSTORE functional test
# :Created:   gio 22 ott 2015 18:15:12 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016, 2017, 2019, 2021, 2022, 2023, 2024 Lele Gaifax
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
psql -c "CREATE EXTENSION hstore" $DATABASE_NAME
python model.py setup $SA_URI
rm -f $WORK_DIR/state.yaml
dbloady -u $SA_URI -s $WORK_DIR/state.yaml data.yaml
python model.py test_1 $SA_URI
dbloady -u $SA_URI -D $WORK_DIR/state.yaml
python model.py test_2 $SA_URI
