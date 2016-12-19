@rest
Feature: Test addition of command package to cli

  Background: Setup PaaS REST client
    Given I send requests to '${DCOS_CLUSTER}:${DCOS_CLUSTER_PORT}'

  Scenario: Add package repo
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos package repo add stratio ${UNIVERSE_URL}' in remote ssh connection
    Then the command exit status is '0'
    When I execute command 'dcos package repo list | grep stratio' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'stratio'

  Scenario: Install dcos command
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos package search valkiria' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'Administer and manage commands in DCOS cluster nodes.'
    When I execute command 'dcos package install --cli valkiria' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'New command available: dcos valkiria'

  Scenario: Test dcos valkiria --help
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos valkiria --help' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'Administer and manage commands in DCOS cluster nodes.'

  Scenario: Test dcos valkiria --info
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos valkiria --info' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'Administer and manage commands in DCOS cluster nodes.'

  Scenario: Test dcos valkiria --version
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos valkiria --version' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains 'dcos-valkiria version 0.1.0'

  Scenario: Test dcos valkiria ssh
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    # Setup ssh passwordless
    And I setup ssh connections to nodes using user '${NODES_USER}' and password '${NODES_PASSWORD}' from '${DCOS_CLI_HOST}' in cluster '${DCOS_CLUSTER}'
    # Node: dcos valkiria ssh --mesos-id=XXXXX 'ls -al'
    When I execute command 'dcos valkiria ssh --option StrictHostKeyChecking=no --user=root --mesos-id=$(dcos node | awk '{print $3}' | grep -v ID | head -1) "ls -al"' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains '.bashrc'
    # Leader: dcos valkiria ssh --leader 'ls -al'
    When I execute command 'dcos valkiria ssh --option StrictHostKeyChecking=no --user ${NODES_USER} --leader "ls -al"' in remote ssh connection
    Then the command exit status is '0'
    And the command output contains '.bashrc'
    # Master: dcos valkiria ssh --master 'ls -al'
    When I execute command 'dcos valkiria ssh --option StrictHostKeyChecking=no --user ${NODES_USER} --master "ls -al"' in remote ssh connection
    Then the command exit status is '1'
    # Slave: dcos valkiria ssh --slave=XXXXX 'ls -al'
    When I execute command 'dcos valkiria ssh --option StrictHostKeyChecking=no --user=root --slave=$(dcos node | awk '{print $3}' | grep -v ID | head -1) "ls -al"' in remote ssh connection
    Then the command exit status is '1'
    # Undo ssh passwordless
    And I undo ssh connections to nodes using user '${NODES_USER}' and password '${NODES_PASSWORD}' from '${DCOS_CLI_HOST}' in cluster '${DCOS_CLUSTER}'

  Scenario: Uninstall command package
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos package uninstall valkiria' in remote ssh connection
    Then the command exit status is '0'

  Scenario: Remove universe
    Given I open remote ssh connection to host '${DCOS_CLI_HOST}' with user 'root' and password 'stratio'
    When I execute command 'dcos package repo remove stratio' in remote ssh connection
    Then the command exit status is '0'
    When I execute command 'dcos package repo list | grep stratio' in remote ssh connection
    Then the command exit status is '1'
