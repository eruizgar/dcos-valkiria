@Library('libpipelines@master') _

hose {
    EMAIL = 'qa'
    MODULE = 'dcos-valkiria'
    REPOSITORY = 'dcos-valkiria'
    SLACKTEAM = 'stratiopaas'
    BUILDTOOL = 'make'
    DEVTIMEOUT = 40

    ATSERVICES = [
            ['DCOSCLI':   ['image': 'stratio/dcos-cli:0.4.14',
                           'env':    ['DCOS_URL=http://10.200.1.221',
                                      'SSH=true',
                                      'TOKEN_AUTHENTICATION=true',
                                      'DCOS_USER=admin@demo.stratio.com',
                                      'DCOS_PASSWORD=stratiotest',
                                      'REMOTE_USER=root',
                                      'REMOTE_PASSWORD=stratio',
                                      'MASTER_MESOS=10.200.1.221',],
                           'sleep':  10]]
        ]

    ATPARAMETERS = """
                    | -DDCOS_CLI_HOST=%%DCOSCLI#0
                    | -DDCOS_CLUSTER=10.200.1.221
                    | -DDCOS_CLUSTER_PORT=80
                    | -DUNIVERSE_URL=http://sodio.stratio.com/nexus/content/sites/paas/universe/0.3.0-SNAPSHOT/stratio-paas-universe-0.3.0-SNAPSHOT.zip
                    | -DNODES_USER=root
                    | -DNODES_PASSWORD=stratio
                    | """

    DEV = { config ->        
        doUT(config)
        doIT(config)
        doPackage(config)
        parallel(QC: {
            doStaticAnalysis(config)
        }, DEPLOY: {
            doDeploy(config)
        }, failFast: config.FAILFAST)
     }

     AT = { config ->
        doAT(conf: config, groups: ['dcos-cli'])
     }
}
