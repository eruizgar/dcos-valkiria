package com.stratio.paas.testsAT.specs;

import com.stratio.tests.utils.RemoteSSHConnection;
import cucumber.api.java.en.Given;

public class DCOSCliSpec extends BaseSpec {

    public DCOSCliSpec(Common spec) {
        this.commonspec = spec;
    }

    /*
     * Setup ssh connections to all nodes in dcos cluster
     *
     * @param user
     * @param password
     *
     */
    @Given("^I setup ssh connections to nodes using user '(.+?)' and password '(.+?)' from '(.+?)' in cluster '(.+?)'$")
    public void setupSSHConnections(String user, String password, String dcosCLINode, String clusterLeader) throws Exception {
        commonspec.getLogger().debug("Setup SSH connections with user " + user + " and password " + password);

        // Setup connection to dcos-cli system
        RemoteSSHConnection localConnection = new RemoteSSHConnection("root", "stratio", dcosCLINode, null);

        // Obtain dcos cluster nodes
        localConnection.runCommand("dcos node | awk '{print $1}' | grep -v HOSTNAME");
        String nodes = localConnection.getResult();
        commonspec.getLogger().debug("Nodes are: " + nodes);
        String[] nodesArray = nodes.split("\\r?\\n");

        // Install sshpass for non interactive rsync
        localConnection.runCommand("apt-get install -y sshpass");

	// Generate ssh key, if it does not exist
	localConnection.runCommand("mkdir /root/.ssh");
	localConnection.runCommand("echo 'n' | ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ''");

        String command = "sshpass -p '" + password + "' ssh-copy-id -i /root/.ssh/id_rsa.pub -o StrictHostKeyChecking=no " + user + "@" +
                clusterLeader + "";
	commonspec.getLogger().debug("Leader command: " + command);
        localConnection.runCommand(command);

        // Setup ssh in all cluster nodes
        RemoteSSHConnection connection;
        for (String node : nodesArray) {
            // rsync public key
            command = "sshpass -p '" + password + "' ssh-copy-id -i /root/.ssh/id_rsa.pub -o StrictHostKeyChecking=no " + user + "@" + node + "";
	    commonspec.getLogger().debug("Node " + node + " command: " + command);
            localConnection.runCommand(command);
        }

        // Close connection
        localConnection.closeConnection();
    }

    @Given("^I undo ssh connections to nodes using user '(.+?)' and password '(.+?)' from '(.+?)' in cluster '(.+?)'$")
    public void undoSSHConnections(String user, String password, String dcosCLINode, String clusterLeader) throws Exception {
        commonspec.getLogger().debug("Undo SSH connections with user " + user + " and password " + password);

        // Setup connection to dcos-cli system
        RemoteSSHConnection localConnection = new RemoteSSHConnection("root", "stratio", dcosCLINode, null);

        // Obtain dcos cluster nodes
        localConnection.runCommand("dcos node | awk '{print $1}' | grep -v HOSTNAME");
        String nodes = localConnection.getResult();
        commonspec.getLogger().debug("Nodes are: " + nodes);
        String[] nodesArray = nodes.split("\\r?\\n");

        // Obtain public key
        localConnection.runCommand("cat /root/.ssh/id_rsa.pub");
        String publicKey = localConnection.getResult();

        // Undo ssh in cluster leader
        String command;
        RemoteSSHConnection nodeConnection = new RemoteSSHConnection(user, password, clusterLeader, null);
        command = "grep –v '" + publicKey + "' /root/.ssh/authorized_keys >> /root/.ssh/tmpkeys";
        nodeConnection.runCommand(command);
        command = "mv /root/.ssh/tmpkeys /root/.ssh/authorized_keys";
        nodeConnection.runCommand(command);
        nodeConnection.closeConnection();

        // Setup ssh in all cluster nodes
        for (String node : nodesArray) {
            // open connection to node
            nodeConnection = new RemoteSSHConnection(user, password, node, null);

            // remove public key from authorized_keys
            command = "grep –v '" + publicKey + "' /root/.ssh/authorized_keys >> /root/.ssh/tmpkeys";
            nodeConnection.runCommand(command);
            command = "mv /root/.ssh/tmpkeys /root/.ssh/authorized_keys";
            nodeConnection.runCommand(command);

            // close connection to node
            nodeConnection.closeConnection();
        }

        // Remove sshpass
        localConnection.runCommand("apt-get purge -y sshpass");

        // Close connection
        localConnection.closeConnection();
    }

}
