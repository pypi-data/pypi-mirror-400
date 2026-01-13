ENV_PATH = '/home/solcatcher/.env'
CRED_VALUES = {
    "postgres":{
        "prefix":'SOLCATCHER_POSTGRESQL',"defaults":{
        "host":'localhost',
        "port":'1234',
        "user":'solcatcher',
        "name":'solcatcher',
        "password":'solcatcher'
    }
        },
    "amqp":{
        "prefix":'SOLCATCHER_AMQP',
        "defaults":{
            "host":'localhost',
            "port":'1234',
            "user":'solcatcher',
            "name":'solcatcher',
            "pass":'solcatcher'
            }
        }
    }
