#!/bin/bash -e

set -o errexit -o nounset -o pipefail

BASEDIR=`dirname $0`/..

rm -rf $BASEDIR/.tox $BASEDIR/env $BASEDIR/build $BASEDIR/dist
echo "Deleted virtualenv and test artifacts."

if [ -f pylint-report.txt ]; then
	rm pylint-report.txt
	echo "Deleted pylint report."
fi

if [ -d surefire-reports ]; then
        rm -Rf surefire-reports
        echo "Deleted surefire-reports (UT)."
fi

if [ -d failsafe-reports ]; then
	rm -Rf failsafe-reports
        echo "Deleted failsafe-reports."
fi

if [ -d coverage-reports ]; then
        rm -rf coverage-reports
        if [ -f .coverage ]; then
                rm .coverage
        fi
        if [ -f coverage.ut ]; then
                rm coverage.ut
        fi
        if [ -f coverage.it ]; then
                rm coverage.it
        fi
        if [ -f coverage.overall ]; then
                rm coverage.overall
        fi
        echo "Deleted coverage reports."
fi
