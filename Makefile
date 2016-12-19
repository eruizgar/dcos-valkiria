all: env test packages

change-version:
	bin/change-version.sh $(version)

clean:
	bin/clean.sh

env:
	bin/env.sh

compile:
	bin/compile.sh

test:
	bin/env.sh
	mkdir -p surefire-reports
	mkdir -p coverage-reports
	./env/bin/nosetests --with-xunit --xunit-file=surefire-reports/nosetests.xml --with-coverage --cover-erase --cover-package=dcos_valkiria tests/unit
	./env/bin/coverage xml -i -o coverage-reports/ut-coverage.xml
	mv .coverage coverage.ut

integration-test:
	bin/env.sh
	mkdir -p failsafe-reports
	mkdir -p coverage-reports
	./env/bin/nosetests --with-xunit --xunit-file=failsafe-reports/nosetests.xml --with-coverage --cover-erase --cover-package=dcos_valkiria tests/integration
	./env/bin/coverage xml -i -o coverage-reports/it-coverage.xml
	mv .coverage coverage.it

package:
	bin/env.sh
	bin/packages.sh

binary: clean env packages
	pyinstaller binary/binary.spec

deploy:
	bin/deploy.sh

code-quality:
	bin/env.sh
	bin/code-quality.sh
