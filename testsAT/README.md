# README

## ACCEPTANCE TESTS

Cucumber automated and manual acceptance tests.
This module depends on a QA library (stratio-test-bdd), where common logic and steps are implemented.

## EXECUTION

These tests will be executed as part of the continuous integration flow as follows:

mvn verify [-D\<ENV_VAR>=\<VALUE>] [-Dit.test=\<TEST_TO_EXECUTE>|-Dgroups=\<GROUP_TO_EXECUTE>]

Example:

mvn verify -DDCOS_CLUSTER=10.200.0.182 -DDCOS_CLUSTER_PORT=80 -DDCOS_CLI_HOST=dcos-cli.demo.stratio.com -DUNIVERSE_URL=http://172.19.1.158/universe.zip -DNODES_USER=root -DNODES_PASSWORD=stratio -Dit.test=com.stratio.paas.testsAT.automated.dcosCommand.DCOSCommand

By default, in jenkins we will execute the group basic, which should contain a subset of tests, that are key to the functioning of the module and the ones generated for the new feature.

All tests, that are not fully implemented, should belong to the group manual and be tagged with '@ignore @manual'

