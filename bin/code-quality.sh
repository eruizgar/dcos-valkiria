#!/bin/bash -e

BASEDIR=`dirname $0`/..

cd $BASEDIR

PATH=$(pwd)/dist:$PATH

# Generate combined xml
$BASEDIR/env/bin/coverage combine coverage.ut coverage.it
$BASEDIR/env/bin/coverage xml -o coverage-reports/overall-coverage.xml
mv .coverage coverage.overall

# Generate pylint report
$BASEDIR/env/bin/pylint dcos_valkiria -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > pylint-report.txt || exit 0
